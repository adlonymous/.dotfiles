---
title: CMS
slug: cms
status: published
description: Content management system API.
chips:
  - Tool
  - CMS
created: 2026-11-09T21:04:27Z
updated: 2026-11-09T21:04:27Z
---

Content management system for creating, editing, and publishing articles, experiments, and library entries on Saleh Digital.

## API Endpoints

**List records**:
```
GET /api/cms/articles?status=published
GET /api/cms/experiments?status=draft
GET /api/cms/books
```

**Get record**:
```
GET /api/cms/articles/:slug
GET /api/cms/experiments/:id
GET /api/cms/books/:id
```

**Create record**:
```
POST /api/cms/articles
Body: { title, description, body, chips, status }
```

**Update record**:
```
PATCH /api/cms/articles/:id
Body: { title?, description?, body?, chips?, status? }
```

**Delete record**:
```
DELETE /api/cms/articles/:id
```

## Record Structure

See `skills/cms-records.md` for full record schema and validation rules.

## Authentication

CMS endpoints require authentication (owner account). Use session cookie or API key.

## Status Values

- `draft`: Private, work-in-progress
- `published`: Live on site
- `archived`: Removed from lists, URL still accessible

## Usage

Admin interface (`admin-kit.md`) or agent API calls:
```js
const article = await fetch('/api/cms/articles/my-slug').then(r => r.json());
```

## Related

See `skills/cms-records.md` for workflow and `packages/admin-kit.md` for admin UI.
