---
title: Screenshot Review
slug: screenshot-review
status: published
description: Visual regression testing and comparison workflow.
chips:
  - Skill
  - Testing
created: 2026-11-09T21:04:27Z
updated: 2026-11-09T21:04:27Z
---

Procedure for capturing, comparing, and reviewing screenshots for visual regression testing and design QA.

## Steps

**1. Capture Baseline**:
- Use headless browser (Puppeteer or Playwright)
- Capture at standard viewports: 390px (mobile), 1440px (desktop)
- Save as PNG with descriptive filenames (`home-1440.png`, `article-390.png`)
- Store in `/screenshots/baseline/`

**2. Capture Test**:
- After code changes, capture same views at same viewports
- Save to `/screenshots/test/`

**3. Generate Diff**:
- Use image diff tool (pixelmatch, looks-same, or Playwright diff)
- Generate diff image highlighting changed pixels
- Save to `/screenshots/diff/`

**4. Review**:
- Load baseline, test, and diff side-by-side
- Identify intentional vs unintentional changes
- Approve or reject test screenshots

**5. Update Baseline**:
- If changes are intentional and approved, replace baseline with test
- Commit new baseline to version control

## Tooling

**Puppeteer Example**:
```js
const browser = await puppeteer.launch({ headless: true });
const page = await browser.newPage();
await page.setViewport({ width: 1440, height: 900 });
await page.goto('https://saleh.digital');
await page.screenshot({ path: 'screenshots/baseline/home-1440.png' });
```

**Pixelmatch Diff**:
```js
const diff = pixelmatch(img1.data, img2.data, diff.data, width, height, { threshold: 0.1 });
```

## Thresholds

- `threshold`: 0.1 (tolerate minor anti-aliasing differences)
- `diffPixels`: < 0.5% of total pixels = pass

## Related

See `tools/debug-panel.md` for runtime visual inspection.
