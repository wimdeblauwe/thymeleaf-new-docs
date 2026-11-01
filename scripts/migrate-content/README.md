# Content migration

Converts the English Thymeleaf 3.1 documentation from `thymeleaf-docs` (Pandoc
Markdown) into Starlight pages. Python 3 standard library only, no install step.

```sh
python3 scripts/migrate-content/migrate.py                      # default source: ../thymeleaf-docs
python3 scripts/migrate-content/migrate.py --source /path/to/thymeleaf-docs
pnpm build                                                      # Starlight build + starlight-links-validator
python3 scripts/migrate-content/check_links.py                  # resolves relative links/anchors/images in dist/
```

Options: `--source`, `--image-fallback` (a `thymeleaf.github.io/doc` checkout, used only
if an image is missing in the source), `--project`, `--report`.

## What it does

- Converts 3 tutorials and 10 articles. The file list is in `migrate.py` (`TUTORIALS`,
  `ARTICLES`).
- `structure.toml` maps source sections onto the pages of the docs navigation, including
  moves, splits and merges. Its header explains the format.
- Setext headings become ATX, heading numbers are stripped, `@documentVersion@` /
  `@projectVersion@` are resolved from `build.gradle`. A heading that becomes a page's
  title moves to the front matter, and the rest shift to fit.
- Pandoc simple tables become GFM tables, `table-scroller` wrapper divs are
  removed, a Pandoc inline footnote becomes a GFM footnote.
- Links between converted documents (absolute thymeleaf.org URLs, relative and
  in-document anchors) are mapped to the new page and heading anchor with relative
  URLs. Other thymeleaf.org links become absolute `https://www.thymeleaf.org/...`.
- Images are copied to `images/` and referenced relatively.
- Every page gets a CC BY-SA 3.0 source note linking the original URL and anchor of each
  of its sources. Named authors stay credited, at the top of a page or, on a merged page,
  at the start of their section.
- Writes `report.md`. Exit code is non-zero if a word or code block difference is
  unexplained, a link cannot be resolved, a source line is on no page or on several, or
  a `[[replace]]` rewording no longer matches.

## Output (overwritten on every run)

The folders named by `dir` in `structure.toml`, plus `images/`, below
`src/content/docs/docs/`. Their files are deleted and regenerated, so don't edit them by
hand. The output is deterministic: rerunning produces identical files.

## Editing a page by hand

Set `manual = true` on the page in `structure.toml` first. The script then keeps that
file, and `structure.toml` records that the page no longer follows upstream. Its pieces
stay listed, so the coverage check and links to its headings keep working. Rename a
heading only if you update links to it. The report marks these pages as manual.

## Why check_links.py

`starlight-links-validator` reports every relative link as an error, and skips
them when `errorOnRelativeLinks` is `false`. The converted pages use relative links
on purpose (root-relative links break under the `/thymeleaf-new-docs` base path),
so `check_links.py` checks them against the built HTML instead.
