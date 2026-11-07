---
name: create-pdf
description: Create new PDF documents, reports, proposals, invoices, handouts, and printable layouts using the local PDF Workshop project with React, pdfcn, and Forme. Use when the user asks to create, generate, design, or export a PDF. Not for editing, merging, or extracting existing PDFs.
compatibility: This PC has __DOTFILES_HOME__/Projects/Aadil/pdf-workshop, Node.js 22+, npm, and Poppler tools. Rendering is local; installing new dependencies requires network access.
---

# Create PDF documents

Use the reusable workspace at `__DOTFILES_HOME__/Projects/Aadil/pdf-workshop`. Read its `AGENTS.md` and `README.md` before changing anything. If this path is unavailable, say so rather than creating a second workspace silently.

## Workflow

1. Establish the content, audience, page size, and desired style. Ask about missing information only when it materially changes the document. Never invent financial, legal, personal, or business details; label demonstration data as synthetic.
2. Inspect existing documents and outputs. Create a descriptive new template in `documents/`; don't replace previous work or PDFs without permission. Use `documents/sample.tsx` as the verified starting point.
3. Compose React document elements with `Document`, `Page`, and layout primitives from `@formepdf/react`, plus pdfcn's Forme components in `components/pdf/`. Use `PdfcnThemeProvider` around the document. Check installed types before relying on renderer props or styles.
4. Add a needed component through the configured registry, for example `npx shadcn@latest add @pdfcn/forme/data-table`. Verify its docs and inspect changes. Do not mix Takumi components into the Forme document. Only text, heading, divider, and shared theme helpers are installed initially.
5. Run from the workspace:

   ```bash
   script/pdf documents/my-report.tsx -o output/my-report.pdf
   script/check
   pdfinfo output/my-report.pdf
   pdftotext -layout output/my-report.pdf -
   pdftoppm -scale-to 1600 -png output/my-report.pdf output/my-report-page
   ```

6. Inspect every generated page image with the image-capable read tool. Verify page count and size, required text, typography, clipping, page breaks, tables, and whitespace. The sample smoke test alone does not validate a new document. Adjust the document, render again, and rerun checks until it looks correct.
7. Deliver the absolute PDF path and, when useful, preview paths. State any remaining limitations. Keep generated artifacts in ignored `output/`; user-requested destinations may be used with permission. Rendering does not require API keys or a cloud service.

## Preview and remote use

- `script/preview documents/my-report.tsx` starts Forme's live browser preview on port 4242 by default. Do not leave a background server running unless requested.
- The user may be on a Mac connected to this PC through Herdr. A PC-local path is not a Mac-local file. Do not launch a PC desktop viewer and claim the user can see it on the Mac.
- Herdr supports Kitty image graphics, so a compatible terminal viewer may display rendered page PNGs. Verify the viewer and client support before promising an inline preview. Herdr has no embedded webview; a browser preview needs the Mac's browser and an SSH tunnel or another explicitly authorized connection.
- Do not expose the preview server publicly or install remote desktop software for PDF creation.

## References

- pdfcn: https://github.com/shadcn-labs/pdfcn
- Component discovery: https://pdfcn.vercel.app/llms.txt
- Forme: https://docs.formepdf.com/
