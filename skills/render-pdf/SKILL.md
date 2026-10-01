---
name: render-pdf
description: Render Markdown or Mermaid files to a clean PDF (tables fit the page, code wraps, no mid-word breaks) using pandoc + print CSS + headless Chrome. Use whenever the user asks to make/render/export a PDF from a .md or .mmd file, or complains a generated PDF has cut-off tables or broken code spans.
---

# Render PDF (Markdown / Mermaid)

Recipe validated 2026-07-11 on macOS (user confirmed the output is exactly what they want).
Never ship a PDF from bare `pandoc -o x.pdf` or unstyled HTML — tables overflow the page
edge and inline code breaks at underscores.

## Markdown → PDF

1. Write `print.css` to the scratchpad (verbatim below — this exact stylesheet is the approved look):

```css
body { font-family: -apple-system, "Helvetica Neue", Arial, sans-serif; font-size: 12px; line-height: 1.5; margin: 28px 34px; color: #111; }
h1 { font-size: 1.7em; } h2 { font-size: 1.3em; border-bottom: 1px solid #ccc; padding-bottom: 3px; } h3 { font-size: 1.1em; }
code { font-family: Menlo, Consolas, monospace; font-size: 0.88em; background: #f2f2f2; padding: 0 2px; white-space: nowrap; }
pre { background: #f6f8fa; border: 1px solid #ddd; padding: 8px 10px; font-size: 0.82em; white-space: pre-wrap; overflow-wrap: break-word; }
pre code { background: none; padding: 0; white-space: pre-wrap; }
table { border-collapse: collapse; width: 100%; table-layout: fixed; font-size: 0.92em; }
th, td { border: 1px solid #aaa; padding: 5px 7px; text-align: left; vertical-align: top; overflow-wrap: break-word; }
th { background: #ececec; }
td code, th code { white-space: normal; overflow-wrap: anywhere; }
h1, h2, h3 { page-break-after: avoid; }
table, pre, tr { page-break-inside: avoid; }
blockquote { border-left: 3px solid #bbb; margin-left: 0; padding-left: 12px; color: #444; }
```

2. Build styled HTML, then print with headless Chrome:

```bash
pandoc -s --metadata title="<Title>" --css print.css --embed-resources input.md -o tmp.html
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless --disable-gpu \
  --no-pdf-header-footer --print-to-pdf=output.pdf "file://$PWD/tmp.html"
```

3. **Verify before delivering** — take a page-width screenshot and Read it; check tables
   fit and nothing is cut off at the right edge:

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless --disable-gpu \
  --screenshot=preview.png --window-size=790,4400 "file://$PWD/tmp.html"
```

Also sanity-check the file: `file output.pdf` (must say "PDF document" with a page count).

## Mermaid (.mmd) → PDF

Use mermaid-cli with the installed Chrome (skip puppeteer's browser download); `-f` fits
the page to the diagram:

```bash
export PUPPETEER_SKIP_DOWNLOAD=1 PUPPETEER_EXECUTABLE_PATH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
npx -y @mermaid-js/mermaid-cli -i diagram.mmd -o diagram.pdf -f
```

## Notes

- Keep temp files (`tmp.html`, `print.css`, `preview.png`) in the scratchpad, not next to
  the deliverable — the user wants only the requested files in the destination folder.
- pdflatex/wkhtmltopdf/weasyprint are NOT installed on this Mac; don't try `pandoc -o x.pdf` directly.
- Remote boxes generally lack pandoc — render locally, then `scp` the PDF over.
