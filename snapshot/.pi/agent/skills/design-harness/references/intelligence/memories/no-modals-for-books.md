---
title: No Modals for Books
slug: no-modals-for-books
status: published
description: Library opens book details in-place, not in modals.
chips:
  - Memory
  - Library
  - UX
created: 2026-11-09T21:04:27Z
updated: 2026-11-09T21:04:27Z
---

## Memory

When a user clicks a book in the Library (bookshelf or coffee table), show the book details in-place in the main content area, not in a modal overlay or dialog.

## Rules

**No dialogs**: Do not use `<dialog>`, overlays, or lightbox-style modals for book details.

**In-place navigation**: Clicking a book transitions the main content area to show full book info (cover, title, author, description, reading status, notes).

**URL change**: Update the URL (e.g., `/library/book/:id`) so the detail view is linkable and bookmarkable.

**Back navigation**: Provide clear back button or breadcrumb to return to library list.

**View Transitions API**: Use native View Transitions (where supported) for smooth animated transition from grid to detail.

## Rationale

**Modals break flow**: Overlays interrupt the spatial model of the interface. The user loses context of where they were in the library.

**Reading is primary**: Book details are substantial content (cover, metadata, notes, reading progress). They deserve the full content area, not a cramped modal.

**Linkability**: Modal states can't be shared via URL. In-place views can be linked directly.

**Consistency**: Other detail views (articles, experiments) navigate in-place. Library should match.

## Implementation

```js
// On book click
function openBookDetail(bookId) {
  // Update URL
  history.pushState({ bookId }, '', `/library/book/${bookId}`);
  
  // Fetch book data
  const book = await fetchBook(bookId);
  
  // Render detail view in main content area
  renderBookDetail(book);
  
  // Use View Transition if supported
  if (document.startViewTransition) {
    document.startViewTransition(() => {
      renderBookDetail(book);
    });
  }
}
```

## Related

See `patterns/bookshelf.md` and `patterns/coffee-table.md` for library views.
