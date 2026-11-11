---
title: Drafts Stay Private
slug: drafts-stay-private
status: published
description: Draft content is never publicly visible.
chips:
  - Memory
  - CMS
created: 2026-11-09T21:04:27Z
updated: 2026-11-09T21:04:27Z
---

## Memory

Content marked as "draft" status in the CMS must never appear in public views (article lists, search results, RSS feeds, sitemaps).

## Rules

**Filtering**: All public queries filter `WHERE status = 'published'`.

**Routes**: Draft articles are only accessible via authenticated admin routes (e.g., `/admin/articles/draft/:slug`).

**Search**: Drafts excluded from site search and external search engine indexing.

**RSS/Sitemap**: Drafts never appear in RSS feeds or XML sitemaps.

**Previews**: Authenticated users can preview drafts via secure token links (e.g., `/preview/:token`).

## CMS Implementation

```js
// Public article list query
const articles = await db.articles.findMany({
  where: { status: 'published' },
  orderBy: { publishedAt: 'desc' }
});

// Admin draft access
if (user.isAdmin) {
  const drafts = await db.articles.findMany({
    where: { status: 'draft' },
    orderBy: { updatedAt: 'desc' }
  });
}
```

## Status Values

- `draft`: Work in progress, private
- `published`: Live on site, publicly visible
- `archived`: Removed from public lists but URL still accessible

## Related

See `intelligence/tools/cms.md` for full CMS specification.
