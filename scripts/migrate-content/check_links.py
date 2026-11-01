#!/usr/bin/env python3
"""Check internal links and images in the built site (run `pnpm build` first).

starlight-links-validator skips relative links, and the converted pages use
relative links on purpose (root-relative links break under the base path), so
this script resolves every internal href and image src in the docs pages
against dist/ and verifies that the target file and the #fragment exist.
"""

import argparse
import posixpath
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

PROJECT = Path(__file__).resolve().parent.parent.parent


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids, self.links, self.images = set(), [], []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            self.ids.add(a["id"])
        if tag == "a" and "href" in a:
            self.links.append(a["href"])
        if tag == "img" and "src" in a:
            self.images.append(a["src"])


def parse(path, cache):
    if path not in cache:
        p = Page()
        p.feed(path.read_text(encoding="utf8"))
        cache[path] = p
    return cache[path]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dist", type=Path, default=PROJECT / "dist")
    ap.add_argument("--base", default="/thymeleaf-new-docs")
    ap.add_argument("--scope", nargs="*", default=["docs"],
                    help="page folders (below dist) whose links are checked")
    args = ap.parse_args()
    dist, base = args.dist.resolve(), args.base.rstrip("/")
    cache, checked, bad = {}, 0, []

    def to_file(url_path):
        rel = url_path[len(base):].lstrip("/") if base and url_path.startswith(base) else None
        if rel is None:
            return None
        f = dist / rel
        if f.is_dir():
            f = f / "index.html"
        return f

    for scope in args.scope:
        for page_file in sorted((dist / scope).rglob("index.html")):
            page_url = base + "/" + page_file.parent.relative_to(dist).as_posix() + "/"
            page = parse(page_file, cache)
            for kind, refs in (("link", page.links), ("image", page.images)):
                for href in refs:
                    u = urlsplit(href)
                    if u.scheme or u.netloc:
                        continue  # external
                    checked += 1
                    if href.startswith("/") and not href.startswith(base + "/"):
                        bad.append(f"{page_url}: root-relative {kind} outside base path: {href}")
                        continue
                    target = posixpath.normpath(posixpath.join(page_url, unquote(u.path))) if u.path else page_url
                    if u.path.endswith("/"):
                        target += "/"
                    f = to_file(target)
                    if f is None or not f.is_file():
                        bad.append(f"{page_url}: {kind} target missing: {href} -> {target}")
                        continue
                    if u.fragment and kind == "link":
                        if unquote(u.fragment) not in parse(f, cache).ids:
                            bad.append(f"{page_url}: anchor missing: {href}")
    print(f"Checked {checked} internal links/images in {', '.join(args.scope)}")
    for b in bad:
        print("BROKEN:", b)
    print("OK" if not bad else f"{len(bad)} problem(s)")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
