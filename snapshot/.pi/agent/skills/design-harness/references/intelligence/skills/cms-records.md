---
title: CMS Records
slug: cms-records
status: published
description: How to structure and manage content records in the CMS.
chips:
  - Skill
  - CMS
created: 2026-11-09T21:04:27Z
updated: 2026-11-09T21:04:27Z
---

Procedure for creating, updating, and publishing content records in Saleh Digital's CMS.

## Record Structure

```json
{
  "id": "uuid-v4",
  "type": "article | experiment | book | harness-record",
  "slug": "url-slug",
  "title": "Display Title",
  "description": "Brief summary (140–200 chars)",
  "body": "Full Markdown content",
  "status": "draft | published | archived",
  "chips": ["tag1", "tag2"],
  "publishedAt": "ISO 8601 datetime",
  "createdAt": "ISO 8601 datetime",
  "updatedAt": "ISO 8601 datetime"
}
```

## Workflow

**1. Create Draft**:
- Generate unique ID and slug
- Set status = `draft`
- Fill title, description, chips
- Draft body content in Markdown

**2. Edit and Preview**:
- Update body and metadata
- Preview in reading layout
- Check spelling, links, images

**3. Publish**:
- Review final content
- Set status = `published`
- Set publishedAt to current datetime
- Content becomes publicly visible

**4. Update Published**:
- Edit body or metadata as needed
- Update updatedAt timestamp
- Changes reflect immediately

**5. Archive**:
- Set status = `archived`
- Removed from public lists
- URL still accessible (for link preservation)

## Validation Rules

- `slug`: lowercase, hyphens only, unique per type
- `title`: 3–120 characters
- `description`: 20–200 characters recommended
- `body`: valid Markdown, images with alt text
- `chips`: 0–8 tags, each 1–20 characters

## Related

See `tools/cms.md` for CMS API and `memories/drafts-stay-private.md` for visibility rules.
