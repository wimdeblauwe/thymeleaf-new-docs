#!/usr/bin/env python3
"""Convert the English Thymeleaf 3.1 Pandoc-Markdown sources into Starlight pages.

Python 3 standard library only. Deterministic: the same sources always produce
byte-identical output. See README.md in this folder.

Scope (Step 2 of the roadmap): mechanical conversion only. No prose is
rewritten and nothing is restructured into the new navigation.
"""

import argparse
import collections
import html
import json
import re
import shutil
import sys
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent.parent
DEFAULT_SOURCE = (PROJECT / ".." / "thymeleaf-docs").resolve()
DEFAULT_IMAGE_FALLBACK = (PROJECT / ".." / "thymeleaf.github.io" / "doc").resolve()

DOCS_ROOT = "docs"  # URL and content prefix: src/content/docs/docs/...
SITE_ORIGINAL = "https://www.thymeleaf.org"
LICENSE_URL = "https://creativecommons.org/licenses/by-sa/3.0/"
THYMELEAF_VERSION_KEY = "3.1"

TUTORIALS = [
    # source name, output directory, label used in descriptions
    ("usingthymeleaf", "using-thymeleaf"),
    ("thymeleafspring", "thymeleaf-spring"),
    ("extendingthymeleaf", "extending-thymeleaf"),
]
ARTICLES = [
    # source name -> readable slug
    ("layouts", "page-layouts"),
    ("springsecurity", "spring-security-basics"),
    ("springmvcaccessdata", "spring-mvc-access-data"),
    ("springmail", "sending-email-with-spring"),
    ("standardurlsyntax", "standard-url-syntax"),
    ("thvsjsp", "thymeleaf-vs-jsp"),
    ("fromhtmltohtmlviahtml", "from-html-to-html-via-html"),
    ("standarddialect5minutes", "standard-dialects-in-5-minutes"),
    ("sayhelloextendingthymeleaf5minutes", "say-hello-extending-thymeleaf"),
    ("sayhelloagainextendingthymeleafevenmore5minutes", "say-hello-again-extending-thymeleaf"),
]
TUTORIAL_DIR = dict(TUTORIALS)
ARTICLE_SLUG = dict(ARTICLES)

WORD_RE = re.compile(r"\w+", re.UNICODE)
FENCE_RE = re.compile(r"^(\s*)(`{3,}|~{3,})(.*)$")
BORDER_RE = re.compile(r"^-{3,}(?: +-{3,})*\s*$")
NUM_PREFIX_RE = re.compile(r"^(\d+(?:\.\d+)*)\.?\s+(?=\S)")


class Problems:
    """Collects warnings and errors so they can be shown in the report."""

    def __init__(self):
        self.warnings = []
        self.errors = []

    def warn(self, msg):
        self.warnings.append(msg)

    def error(self, msg):
        self.errors.append(msg)


PROBLEMS = Problems()


# ---------------------------------------------------------------- helpers

def words(text):
    """Multiset of word tokens, ignoring link/image destinations (rewritten on purpose)."""
    text = re.sub(r"\]\([^)\s]*\)", "]()", text)
    return collections.Counter(w for w in WORD_RE.findall(text))


def yaml_str(value):
    return json.dumps(value, ensure_ascii=False)


def split_frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not m:
        raise ValueError("no front matter")
    meta = {}
    for line in m.group(1).split("\n"):
        km = re.match(r"^(\w+):\s*(.*)$", line)
        if not km:
            continue
        v = km.group(2).strip()
        if v.startswith("'") and v.endswith("'") and len(v) >= 2:
            v = v[1:-1].replace("''", "'")
        meta[km.group(1)] = v
    return meta, text[m.end():]


def read_document_metadata(source):
    """Read version/date for 3.1 from build.gradle, as the Gradle build does."""
    gradle = (source / "build.gradle").read_text(encoding="utf8")
    m = re.search(
        r"'" + re.escape(THYMELEAF_VERSION_KEY) + r"':\s*\[\s*version:\s*'([^']+)',\s*date:\s*LocalDate\.of\((\d+),\s*(\d+),\s*(\d+)\)",
        gradle,
    )
    if not m:
        raise SystemExit("Could not find the 3.1 documentMetadata entry in build.gradle")
    version, y, mo, d = m.group(1), int(m.group(2)), int(m.group(3)), int(m.group(4))
    months = ["January", "February", "March", "April", "May", "June", "July",
              "August", "September", "October", "November", "December"]
    # Same pattern as the Gradle build: yyyyMMdd - dd MMMM yyyy
    document_version = f"{y:04d}{mo:02d}{d:02d} - {d:02d} {months[mo - 1]} {y:04d}"
    return version, document_version


def plain_inline(text):
    """Approximate the plain text of a Markdown inline string (for ids and descriptions)."""
    t = html.unescape(text)
    t = re.sub(r"!\[([^\]]*)\]\([^)]*\)", r"\1", t)
    t = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", t)
    t = t.replace("`", "")
    t = t.replace("*", "")
    t = re.sub(r"(?<!\w)_|_(?!\w)", "", t)
    return t


def pandoc_id(text):
    """Pandoc's default auto identifier (as used by the published HTML)."""
    t = plain_inline(text).lower()
    t = "".join(c for c in t if c.isalnum() or c in "_-." or c.isspace())
    t = "-".join(t.split())
    m = re.search(r"[^\W\d_]", t)  # drop everything before the first letter
    t = t[m.start():] if m else ""
    return t or "section"


def github_slug(text):
    """github-slugger, as used by Astro/Starlight for heading ids."""
    t = plain_inline(text).lower()
    out = []
    for c in t:
        cat = unicodedata.category(c)
        if c in "-_ " or cat[0] in "LMN" or cat == "Pc":
            out.append(c)
    return "".join(out).replace(" ", "-")


def slugify(text):
    t = unicodedata.normalize("NFKD", plain_inline(text)).replace("'", "").replace("\u2019", "")
    t = "".join(c for c in t if not unicodedata.combining(c)).lower()
    t = re.sub(r"[^a-z0-9]+", "-", t).strip("-")
    return t or "section"


class Dedup:
    """Assign unique ids, appending -1, -2 ... for repeats (Pandoc and github-slugger agree)."""

    def __init__(self):
        self.seen = set()

    def unique(self, base):
        cand, n = base, 0
        while cand in self.seen:
            n += 1
            cand = f"{base}-{n}"
        self.seen.add(cand)
        return cand


# ---------------------------------------------------------------- stage A

class Doc:
    def __init__(self, kind, name, meta, body):
        self.kind = kind          # "tutorial" | "article"
        self.name = name          # source base name, e.g. "usingthymeleaf"
        self.meta = meta
        self.body = body          # raw body text
        self.lines = []           # list of [text, in_code]
        self.headings = []        # dicts: line, level, raw, text
        self.removed = collections.Counter()   # tokens removed on purpose
        self.added = collections.Counter()     # tokens added on purpose
        self.cats = collections.Counter()      # removed token counts by reason
        self.tables = 0
        self.divs_removed = 0
        self.setext = 0
        self.raw_html_wrapped = []


def _remove(self, cat, text):
    w = words(text)
    self.removed.update(w)
    self.cats[cat] += sum(w.values())


Doc.remove = _remove


def mark_code(lines):
    """Return [(line, in_code)]. Fence lines count as code."""
    out, fence = [], None
    for l in lines:
        m = FENCE_RE.match(l)
        if fence is None:
            if m:
                fence = (m.group(2)[0], len(m.group(2)))
                out.append([l, True])
            else:
                out.append([l, False])
        else:
            out.append([l, True])
            if m and m.group(2)[0] == fence[0] and len(m.group(2)) >= fence[1] and not m.group(3).strip():
                fence = None
    return out


def split_cells(line, starts):
    cells = []
    for i, s in enumerate(starts):
        e = starts[i + 1] if i + 1 < len(starts) else len(line)
        cells.append(line[s:e].strip() if s < len(line) else "")
    return cells


def convert_table(block, doc):
    """Pandoc simple table lines -> list of GFM table lines."""
    lines = [l.rstrip() for l in block]
    # locate the column border line (has gaps)
    col_idx = next(i for i, l in enumerate(lines) if re.search(r"-\s+-", l))
    starts = [m.start() for m in re.finditer(r"-+", lines[col_idx])]
    header = None
    if col_idx == 0:
        rows_raw = lines[1:-1]            # headerless: col border ... col border
    else:
        # border, header line(s), col border, rows..., closing border
        header_lines = lines[1:col_idx]
        header = split_cells(header_lines[0], starts) if len(header_lines) == 1 else None
        if header is None:
            raise ValueError("multi-line table header not supported")
        rows_raw = lines[col_idx + 1:-1]
    # group rows: blank-line separated if blank lines present, else one line per row
    if any(not l.strip() for l in rows_raw):
        groups, cur = [], []
        for l in rows_raw:
            if l.strip():
                cur.append(l)
            elif cur:
                groups.append(cur)
                cur = []
        if cur:
            groups.append(cur)
    else:
        groups = [[l] for l in rows_raw]
    rows = []
    for g in groups:
        cols = [[] for _ in starts]
        for l in g:
            for i, c in enumerate(split_cells(l, starts)):
                if c:
                    cols[i].append(c)
        row = []
        for parts in cols:
            cell, prev_hard = "", False
            for j, p in enumerate(parts):
                hard = p.endswith("\\")
                if j > 0:
                    if prev_hard:
                        cell += "<br>"
                        doc.added.update(words("br"))
                    else:
                        cell += " "
                cell += p[:-1] if hard else p
                prev_hard = hard
            row.append(cell.replace("|", "\\|"))
        rows.append(row)
    n = len(starts)
    out = []
    hdr = [c.replace("|", "\\|") for c in header] if header else [""] * n
    out.append("| " + " | ".join(hdr) + " |")
    out.append("| " + " | ".join(["---"] * n) + " |")
    for r in rows:
        out.append("| " + " | ".join(r) + " |")
    doc.tables += 1
    return out


def normalise(doc):
    """Stage A: tables, wrapper divs, setext -> ATX, heading numbers. Code is untouched."""
    src = mark_code(doc.body.split("\n"))
    out = []   # [text, in_code]
    i = 0
    n = len(src)
    while i < n:
        text, code = src[i]
        if code:
            out.append([text, True])
            i += 1
            continue
        # wrapper divs used for table scrolling
        if re.match(r'^<div class="table-scroller">\s*$', text):
            doc.remove("table-scroller wrapper tags", text)
            doc.divs_removed += 1
            i += 1
            continue
        if re.match(r"^</div>\s*$", text):
            doc.remove("table-scroller wrapper tags", text)
            doc.divs_removed += 1
            i += 1
            continue
        # Pandoc simple table
        prev_blank = (not out) or (not out[-1][0].strip())
        if prev_blank and BORDER_RE.match(text) and i + 1 < n and src[i + 1][0].strip():
            # Gather until the closing border
            has_gap = bool(re.search(r"-\s+-", text))
            j = i + 1
            borders_needed = 1 if has_gap else 2  # headerless: one more border; with header: col border + closing
            found = 0
            while j < n and not src[j][1]:
                if BORDER_RE.match(src[j][0]):
                    found += 1
                    if found == borders_needed:
                        break
                j += 1
            block = [src[k][0] for k in range(i, j + 1)]
            out.extend([l, False] for l in convert_table(block, doc))
            i = j + 1
            continue
        # setext heading
        if (
            i + 1 < n
            and not src[i + 1][1]
            and re.match(r"^(=+|-+)\s*$", src[i + 1][0])
            and text.strip()
            and not re.match(r"^\s*([-*+>#]|\d+[.)])\s", text)
            and not BORDER_RE.match(text)
            and prev_blank
        ):
            level = 1 if src[i + 1][0].startswith("=") else 2
            out.append(["#" * level + " " + text.strip(), False])
            doc.setext += 1
            i += 2
            continue
        out.append([text, False])
        i += 1
    # headings and number stripping
    for idx, item in enumerate(out):
        text, code = item
        if code:
            continue
        m = re.match(r"^(#{1,6}) (.*?)\s*#*\s*$", text)
        if not m:
            continue
        level, raw = len(m.group(1)), m.group(2)
        stripped = raw
        if doc.kind == "tutorial":
            nm = NUM_PREFIX_RE.match(raw)
            if nm:
                doc.remove("heading numbers", nm.group(0))
                stripped = raw[nm.end():]
        item[0] = "#" * level + " " + stripped
        doc.headings.append({"line": idx, "level": level, "raw": raw, "text": stripped})
    # collapse runs of blank lines outside code
    final = []
    for text, code in out:
        if not code and not text.strip() and final and not final[-1][1] and not final[-1][0].strip():
            continue
        final.append([text if code else text, code])
    # headings reference line indices in `out`; rebuild index mapping after collapse
    # (simplest: recompute heading list from final)
    doc.lines = final
    rebuilt = []
    k = 0
    for idx, (text, code) in enumerate(final):
        if code:
            continue
        m = re.match(r"^(#{1,6}) (.*)$", text)
        if m:
            rebuilt.append({"line": idx, "level": len(m.group(1)), "text": m.group(2)})
    # merge raw text from the original heading list (same order)
    assert len(rebuilt) == len(doc.headings), (doc.name, len(rebuilt), len(doc.headings))
    for r, h in zip(rebuilt, doc.headings):
        h["line"] = r["line"]


# ---------------------------------------------------------------- structure

class Page:
    def __init__(self, doc, slug, title, order, lines, kind, h1_raw=None):
        self.doc = doc
        self.slug = slug
        self.title = title
        self.order = order
        self.lines = lines
        self.kind = kind          # "chapter" | "article" | "index"
        self.h1_raw = h1_raw
        self.dir = None           # content-relative directory, set later
        self.footnotes = []
        self.range = (0, 0)       # line range in the normalised document

    @property
    def url(self):
        # directory-style URL path below the base, without leading/trailing slash
        return f"{self.dir}/{self.slug}" if self.slug != "index" else self.dir


def build_pages(doc):
    """Split a document into pages. Tutorials: one page per H1 chapter."""
    if doc.kind == "article":
        pg = Page(doc, ARTICLE_SLUG[doc.name], doc.meta["title"], None, doc.lines, "article")
        pg.range = (0, len(doc.lines))
        return [pg]
    chapters, cur, order = [], None, 0
    h1_idx = [h["line"] for h in doc.headings if h["level"] == 1]
    first = h1_idx[0]
    pre = [l for l, c in doc.lines[:first] if l.strip()]
    if pre:
        PROBLEMS.error(f"{doc.name}: content before first chapter heading: {pre[:3]}")
    bounds = h1_idx + [len(doc.lines)]
    used = Dedup()
    for b in range(len(h1_idx)):
        seg = doc.lines[bounds[b]:bounds[b + 1]]
        title = re.match(r"^# (.*)$", seg[0][0]).group(1).strip()
        order += 1
        slug = used.unique(slugify(title))
        # drop the H1 line itself; trim leading/trailing blank lines
        body = seg[1:]
        while body and not body[0][1] and not body[0][0].strip():
            body = body[1:]
        while body and not body[-1][1] and not body[-1][0].strip():
            body = body[:-1]
        raw = next(h["raw"] for h in doc.headings if h["line"] == bounds[b])
        page = Page(doc, slug, title, order, body, "chapter", h1_raw=raw)
        page.range = (bounds[b], bounds[b + 1])
        doc.remove("chapter titles moved to front matter", title)
        chapters.append(page)
    return chapters


# ---------------------------------------------------------------- anchors / links

class LinkMap:
    def __init__(self, docs_pages):
        # (docname, pandoc_id) -> (page, new_anchor or None)
        self.map = {}
        self.pages_by_doc = {}
        for doc, pages in docs_pages:
            self.pages_by_doc[doc.name] = pages
            pand = Dedup()
            slugs = {id(p): Dedup() for p in pages}
            for dd in slugs.values():
                dd.seen.add("_top")
            for h in doc.headings:
                pid = pand.unique(pandoc_id(h["raw"]))
                page = next(p for p in pages if p.range[0] <= h["line"] < p.range[1])
                if h["level"] == 1 and doc.kind == "tutorial":
                    anchor = None   # chapter title becomes the page title
                else:
                    anchor = slugs[id(page)].unique(github_slug(h["text"]))
                self.map[(doc.name, pid)] = (page, anchor)

    def resolve(self, docname, pid):
        return self.map.get((docname, pid))


def rel_url(from_page, to_dir, anchor):
    """Relative link between directory-style URLs."""
    import posixpath
    here = from_page.url
    rel = posixpath.relpath(to_dir, start=here)
    rel = "./" if rel == "." else rel + "/"
    return rel + (f"#{anchor}" if anchor else "")


LINK_DOC_RE = re.compile(
    r"^(?:https?://(?:www\.)?thymeleaf\.org)?/doc/(tutorials/3\.1|articles)/([A-Za-z0-9_]+)\.html(?:#(.*))?$"
)
LINK_REL_ARTICLE_RE = re.compile(r"^([A-Za-z0-9_]+)\.html(?:#(.*))?$")


class LinkRewriter:
    def __init__(self, linkmap, tutorial_index_pages, article_pages):
        self.lm = linkmap
        self.tidx = tutorial_index_pages   # docname -> Page (index)
        self.apages = article_pages        # docname -> Page
        self.counts = collections.Counter()
        self.log = []

    def target_page(self, group, name):
        if group == "tutorials/3.1" and name in self.tidx:
            return ("tutorial", name)
        if group == "articles" and name in self.apages:
            return ("article", name)
        return None

    def rewrite(self, dest, page):
        doc = page.doc
        # 1. in-document anchors
        if dest.startswith("#"):
            return self.to_doc(doc.name, doc.kind, dest[1:], page, dest)
        m = LINK_DOC_RE.match(dest)
        if m:
            group, name, anchor = m.group(1), m.group(2), m.group(3)
            tgt = self.target_page(group, name)
            if tgt:
                return self.to_doc(name, tgt[0], anchor, page, dest)
            self.counts["absolute (not converted)"] += 1
            return self.absolute(dest)
        if doc.kind == "article":
            m = LINK_REL_ARTICLE_RE.match(dest)
            if m and not dest.startswith(("http", "/")):
                name, anchor = m.group(1), m.group(2)
                if name in self.apages:
                    return self.to_doc(name, "article", anchor, page, dest)
                self.counts["absolute (not converted)"] += 1
                return f"{SITE_ORIGINAL}/doc/articles/{dest}"
        if dest.startswith("/") and not dest.startswith("//"):
            self.counts["absolute (not converted)"] += 1
            return SITE_ORIGINAL + dest
        if re.match(r"^http://(www\.)?thymeleaf\.org(/|$)", dest):
            self.counts["absolute (not converted)"] += 1
            return self.absolute(dest)
        if re.match(r"^https://thymeleaf\.org(/|$)", dest):
            return self.absolute(dest)
        self.counts["external, unchanged"] += 1
        return dest

    @staticmethod
    def absolute(dest):
        return re.sub(r"^https?://(www\.)?thymeleaf\.org", SITE_ORIGINAL, dest)

    def to_doc(self, name, kind, anchor, page, original):
        if kind == "tutorial":
            pages = self.lm.pages_by_doc[name]
            idx = self.tidx[name]
        else:
            pages = self.lm.pages_by_doc[name]
            idx = self.apages[name]
        if not anchor:
            target = idx
            self.counts["internal"] += 1
            return rel_url(page, target.url, None)
        res = self.lm.resolve(name, anchor)
        if res is None:
            msg = f"{page.doc.name}/{page.slug}: unresolved anchor '{original}'"
            PROBLEMS.error(msg)
            self.counts["unresolved"] += 1
            return original
        tp, tanchor = res
        self.counts["internal"] += 1
        if tp is page:
            return f"#{tanchor}" if tanchor else "./"
        return rel_url(page, tp.url, tanchor)


CODE_SPAN_RE = re.compile(r"(?<!`)(`+)(?!`)(.+?)(?<!`)\1(?!`)", re.DOTALL)


def mask_code(text):
    return CODE_SPAN_RE.sub(lambda m: "\x00" * len(m.group(0)), text)


def inline_transform(text, page, rewriter, images, doc):
    """Rewrite link/image destinations and neutralise stray raw HTML in a text chunk."""
    parts = re.split(r"(\n\s*\n)", text)
    out = []
    for part in parts:
        if re.fullmatch(r"\n\s*\n", part) or not part:
            out.append(part)
            continue
        # Pandoc inline footnotes ^[text] -> GFM footnotes [^n] with a definition at the page end
        masked = mask_code(part)
        res, pos = [], 0
        for m in re.finditer(r"\^\[([^\]\x00]+)\]", masked):
            page.footnotes.append(part[m.start(1):m.end(1)])
            n = len(page.footnotes)
            res.append(part[pos:m.start()])
            res.append(f"[^{n}]")
            pos = m.end()
            doc.added.update(words(f"{n} {n}"))   # the label appears in the reference and in the definition
        res.append(part[pos:])
        part = "".join(res)
        masked = mask_code(part)
        res, pos = [], 0
        for m in re.finditer(r"\]\(([^)\s\x00]+)\)", masked):
            # find opening bracket to know if this is an image
            depth, k = 0, m.start()
            while k >= 0:
                ch = masked[k]
                if ch == "]":
                    depth += 1
                elif ch == "[":
                    depth -= 1
                    if depth == 0:
                        break
                k -= 1
            is_image = k > 0 and masked[k - 1] == "!"
            dest = m.group(1)
            if is_image:
                new = images(dest, page)
            else:
                new = rewriter.rewrite(dest, page)
            res.append(part[pos:m.start(1)])
            res.append(new)
            pos = m.end(1)
        res.append(part[pos:])
        part = "".join(res)
        # stray raw HTML outside code spans (e.g. <form:input>): show it literally
        masked = mask_code(part)
        res, pos = [], 0
        for m in re.finditer(r"<(/?[A-Za-z][\w:.-]*)(\s[^<>]*)?/?>", masked):
            tag = m.group(0)
            if re.match(r"<(https?|mailto):", tag):
                continue
            line_start = masked.rfind("\n", 0, m.start()) + 1
            if tag == "<br>" and masked[line_start:].startswith("|"):
                continue   # <br> that this script itself put into a table cell
            res.append(part[pos:m.start()])
            res.append("`" + part[m.start():m.end()] + "`")
            pos = m.end()
            doc.raw_html_wrapped.append(tag)
        res.append(part[pos:])
        out.append("".join(res))
    return "".join(out)


# ---------------------------------------------------------------- output

def first_sentence(text, limit=200):
    t = re.sub(r"\s+", " ", text).strip()
    t = re.sub(r"\s*[:;]$", ".", t)
    abbrev = ("e.g.", "i.e.", "etc.", "vs.", "cf.")
    end = len(t)
    for m in re.finditer(r"[.!?][\"')\]]*(?=\s+[A-Z\"'(\[])", t):
        head = t[: m.end()]
        if head.lower().endswith(abbrev):
            continue
        end = m.end()
        break
    s = t[:end]
    if len(s) > limit:
        s = s[:limit].rsplit(" ", 1)[0].rstrip(",;:") + "…"
    return s


def make_description(page, fallback):
    para, collecting = [], False
    for text, code in page.lines[:80]:
        if code:
            if collecting:
                break
            continue
        if not text.strip():
            if collecting:
                break
            continue
        if re.match(r"^(#{1,6} |>|\s|[-*+] |\d+[.)] |\||<)", text):
            if collecting:
                break
            continue
        collecting = True
        para.append(text.strip())
    if para:
        joined = re.sub(r"\[([^\]]*)\]\([^)]*\)", lambda m: "[" + re.sub(r"\s+", "\x01", m.group(1)) + "](x)", " ".join(para))
        d = first_sentence(plain_inline(joined)).replace("\x01", " ")
        if len(d) >= 20:
            return d
    return fallback


def source_url(page):
    doc = page.doc
    if doc.kind == "tutorial":
        base = f"{SITE_ORIGINAL}/doc/tutorials/{THYMELEAF_VERSION_KEY}/{doc.name}.html"
        if page.kind == "chapter":
            return base + "#" + pandoc_id(page.h1_raw)
        return base
    return f"{SITE_ORIGINAL}/doc/articles/{doc.name}.html"


def source_note(page):
    return (
        f"*Adapted from the [Thymeleaf documentation]({source_url(page)}) at thymeleaf.org, "
        f"licensed under [CC BY-SA 3.0]({LICENSE_URL}).*"
    )


def author_line(meta):
    a = meta.get("author")
    if not a or a == "Thymeleaf":
        return None
    a = re.sub(r'<a href="([^"]+)">([^<]*)</a>', lambda m: f"[{m.group(2)}]({m.group(1)})", a)
    a = html.unescape(a)
    return f"**Author:** {a}"


def render_page(page, description):
    fm = ["---", f"title: {yaml_str(page.title)}", f"description: {yaml_str(description)}"]
    if page.order is not None:
        fm += ["sidebar:", f"  order: {page.order}"]
    fm.append("---")
    parts = ["\n".join(fm), ""]
    if page.kind == "article":
        al = author_line(page.doc.meta)
        if al:
            parts += [al, ""]
    body = "\n".join(t for t, _ in page.lines).strip("\n")
    if body:
        parts += [body, ""]
    if page.footnotes:
        parts += [f"[^{i}]: {t}" for i, t in enumerate(page.footnotes, 1)] + [""]
    parts += ["---", "", source_note(page), ""]
    return "\n".join(parts)


def render_index(doc, tutorial_title, chapters, index_page, version, document_version):
    desc = f"Chapters of “{tutorial_title}” for Thymeleaf {THYMELEAF_VERSION_KEY}."
    fm = ["---", f"title: {yaml_str(tutorial_title)}", f"description: {yaml_str(desc)}",
          "sidebar:", "  order: 0", "---"]
    lines = ["\n".join(fm), "",
             f"This tutorial covers Thymeleaf {version}. Document version: {document_version}.", "",
             "Chapters:", ""]
    for c in chapters:
        lines.append(f"- [{c.title}]({rel_url(index_page, c.url, None)})")
    lines += ["", "---", "", source_note(index_page), ""]
    return "\n".join(lines)


# ---------------------------------------------------------------- code blocks

def code_blocks(lines):
    """List of fenced code blocks (each is the tuple of its lines)."""
    blocks, cur = [], None
    for text, code in mark_code(lines):
        if code:
            cur = (cur or []) + [text]
            m = FENCE_RE.match(text)
            # closing fence: a fence line while a block is already open
            if m and len(cur) > 1 and not m.group(3).strip():
                blocks.append(tuple(cur))
                cur = None
        else:
            if cur:
                blocks.append(tuple(cur))
                cur = None
    return blocks


# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--source", type=Path, default=DEFAULT_SOURCE,
                    help="path to a thymeleaf-docs checkout (default: %(default)s)")
    ap.add_argument("--image-fallback", type=Path, default=DEFAULT_IMAGE_FALLBACK,
                    help="thymeleaf.github.io/doc folder searched when an image is missing in --source")
    ap.add_argument("--project", type=Path, default=PROJECT, help="Astro project root (default: %(default)s)")
    ap.add_argument("--report", type=Path, default=HERE / "report.md", help="where to write the report")
    args = ap.parse_args()

    source = args.source.resolve()
    project = args.project.resolve()
    content = project / "src" / "content" / "docs" / DOCS_ROOT
    version, document_version = read_document_metadata(source)

    # ---- load
    docs = []
    for name, _ in TUTORIALS:
        p = source / "docs" / "tutorials" / THYMELEAF_VERSION_KEY / f"{name}.md"
        meta, body = split_frontmatter(p.read_text(encoding="utf8"))
        docs.append(Doc("tutorial", name, meta, body))
    for name, _ in ARTICLES:
        p = source / "docs" / "articles" / f"{name}.md"
        meta, body = split_frontmatter(p.read_text(encoding="utf8"))
        docs.append(Doc("article", name, meta, body))

    # ---- stage A + pages
    docs_pages = []
    for d in docs:
        normalise(d)
        pages = build_pages(d)
        for pg in pages:
            pg.dir = (f"{DOCS_ROOT}/tutorials/{TUTORIAL_DIR[d.name]}" if d.kind == "tutorial"
                      else f"{DOCS_ROOT}/articles")
        docs_pages.append((d, pages))

    tutorial_index = {}
    for d, pages in docs_pages:
        if d.kind == "tutorial":
            ip = Page(d, "index", d.meta["title"], 0, [], "index")
            ip.dir = f"{DOCS_ROOT}/tutorials/{TUTORIAL_DIR[d.name]}"
            tutorial_index[d.name] = ip
    article_pages = {d.name: pages[0] for d, pages in docs_pages if d.kind == "article"}

    lm = LinkMap(docs_pages)
    rewriter = LinkRewriter(lm, tutorial_index, article_pages)

    # ---- images
    image_jobs = {}   # dest file (relative to content root) -> source path
    image_refs = collections.Counter()

    def find_image(doc, rel):
        cands = []
        if doc.kind == "tutorial":
            cands.append(source / "docs" / "tutorials" / THYMELEAF_VERSION_KEY / rel)
            cands.append(args.image_fallback / "tutorials" / THYMELEAF_VERSION_KEY / rel)
        else:
            cands.append(source / "docs" / "articles" / rel)
            cands.append(args.image_fallback / "articles" / rel)
        for c in cands:
            if c.is_file():
                return c
        return None

    def images(dest, page):
        doc = page.doc
        if re.match(r"^[a-z]+://", dest) or dest.startswith("/"):
            PROBLEMS.error(f"{doc.name}: unexpected non-local image {dest}")
            return dest
        src_file = find_image(doc, dest)
        if src_file is None:
            PROBLEMS.error(f"{doc.name}: image not found: {dest}")
            return dest
        if doc.kind == "tutorial":
            # images/<tutorial>/<file>  ->  <tutorial dir>/images/<file>
            out_rel = f"images/{Path(dest).name}"
            out_dir = f"tutorials/{TUTORIAL_DIR[doc.name]}"
        else:
            out_rel = dest   # images/<article group>/<file>, next to the article pages
            out_dir = "articles"
        image_jobs[f"{out_dir}/{out_rel}"] = src_file
        image_refs[f"{out_dir}/{out_rel}"] += 1
        return "./" + out_rel

    # ---- stage B: inline rewriting per page
    for d, pages in docs_pages:
        for pg in pages:
            chunk, new_lines = [], []

            def flush():
                if chunk:
                    text = inline_transform("\n".join(chunk), pg, rewriter, images, d)
                    new_lines.extend([l, False] for l in text.split("\n"))
                    chunk.clear()

            for text, code in pg.lines:
                if code:
                    flush()
                    new_lines.append([text, True])
                else:
                    chunk.append(text)
            flush()
            pg.lines = new_lines

    # ---- write (generated folders are wiped first: output must depend only on the sources)
    for _, dirname in TUTORIALS:
        shutil.rmtree(content / "tutorials" / dirname, ignore_errors=True)
    shutil.rmtree(content / "articles", ignore_errors=True)

    written = {}   # relative path -> (page, text)
    for d, pages in docs_pages:
        if d.kind == "tutorial":
            out_dir = content / "tutorials" / TUTORIAL_DIR[d.name]
            out_dir.mkdir(parents=True, exist_ok=True)
            ip = tutorial_index[d.name]
            txt = render_index(d, d.meta["title"], pages, ip, version, document_version)
            (out_dir / "index.md").write_text(txt, encoding="utf8", newline="\n")
            written[f"tutorials/{TUTORIAL_DIR[d.name]}/index.md"] = (ip, txt)
        for pg in pages:
            out_dir = content / ("tutorials/" + TUTORIAL_DIR[d.name] if d.kind == "tutorial" else "articles")
            out_dir.mkdir(parents=True, exist_ok=True)
            fallback = (f"Chapter “{pg.title}” of the tutorial “{d.meta['title']}” for Thymeleaf {THYMELEAF_VERSION_KEY}."
                        if d.kind == "tutorial" else f"Thymeleaf article: {pg.title}.")
            desc = make_description(pg, fallback)
            txt = render_page(pg, desc)
            rel = (f"tutorials/{TUTORIAL_DIR[d.name]}/{pg.slug}.md" if d.kind == "tutorial" else f"articles/{pg.slug}.md")
            (content / rel).write_text(txt, encoding="utf8", newline="\n")
            written[rel] = (pg, txt)
    for rel, srcf in sorted(image_jobs.items()):
        dst = content / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(srcf, dst)

    # ---- report
    write_report(args, docs_pages, written, image_refs, rewriter, version, document_version, source)
    for w in PROBLEMS.warnings:
        print("WARNING:", w, file=sys.stderr)
    for e in PROBLEMS.errors:
        print("ERROR:", e, file=sys.stderr)
    print(f"Wrote {len(written)} pages and {len(image_jobs)} images; report: {args.report}")
    return 1 if PROBLEMS.errors else 0


def strip_added(text, page):
    """Return only the converted source body of an output page (no front matter, author line, note)."""
    _, body = split_frontmatter(text)
    body = re.sub(r"\n---\n\n\*Adapted from the .*\*\n$", "\n", body)
    body = re.sub(r"^\n?\*\*Author:\*\* .*\n", "", body)
    return body


def write_report(args, docs_pages, written, image_refs, rewriter, version, document_version, source):
    out = ["# Conversion report", "",
           "Generated by `scripts/migrate-content/migrate.py`. Deterministic: rerunning produces the same text.", "",
           f"Thymeleaf version: {version}. Document version: {document_version}.", ""]
    ok_all = True
    out += ["## Per source", "",
            "Word tokens are `\\w+` runs, counted as a multiset, ignoring link and image destinations "
            "(those are rewritten on purpose). Front matter, the added author line and the added source note are excluded "
            "from the output side.", "",
            "| Source | Pages | Words in source | Words in output | Removed on purpose | Added on purpose | Unexplained difference | Code blocks src / out | Code identical |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |"]
    details = []
    for d, pages in docs_pages:
        rel = (f"tutorials/{THYMELEAF_VERSION_KEY}/{d.name}.md" if d.kind == "tutorial" else f"articles/{d.name}.md")
        src_body = d.body
        src_counter = words(src_body)
        out_texts = []
        for pg in pages:
            path = (f"tutorials/{TUTORIAL_DIR[d.name]}/{pg.slug}.md" if d.kind == "tutorial" else f"articles/{pg.slug}.md")
            out_texts.append(strip_added(written[path][1], pg))
        out_body = "\n".join(out_texts)
        out_counter = words(out_body)
        expected = src_counter - d.removed + d.added
        missing = expected - out_counter
        extra = out_counter - expected
        unexplained = sum(missing.values()) + sum(extra.values())
        if unexplained:
            ok_all = False
        sb = code_blocks(src_body.split("\n"))
        ob = code_blocks(out_body.split("\n"))
        same = sb == ob
        if not same:
            ok_all = False
        out.append(
            f"| `{rel}` | {len(pages)} | {sum(src_counter.values())} | {sum(out_counter.values())} | "
            f"{sum(d.removed.values())} | {sum(d.added.values())} | {unexplained} | {len(sb)} / {len(ob)} | {'yes' if same else 'NO'} |"
        )
        det = [f"### `{rel}`", ""]
        det.append(f"- Output pages: {len(pages)}" + (" plus an index page (not counted)" if d.kind == "tutorial" else ""))
        det.append(f"- Code blocks with a language tag: {sum(1 for b in sb if FENCE_RE.match(b[0]).group(3).strip())} of {len(sb)}")
        det.append(f"- Setext headings converted to ATX: {d.setext}")
        det.append("- Tokens removed on purpose: " + (", ".join(f"{v} {k}" for k, v in sorted(d.cats.items())) or "none"))
        det.append(f"- Pandoc tables converted: {d.tables}; table-scroller wrapper tags removed: {d.divs_removed}")
        det.append(f"- Added `br` tokens from `<br>` inside table cells: {d.added.get('br', 0)}")
        if d.raw_html_wrapped:
            det.append(f"- Stray raw HTML shown literally (wrapped in backticks): {', '.join('`' + t + '`' for t in d.raw_html_wrapped)}")
        if missing or extra:
            det.append(f"- UNEXPLAINED missing: {dict(missing)}; extra: {dict(extra)}")
        details += det + [""]
    out += [""] + details
    out += ["Explained differences are only: heading numbers removed, tutorial chapter titles moved to the front matter "
            "(H1 becomes the page title), `table-scroller` wrapper tags removed, and `br` tokens from `<br>` line breaks "
            "inside converted table cells.", ""]
    out += ["## Output pages", "", "| Page | Words (body) |", "| --- | ---: |"]
    for rel in sorted(written):
        pg, txt = written[rel]
        if pg.kind == "index":
            continue
        out.append(f"| `{rel}` | {sum(words(strip_added(txt, pg)).values())} |")
    out += ["", "## Links", "", "| Kind | Count |", "| --- | ---: |"]
    for k in sorted(rewriter.counts):
        out.append(f"| {k} | {rewriter.counts[k]} |")
    out += ["", "## Images", "", f"{sum(image_refs.values())} references to {len(image_refs)} image files.", ""]
    for k in sorted(image_refs):
        out.append(f"- `{k}` x{image_refs[k]}")
    out += ["", "## Problems", ""]
    if not PROBLEMS.errors and not PROBLEMS.warnings:
        out.append("None.")
    for e in PROBLEMS.errors:
        out.append(f"- ERROR: {e}")
    for w in PROBLEMS.warnings:
        out.append(f"- WARNING: {w}")
    out += ["", f"## Result", "", "All word and code block checks passed." if ok_all and not PROBLEMS.errors else "CHECKS FAILED - see above.", ""]
    args.report.write_text("\n".join(out), encoding="utf8", newline="\n")
    if not ok_all:
        PROBLEMS.error("word/code comparison failed, see report")


if __name__ == "__main__":
    sys.exit(main())
