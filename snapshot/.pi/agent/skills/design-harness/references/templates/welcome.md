---
title: Welcome
slug: welcome
status: published
description: "The front door (#/welcome, and /): one serif paragraph introducing Ahmed, with the ways to reach him (Email, Book a meeting, X/Twitter, LinkedIn) as its sub-nav. Replaces the Contact page."
chips:
  - Template
  - Welcome
  - Contact
created: 2026-11-11T16:33:12Z
updated: 2026-11-11T16:33:12Z
---

Route: `#/welcome`, and the site's front door: `https://saleh.digital/` opens it (canonical `https://saleh.digital/`, `<title>` "Welcome, Ahmed Saleh" once the app has run; the static `<title>` is "Ahmed Saleh"). Checked live on 2026-11-11 after the site sync that day. `#/contact` and `#/connect` also land here.

- **Menu:** Welcome is the first room and is active (`aria-current="page"`).
- **Sub-nav (column 2):** the ways to reach Ahmed, `CONNECT` links from `js/settings.js` (`connectLinks()`): **Email** (`mailto:`), **Book a meeting** (cal.com, new tab), **X/Twitter** (new tab), **LinkedIn** (new tab). External links get `target="_blank" rel="noopener"` and an aria-label ending "(opens in a new tab)". They are the rows of the old Contact page, which is gone.
- **Body:** a `<h1 class="sr-only">Welcome</h1>` and one paragraph of the serif body (the post reading size: 18/28.8, tracking −0.2px, in the 640px column), streamed in like a post. The live text introduces Ahmed: his name, his current company (named on the live page; written "[company]" here) in Toronto, and his past roles (product designer at Roblox, Guilded and Dot Health; lead UX and product design instructor at General Assembly).
- **Actions row:** none (`#discuss` hidden).

Live DOM (2026-11-11; the email address and the company name are left out):

```html
<nav class="col col-sub" aria-label="In this section"><ul id="sub" aria-label="Welcome">
  <li><a class="item" data-morph="sub-connect-email" data-node="connect/email" href="mailto:…">Email</a></li>
  <li><a class="item" data-morph="sub-connect-meeting" data-node="connect/meeting" href="https://cal.com/ahmed-saleh/30min" target="_blank" rel="noopener" aria-label="Book a meeting (opens in a new tab)">Book a meeting</a></li>
  <li><a class="item" data-morph="sub-connect-x" data-node="connect/x" href="https://x.com/saleh_digital" target="_blank" rel="noopener" aria-label="X/Twitter (opens in a new tab)">X/Twitter</a></li>
  <li><a class="item" data-morph="sub-connect-linkedin" data-node="connect/linkedin" href="https://www.linkedin.com/in/saleh-ahmed/" target="_blank" rel="noopener" aria-label="LinkedIn (opens in a new tab)">LinkedIn</a></li>
</ul></nav>
<article id="article" data-morph-lines="body" tabindex="-1">
  <h1 class="sr-only">Welcome</h1>
  <p>My name is Ahmed Saleh. I'm currently the co-founder and CEO of [company], … based in Toronto. Previously, I was a product designer at Roblox, Guilded and Dot Health and a lead UX + product design instructor at General Assembly.</p>
</article>
```

The links come from `js/settings.js` (the contact address is replaced by `mailto:…` here; everything else is verbatim):

Source: `site/js/settings.js`, lines 30 to 45

```js
// The ways to reach Ahmed: Welcome's sub-menu (Ahmed, Nov 11; they were the Contact page, now gone). #/contact and #/connect land on Welcome. Its sub-menu is the
// ways to reach Ahmed, each going straight out. An address left '' shows the row but
// leads back to Connect until it is set here.
export const CONNECT_LINKS = [
  { slug: 'email', title: 'Email', href: 'mailto:…' },
  { slug: 'meeting', title: 'Book a meeting', href: '' }, // empty: the CMS booking link (BOOKING_URL)
  { slug: 'x', title: 'X/Twitter', href: 'https://x.com/saleh_digital' },
  { slug: 'linkedin', title: 'LinkedIn', href: 'https://www.linkedin.com/in/saleh-ahmed/' },
];
export const CONNECT = { slug: 'contact', title: 'Contact', id: 'connect', kind: 'section', app: true, links: true, items: [] };
CONNECT.items = [{ slug: 'all', title: 'Contact', id: 'connect/all', kind: 'item', section: CONNECT, paras: [], body: [], discuss: 0 }];
export const connectLinks = (bookingUrl = '') => CONNECT_LINKS.map(l => {
  const href = l.href || (l.slug === 'meeting' ? bookingUrl : l.slug === 'email' && CONTACT_EMAIL ? `mailto:${CONTACT_EMAIL}` : '');
  return { ...l, href: href || '#/welcome', out: !!href && !href.startsWith('mailto:'), id: `connect/${l.slug}` };
});
```
