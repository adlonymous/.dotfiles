---
title: Open Library
slug: open-library
status: published
description: Public API for book metadata and covers.
chips:
  - Package
  - API
created: 2026-11-09T21:04:27Z
updated: 2026-11-09T21:04:27Z
---

Public API provided by Internet Archive's Open Library project. Used to fetch book metadata (title, author, ISBN, publish date, cover images) for the Library section.

## License

Open Library API is free to use. Data is available under Open Data Commons Open Database License (ODbL).

## Vendor

**Internet Archive / Open Library**
Website: https://openlibrary.org
API Docs: https://openlibrary.org/developers/api

## Endpoints

**Search books**:
```
GET https://openlibrary.org/search.json?q={query}
```

**Get book by ISBN**:
```
GET https://openlibrary.org/isbn/{isbn}.json
```

**Get cover image**:
```
GET https://covers.openlibrary.org/b/isbn/{isbn}-L.jpg
```

Cover sizes: `-S` (small), `-M` (medium), `-L` (large)

## Usage Example

```js
async function fetchBookByISBN(isbn) {
  const res = await fetch(`https://openlibrary.org/isbn/${isbn}.json`);
  const book = await res.json();
  return {
    title: book.title,
    author: book.authors?.map(a => a.name).join(', '),
    cover: `https://covers.openlibrary.org/b/isbn/${isbn}-L.jpg`
  };
}
```

## Rate Limiting

Open Library requests no aggressive scraping. Cache book data and covers locally after first fetch.

## Related

See `intelligence/agents/web.md` for research agent that uses this API to fetch book metadata.
