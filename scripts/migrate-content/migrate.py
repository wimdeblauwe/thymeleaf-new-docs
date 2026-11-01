#!/usr/bin/env python3
"""Convert the English Thymeleaf 3.1 Pandoc-Markdown sources into Starlight pages.

Python 3 standard library only. Deterministic: the same sources always produce
byte-identical output. See README.md in this folder.

The conversion itself is mechanical. structure.toml decides which source
section lands on which page, and lists the few rewordings of stale references.
"""

import argparse
import collections
import html
import json
import posixpath
import re
import shutil
import sys
import tomllib
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

TUTORIALS = ["usingthymeleaf", "thymeleafspring", "extendingthymeleaf"]
ARTICLES = [
    "layouts",
    "springsecurity",
    "springmvcaccessdata",
    "springmail",
    "standardurlsyntax",
    "thvsjsp",
    "fromhtmltohtmlviahtml",
    "standarddialect5minutes",
    "sayhelloextendingthymeleaf5minutes",
    "sayhelloagainextendingthymeleafevenmore5minutes",
]

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
        self.replacements = []    # [[replace]] entries from structure.toml
        self.footnote_defs = []   # converted footnotes, for the word comparison
        self.by_pid = {}          # Pandoc id -> heading
        self.home = None          # key of the page a link to the whole document goes to


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
    ids = Dedup()
    for r, h in zip(rebuilt, doc.headings):
        h["line"] = r["line"]
        h["pid"] = ids.unique(pandoc_id(h["raw"]))
        doc.by_pid[h["pid"]] = h


# ---------------------------------------------------------------- structure

class Piece:
    """A selection of one source document, placed on a page (see structure.toml)."""

    def __init__(self, doc, indices, spec):
        self.doc = doc            # None for a text piece
        self.indices = indices    # selected line numbers in doc.lines
        self.spec = spec
        self.start_heading = None # the source heading the selection starts at, if any
        self.anchor_heading = None  # the heading whose anchor identifies this piece's source
        self.whole = False        # the whole source document, so the source link has no anchor
        self.kept = False         # lines[0] is the piece's own heading
        self.heading = spec.get("heading")  # heading added on purpose
        self.lines = []           # [text, in_code]
        self.headings = []        # (source heading, level, text) of headings left in the piece
        self.dropped = None       # source heading replaced by the page title

    @property
    def is_text(self):
        return "text" in self.spec


class Page:
    def __init__(self, directory, spec, order):
        self.dir = f"{DOCS_ROOT}/{directory}"
        self.slug = spec["slug"]
        self.key = f"{directory}/{self.slug}"
        self.title = spec["title"]
        self.order = order
        self.hidden = spec.get("hidden", False)
        self.manual = spec.get("manual", False)
        self.pieces = []
        self.footnotes = []

    @property
    def url(self):
        # directory-style URL path below the base, without leading/trailing slash
        return f"{self.dir}/{self.slug}"

    @property
    def rel(self):
        return f"{self.key}.md"

    @property
    def docs(self):
        out = []
        for p in self.pieces:
            if p.doc and p.doc not in out:
                out.append(p.doc)
        return out


def find_heading(doc, pid, where):
    h = doc.by_pid.get(pid)
    if h is None:
        raise SystemExit(f"structure.toml: {where}: no heading '{pid}' in {doc.name}")
    return h


def section_end(doc, h):
    return next((o["line"] for o in doc.headings if o["line"] > h["line"] and o["level"] <= h["level"]),
                len(doc.lines))


def find_text(doc, needle, lo, hi, where):
    for i in range(lo, hi):
        if not doc.lines[i][1] and needle in doc.lines[i][0]:
            return i
    raise SystemExit(f"structure.toml: {where}: text not found in the section: {needle!r}")


def select_piece(spec, docs, where):
    """Turn one entry of a page's `pieces` list into a Piece holding source line numbers."""
    if isinstance(spec, str):
        spec = {"section": spec}
    if "text" in spec:
        doc = docs[spec["doc"]] if "doc" in spec else None
        return Piece(doc, [], spec)
    name, _, pid = spec["section"].partition("#")
    if name not in docs:
        raise SystemExit(f"structure.toml: {where}: unknown document '{name}'")
    doc = docs[name]
    h = find_heading(doc, pid, where) if pid else None
    lo, hi = (h["line"], section_end(doc, h)) if h else (0, len(doc.lines))
    sect_lo, sect_hi = lo, hi
    if spec.get("intro"):
        hi = next((o["line"] for o in doc.headings if lo < o["line"] < hi), hi)
    if "from" in spec:
        lo = find_text(doc, spec["from"], sect_lo, sect_hi, where)
    if "until" in spec:
        hi = find_text(doc, spec["until"], sect_lo, sect_hi, where)
    drop = set()
    for pid_x in spec.get("exclude", []):
        x = find_heading(doc, pid_x, where)
        drop.update(range(x["line"], section_end(doc, x)))
    for a, b in spec.get("cuts", []):
        drop.update(range(find_text(doc, a, sect_lo, sect_hi, where), find_text(doc, b, sect_lo, sect_hi, where)))
    piece = Piece(doc, [i for i in range(lo, hi) if i not in drop], spec)
    piece.whole = h is None and not spec.get("exclude")
    if h and lo == h["line"]:
        piece.start_heading = h
    piece.anchor_heading = h
    return piece


def level_pieces(piece, first):
    """Build a piece's lines, resolving its heading levels for its place on the page."""
    doc, spec = piece.doc, piece.spec
    selected = list(piece.indices)
    while selected and not doc.lines[selected[-1]][1] and not doc.lines[selected[-1]][0].strip():
        selected.pop()
    start = piece.start_heading
    keep = bool(start) and not piece.heading and spec.get("keep_heading", not first)
    if start and not keep:
        selected = selected[1:]
        piece.dropped = start
        doc.remove("chapter titles moved to front matter", start["text"])
    while selected and not doc.lines[selected[0]][1] and not doc.lines[selected[0]][0].strip():
        selected = selected[1:]
    by_line = {h["line"]: h for h in doc.headings}
    inner = [by_line[i]["level"] for i in selected if i in by_line and not (keep and i == start["line"])]
    if keep:
        shift = start["level"] - 2
    elif inner:
        shift = min(inner) - (3 if piece.heading else 2)
    else:
        shift = 0
    piece.kept = keep
    for i in selected:
        text, code = doc.lines[i]
        if i in by_line:
            h = by_line[i]
            level = min(h["level"] - shift, 6)
            text = "#" * level + " " + h["text"]
            piece.headings.append((h, level, h["text"]))
        piece.lines.append([text, code])


def build_pages(structure, docs):
    pages, seen, retired, retired_lines = [], {}, [], set()
    for entry in structure.get("retired", []):
        name, _, pid = entry.partition("#")
        h = find_heading(docs[name], pid, "retired")
        retired.append((docs[name], h, next(o for o in docs[name].headings if o["line"] > h["line"])))
        retired_lines.add((name, h["line"]))
        docs[name].remove("chapter titles moved to front matter", h["text"])
    for section in structure["section"]:
        for order, spec in enumerate(section["page"], 1):
            page = Page(section["dir"], spec, order)
            for n, ps in enumerate(spec["pieces"]):
                piece = select_piece(ps, docs, page.key)
                if not piece.is_text:
                    level_pieces(piece, n == 0)
                    for i in piece.indices:
                        seen.setdefault((piece.doc.name, i), []).append(page.key)
                page.pieces.append(piece)
            pages.append(page)
    for d in docs.values():
        d.home = None
        for i, (text, _) in enumerate(d.lines):
            where = seen.get((d.name, i), [])
            if len(where) > 1:
                PROBLEMS.error(f"{d.name}: line {i} is placed on several pages {where}: {text[:60]!r}")
            if text.strip() and not where and (d.name, i) not in retired_lines:
                PROBLEMS.error(f"{d.name}: line {i} is on no page: {text[:60]!r}")
            if text.strip() and d.home is None and where:
                d.home = where[0]
    return pages, retired


# ---------------------------------------------------------------- anchors / links

class LinkMap:
    def __init__(self, pages, retired):
        self.map = {}      # (docname, pandoc_id) -> (page, new_anchor or None)
        self.by_key = {p.key: p for p in pages}
        for page in pages:
            slugs = Dedup()
            slugs.seen.add("_top")
            for piece in page.pieces:
                if piece.heading:
                    slugs.unique(github_slug(piece.heading))
                if piece.dropped:
                    self.map[(piece.doc.name, piece.dropped["pid"])] = (page, None)
                for h, _, text in piece.headings:
                    self.map[(piece.doc.name, h["pid"])] = (page, slugs.unique(github_slug(text)))
        # a retired chapter title links to the page that holds the chapter's first section
        for doc, h, following in retired:
            self.map[(doc.name, h["pid"])] = (self.map[(doc.name, following["pid"])][0], None)

    def resolve(self, docname, pid):
        return self.map.get((docname, pid))

def rel_url(from_page, to_dir, anchor):
    """Relative link between directory-style URLs."""
    here = from_page.url
    rel = posixpath.relpath(to_dir, start=here)
    rel = "./" if rel == "." else rel + "/"
    return rel + (f"#{anchor}" if anchor else "")


LINK_DOC_RE = re.compile(
    r"^(?:https?://(?:www\.)?thymeleaf\.org)?/doc/(tutorials/3\.1|articles)/([A-Za-z0-9_]+)\.html(?:#(.*))?$"
)
LINK_REL_ARTICLE_RE = re.compile(r"^([A-Za-z0-9_]+)\.html(?:#(.*))?$")


class LinkRewriter:
    def __init__(self, linkmap, docs):
        self.lm = linkmap
        self.docs = docs
        self.counts = collections.Counter()
        self.log = []

    def target_doc(self, group, name):
        d = self.docs.get(name)
        if d and ((group == "tutorials/3.1") == (d.kind == "tutorial")):
            return d
        return None

    def rewrite(self, dest, page, doc):
        # 0. links written in structure.toml
        if dest.startswith("page:"):
            key, _, anchor = dest[5:].partition("#")
            if key not in self.lm.by_key:
                PROBLEMS.error(f"{page.key}: unknown page in link '{dest}'")
                return dest
            self.counts["internal"] += 1
            return rel_url(page, self.lm.by_key[key].url, anchor or None)
        # 1. in-document anchors
        if dest.startswith("#"):
            return self.to_doc(doc, dest[1:], page, dest)
        m = LINK_DOC_RE.match(dest)
        if m:
            group, name, anchor = m.group(1), m.group(2), m.group(3)
            tgt = self.target_doc(group, name)
            if tgt:
                return self.to_doc(tgt, anchor, page, dest)
            self.counts["absolute (not converted)"] += 1
            return self.absolute(dest)
        if doc.kind == "article":
            m = LINK_REL_ARTICLE_RE.match(dest)
            if m and not dest.startswith(("http", "/")):
                name, anchor = m.group(1), m.group(2)
                tgt = self.target_doc("articles", name)
                if tgt:
                    return self.to_doc(tgt, anchor, page, dest)
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

    def to_doc(self, target, anchor, page, original):
        if not anchor:
            self.counts["internal"] += 1
            return rel_url(page, self.lm.by_key[target.home].url, None)
        res = self.lm.resolve(target.name, anchor)
        if res is None:
            msg = f"{page.key}: unresolved anchor '{original}'"
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


def inline_transform(text, page, rewriter, images, doc, count=True):
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
            if count:
                doc.added.update(words(f"{n} {n}"))   # the label appears in the reference and in the definition
                doc.footnote_defs.append(f"[^{n}]: {page.footnotes[-1]}")
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
                new = images(dest, page, doc)
            else:
                new = rewriter.rewrite(dest, page, doc)
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
    first = next((p for p in page.pieces if p.lines), None)
    for text, code in (first.lines[:80] if first else []):
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


def doc_url(doc):
    if doc.kind == "tutorial":
        return f"{SITE_ORIGINAL}/doc/tutorials/{THYMELEAF_VERSION_KEY}/{doc.name}.html"
    return f"{SITE_ORIGINAL}/doc/articles/{doc.name}.html"


def source_ref(piece):
    """(label, URL) of the original location of a piece."""
    doc = piece.doc
    h = piece.anchor_heading
    if piece.whole or h is None:
        return doc.meta["title"], doc_url(doc)
    return plain_inline(h["text"]), doc_url(doc) + "#" + h["pid"]


def source_note(page):
    refs = []
    for p in page.pieces:
        if p.is_text:
            continue
        ref = source_ref(p)
        if ref not in refs:
            refs.append(ref)
    licence = f"licensed under [CC BY-SA 3.0]({LICENSE_URL})"
    if len(refs) == 1:
        return f"*Adapted from the [Thymeleaf documentation]({refs[0][1]}) at thymeleaf.org, {licence}.*"
    links = ", ".join(f"[{label}]({url})" for label, url in refs)
    return f"*Adapted from the Thymeleaf documentation at thymeleaf.org, {licence}: {links}.*"


def author_name(meta):
    a = meta.get("author")
    if not a or a == "Thymeleaf":
        return None
    a = re.sub(r'<a href="([^"]+)">([^<]*)</a>', lambda m: f"[{m.group(2)}]({m.group(1)})", a)
    return html.unescape(a)


def render_page(page, description):
    fm = ["---", f"title: {yaml_str(page.title)}", f"description: {yaml_str(description)}", "sidebar:"]
    fm.append(f"  order: {page.order}")
    if page.hidden:
        fm.append("  hidden: true")
    fm.append("---")
    parts = ["\n".join(fm), ""]
    authored = [d for d in page.docs if author_name(d.meta)]
    single = len(page.docs) == 1
    if single and authored:
        parts += [f"**Author:** {author_name(authored[0].meta)}", ""]
    credited = set()
    for piece in page.pieces:
        lines = [t for t, _ in piece.lines]
        if piece.heading:
            parts += [f"## {piece.heading}", ""]
        elif piece.kept:
            parts += [lines[0], ""]
            lines = lines[1:]
            while lines and not lines[0].strip():
                lines = lines[1:]
        d = piece.doc
        if not single and d in authored and d not in credited:
            credited.add(d)
            parts += [f"*This section comes from the article “{d.meta['title']}” by {author_name(d.meta)}.*", ""]
        body = "\n".join(lines).strip("\n")
        if body:
            parts += [body, ""]
    if page.footnotes:
        parts += [f"[^{i}]: {t}" for i, t in enumerate(page.footnotes, 1)] + [""]
    parts += ["---", "", source_note(page), ""]
    return "\n".join(parts)


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


def apply_replacements(text, doc):
    """Reword cross-references that the new structure made stale (structure.toml [[replace]])."""
    for r in doc.replacements:
        n = text.count(r["old"])
        if n:
            text = text.replace(r["old"], r["new"])
            r["used"] = r.get("used", 0) + n
            for _ in range(n):
                doc.remove("stale cross-references reworded", r["old"])
                doc.added.update(words(r["new"]))
    return text


def clear_generated(content, pages, section_dirs):
    """Generated folders are wiped so the output depends only on the sources."""
    keep = {content / p.rel for p in pages if p.manual}
    targets = [content / d for d in section_dirs] + [content / "images"]
    for base in targets:
        for f in sorted(base.rglob("*")) if base.is_dir() else []:
            if f.is_file() and f not in keep:
                f.unlink()
    for base in targets:
        for f in sorted(base.rglob("*"), reverse=True) if base.is_dir() else []:
            if f.is_dir() and not any(f.iterdir()):
                f.rmdir()


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--source", type=Path, default=DEFAULT_SOURCE,
                    help="path to a thymeleaf-docs checkout (default: %(default)s)")
    ap.add_argument("--image-fallback", type=Path, default=DEFAULT_IMAGE_FALLBACK,
                    help="thymeleaf.github.io/doc folder searched when an image is missing in --source")
    ap.add_argument("--project", type=Path, default=PROJECT, help="Astro project root (default: %(default)s)")
    ap.add_argument("--structure", type=Path, default=HERE / "structure.toml",
                    help="mapping of source sections to pages (default: %(default)s)")
    ap.add_argument("--report", type=Path, default=HERE / "report.md", help="where to write the report")
    args = ap.parse_args()

    source = args.source.resolve()
    project = args.project.resolve()
    content = project / "src" / "content" / "docs" / DOCS_ROOT
    version, document_version = read_document_metadata(source)
    structure = tomllib.loads(args.structure.read_text(encoding="utf8"))

    # ---- load
    docs = {}
    for name in TUTORIALS:
        p = source / "docs" / "tutorials" / THYMELEAF_VERSION_KEY / f"{name}.md"
        meta, body = split_frontmatter(p.read_text(encoding="utf8"))
        docs[name] = Doc("tutorial", name, meta, body)
    for name in ARTICLES:
        p = source / "docs" / "articles" / f"{name}.md"
        meta, body = split_frontmatter(p.read_text(encoding="utf8"))
        docs[name] = Doc("article", name, meta, body)
    for r in structure.get("replace", []):
        docs[r["doc"]].replacements.append(r)

    # ---- stage A + pages
    for d in docs.values():
        normalise(d)
    pages, retired = build_pages(structure, docs)
    lm = LinkMap(pages, retired)
    rewriter = LinkRewriter(lm, docs)

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

    def images(dest, page, doc):
        if re.match(r"^[a-z]+://", dest) or dest.startswith("/"):
            PROBLEMS.error(f"{doc.name}: unexpected non-local image {dest}")
            return dest
        src_file = find_image(doc, dest)
        if src_file is None:
            PROBLEMS.error(f"{doc.name}: image not found: {dest}")
            return dest
        # images/<tutorial>/<file> and images/<article group>/<file> keep their source grouping
        out = dest
        image_jobs[out] = src_file
        image_refs[out] += 1
        here = posixpath.dirname(page.rel)
        return posixpath.relpath(out, start=here)

    # ---- stage B: inline rewriting per piece
    for pg in pages:
        for piece in pg.pieces:
            if piece.is_text:
                d = piece.doc or next(iter(docs.values()))
                text = inline_transform(piece.spec["text"], pg, rewriter, images, d, count=False)
                piece.lines = [[l, False] for l in text.split("\n")]
                continue
            d = piece.doc
            chunk, new_lines = [], []

            def flush():
                if chunk:
                    text = inline_transform(apply_replacements("\n".join(chunk), d), pg, rewriter, images, d)
                    new_lines.extend([l, False] for l in text.split("\n"))
                    chunk.clear()

            for text, code in piece.lines:
                if code:
                    flush()
                    new_lines.append([text, True])
                else:
                    chunk.append(text)
            flush()
            piece.lines = new_lines

    for d in docs.values():
        for r in d.replacements:
            if not r.get("used"):
                PROBLEMS.error(f"{d.name}: replacement never matched: {r['old']!r}")

    # ---- write
    section_dirs = [s["dir"] for s in structure["section"]]
    clear_generated(content, pages, section_dirs)

    written = {}   # relative path -> (page, text)
    for pg in pages:
        if pg.manual:
            continue
        txt = render_page(pg, make_description(pg, f"{pg.title} in Thymeleaf {THYMELEAF_VERSION_KEY}."))
        out = content / pg.rel
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(txt, encoding="utf8", newline="\n")
        written[pg.rel] = (pg, txt)
    for rel, srcf in sorted(image_jobs.items()):
        dst = content / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(srcf, dst)

    # ---- report
    write_report(args, docs, pages, written, image_refs, rewriter, version, document_version)
    for w in PROBLEMS.warnings:
        print("WARNING:", w, file=sys.stderr)
    for e in PROBLEMS.errors:
        print("ERROR:", e, file=sys.stderr)
    print(f"Wrote {len(written)} pages and {len(image_jobs)} images; report: {args.report}")
    return 1 if PROBLEMS.errors else 0


def doc_output(doc, pages):
    """The converted text of one source document, across every page it landed on."""
    out = []
    for pg in pages:
        for piece in pg.pieces:
            if piece.doc is doc and not piece.is_text:
                out.append("\n".join(t for t, _ in piece.lines))
    return "\n".join(out + doc.footnote_defs)


def write_report(args, docs, pages, written, image_refs, rewriter, version, document_version):
    out = ["# Conversion report", "",
           "Generated by `scripts/migrate-content/migrate.py`. Deterministic: rerunning produces the same text.", "",
           f"Thymeleaf version: {version}. Document version: {document_version}.", ""]
    ok_all = True
    out += ["## Per source", "",
            "Word tokens are `\\w+` runs, counted as a multiset, ignoring link and image destinations "
            "(those are rewritten on purpose). Front matter, author lines, source notes and text added by "
            "`structure.toml` are excluded from the output side. A code block is compared as a whole, "
            "in any order, because moved sections change the order.", "",
            "| Source | Pages | Words in source | Words in output | Removed on purpose | Added on purpose | Unexplained difference | Code blocks src / out | Code identical |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |"]
    details = []
    for d in docs.values():
        rel = (f"tutorials/{THYMELEAF_VERSION_KEY}/{d.name}.md" if d.kind == "tutorial" else f"articles/{d.name}.md")
        doc_pages = [p for p in pages if d in p.docs]
        src_counter = words(d.body)
        out_body = doc_output(d, pages)
        out_counter = words(out_body)
        expected = src_counter - d.removed + d.added
        missing = expected - out_counter
        extra = out_counter - expected
        unexplained = sum(missing.values()) + sum(extra.values())
        if unexplained:
            ok_all = False
        sb = code_blocks(d.body.split("\n"))
        ob = code_blocks(out_body.split("\n"))
        same = collections.Counter(sb) == collections.Counter(ob)
        if not same:
            ok_all = False
        out.append(
            f"| `{rel}` | {len(doc_pages)} | {sum(src_counter.values())} | {sum(out_counter.values())} | "
            f"{sum(d.removed.values())} | {sum(d.added.values())} | {unexplained} | {len(sb)} / {len(ob)} | {'yes' if same else 'NO'} |"
        )
        det = [f"### `{rel}`", ""]
        det.append(f"- Output pages: {', '.join('`' + p.key + '`' for p in doc_pages)}")
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
    out += ["Explained differences are only: heading numbers removed, headings that became a page title moved "
            "to the front matter, `table-scroller` wrapper tags removed, `br` tokens from `<br>` line breaks inside "
            "converted table cells, and the `[[replace]]` rewordings in `structure.toml`.", ""]
    out += ["## Coverage", "",
            "Every non-blank line of the normalised sources must land on exactly one page. "
            "A line that is missing or placed twice is listed under Problems.", ""]
    out += ["## Output pages", "", "| Page | Words (body) | Sources |", "| --- | ---: | --- |"]
    for pg in pages:
        n = sum(sum(words("\n".join(t for t, _ in p.lines)).values()) for p in pg.pieces if not p.is_text)
        srcs = ", ".join(f"`{p.doc.name}{'#' + p.anchor_heading['pid'] if p.anchor_heading else ''}`"
                         for p in pg.pieces if not p.is_text)
        state = " (manual)" if pg.manual else ""
        out.append(f"| `{pg.key}`{state} | {n} | {srcs} |")
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
