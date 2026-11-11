---
title: TipTap
slug: tiptap
status: published
description: Headless rich-text editor framework.
chips:
  - Package
  - Editor
created: 2026-11-09T21:04:27Z
updated: 2026-11-09T21:04:27Z
---

Headless WYSIWYG editor built on ProseMirror. Used in the CMS for editing article/experiment body content.

## License

MIT License (open-source core). Pro features available with paid license (not required for basic usage).

## Vendor

**Tiptap GmbH**
Website: https://tiptap.dev
GitHub: https://github.com/ueberdosis/tiptap

## Installation

```bash
npm install @tiptap/core @tiptap/starter-kit @tiptap/react
```

## Extensions Used

- **StarterKit**: Basic formatting (bold, italic, headings, lists)
- **Link**: Hyperlink support
- **Image**: Inline images
- **CodeBlock**: Syntax-highlighted code blocks

## Configuration Example

```js
import { useEditor, EditorContent } from '@tiptap/react';
import StarterKit from '@tiptap/starter-kit';

const editor = useEditor({
  extensions: [StarterKit],
  content: '<p>Hello world</p>',
  onUpdate: ({ editor }) => {
    const html = editor.getHTML();
    saveContent(html);
  }
});

return <EditorContent editor={editor} />;
```

## Styling

TipTap is headless (no default styles). Apply Saleh Digital's typography tokens:

```css
.ProseMirror {
  font-family: var(--body);
  font-size: 17px;
  line-height: 28px;
  filter: url(#ink-body);
}

.ProseMirror h1 {
  font-size: 32px;
  line-height: 40px;
  font-weight: 600;
  letter-spacing: -1.28px;
}
```

## Output

TipTap outputs HTML. Sanitize on save and render to prevent XSS.

## Related

See `intelligence/packages/admin-kit.md` for CMS admin interface.
