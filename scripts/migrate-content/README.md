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

- Converts 3 tutorials (one page per top-level chapter plus an `index.md`) and 10
  articles. The file list is in `migrate.py` (`TUTORIALS`, `ARTICLES`).
- Setext headings become ATX, heading numbers are stripped, tutorial H1 chapters
  become the page title, `@documentVersion@` / `@projectVersion@` are resolved from
  `build.gradle`.
- Pandoc simple tables become GFM tables, `table-scroller` wrapper divs are
  removed, a Pandoc inline footnote becomes a GFM footnote.
- Links between converted documents (absolute thymeleaf.org URLs, relative and
  in-document anchors) are mapped to the new page and heading anchor with relative
  URLs. Other thymeleaf.org links become absolute `https://www.thymeleaf.org/...`.
- Images are copied next to the pages and referenced relatively.
- Every page gets a CC BY-SA 3.0 source note linking the original page.
- Writes `report.md` (word and code block comparison per source). Exit code is
  non-zero if anything is unexplained or a link cannot be resolved.

## Output (overwritten on every run)

`src/content/docs/docs/tutorials/{using-thymeleaf,thymeleaf-spring,extending-thymeleaf}/`
and `src/content/docs/docs/articles/`. These folders are deleted and regenerated, so
do not edit files there by hand. The output is deterministic: rerunning produces
identical files.

## Why check_links.py

`starlight-links-validator` reports every relative link as an error, and skips
them when `errorOnRelativeLinks` is `false`. The converted pages use relative links
on purpose (root-relative links break under the `/thymeleaf-new-docs` base path),
so `check_links.py` checks them against the built HTML instead.
