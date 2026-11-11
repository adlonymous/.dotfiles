---
title: Contact
slug: contact
status: published
description: "Retired 2026-11-11 (its links moved to Welcome). Was: one line of the serif body; the sub-nav lists the ways to reach Ahmed (Email, Book a meeting, X/Twitter, LinkedIn, Company website), each going straight out."
chips:
  - Template
  - Contact
created: 2026-11-11T16:10:00Z
updated: 2026-11-11T16:10:14Z
---

**Retired on 2026-11-11.** The Contact page is gone from the live site: `#/contact` and `#/connect` now land on [Welcome](welcome.md), whose sub-nav carries the same links (Email, Book a meeting, X/Twitter, LinkedIn; the Company website row was dropped). The rest of this record describes the page as it was on the morning of 2026-11-11, kept for reference.

Route: `#/contact` (`#/connect` also works). It is an app page (`CONNECT` in `js/settings.js`), drawn in the same three columns.

The menu at every page (live, 2026-11-11): **Articles, Lectures, Speaking, Experiments, Library, Coffee table**, a paragraph step, then **Contact, Settings**. There is one menu entry per CMS section (`js/rooms.js`, `GROUPED = null`). Contact and Settings are app pages, not CMS sections.

- **Sub-nav:** the ways to reach Ahmed: **Email, Book a meeting, X/Twitter, LinkedIn, Company website**. Each goes straight out: email is a `mailto:` built from `CONTACT_EMAIL`, the meeting uses the CMS booking link (`BOOKING_URL`), and external links open in a new tab. A link whose address is still empty shows the row but leads back to `#/contact`.
- **Body:** one line, `p.set-lede` in the serif 16/20.8, max 540px: "Email for anything. A meeting for a proper conversation. The rest to follow along."
- **Actions row:** hidden.
- The page streams in like a post.

```html
<article id="article" class="is-settings" data-morph-lines="body" tabindex="-1">
  <h1 class="sr-only">Contact, Contact</h1>
  <div class="settings settings-connect">
    <p class="set-lede">Email for anything. A meeting for a proper conversation. The rest to follow along.</p>
  </div>
</article>
```

Source: `site/js/settings.js` as it was before the 2026-11-11 sync (now see [welcome](welcome.md)), lines 22 to 37

```js
// Contact: its own page in the menu (it was Book a call, then Connect; Ahmed, Nov 9). #/connect still opens it. Its sub-menu is the
// ways to reach Ahmed, each going straight out. An address left '' shows the row but
// leads back to Connect until it is set here.
export const CONNECT_LINKS = [
  { slug: 'email', title: 'Email', href: '' },            // mailto:…
  { slug: 'meeting', title: 'Book a meeting', href: '' }, // empty: the CMS booking link (BOOKING_URL)
  { slug: 'x', title: 'X/Twitter', href: '' },            // https://x.com/…
  { slug: 'linkedin', title: 'LinkedIn', href: '' },      // https://www.linkedin.com/in/…
  { slug: 'company', title: 'Company website', href: '' },
];
export const CONNECT = { slug: 'contact', title: 'Contact', id: 'connect', kind: 'section', app: true, links: true, items: [] };
CONNECT.items = [{ slug: 'all', title: 'Contact', id: 'connect/all', kind: 'item', section: CONNECT, paras: [], body: [], discuss: 0 }];
export const connectLinks = (bookingUrl = '') => CONNECT_LINKS.map(l => {
  const href = l.href || (l.slug === 'meeting' ? bookingUrl : l.slug === 'email' && CONTACT_EMAIL ? `mailto:${CONTACT_EMAIL}` : '');
  return { ...l, href: href || '#/contact', out: !!href && !href.startsWith('mailto:'), id: `connect/${l.slug}` };
```
