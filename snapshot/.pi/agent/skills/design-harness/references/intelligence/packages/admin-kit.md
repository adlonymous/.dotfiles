---
title: Admin Kit
slug: admin-kit
status: published
description: Internal admin interface components and utilities.
chips:
  - Package
  - Admin
created: 2026-11-09T21:04:27Z
updated: 2026-11-09T21:04:27Z
---

Internal admin interface package for authenticated CMS operations, settings management, and debug tools.

## Components

**Auth Guard**: Check user authentication before rendering admin routes.

**CMS Editor**: Rich text editor for article/experiment body content (likely TipTap-based, see `tiptap.md`).

**Settings Panel**: UI for managing site-wide settings (themes, feature flags, sliders).

**Debug Tools**: Access to debug panel, shader benches, performance metrics.

## Utilities

**API Client**: Authenticated fetch wrapper for CMS API calls.

**Toast Notifications**: Success/error feedback for admin actions.

**Form Validation**: Validate CMS record input before save.

## Styling

Admin interface uses same design tokens as public site but may include additional admin-only components (data tables, code editors).

## Access Control

Only accessible to authenticated owner account. No team/multi-user support currently.

## Usage

Admin routes: `/admin/*`
- `/admin/articles` -- list and edit articles
- `/admin/tools` -- access debug panel, shader benches
- `/admin/settings` -- adjust foundation sliders, themes, feature flags

## Related

See `tools/cms.md` for CMS API and `skills/cms-records.md` for record management workflow.
