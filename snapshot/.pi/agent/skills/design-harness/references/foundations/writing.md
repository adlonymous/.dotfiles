---
title: Writing
slug: writing
status: published
group: Foundations
order: 10
discuss: 0
created: 2026-11-09T19:23:22Z
updated: 2026-11-09T19:23:22Z
---

The writing voice is concise, technical, and first-person. Every word is chosen deliberately.

## Voice

**First-person, owner voice:**
- "I designed this"
- "my work"
- "the work I've been doing"

**Never third-person:**
- ❌ "Ahmed designed this"
- ❌ "his work"
- ❌ "the work he's been doing"

## Tone

**Concise and direct:**
- Short sentences
- Active voice
- No filler words
- Every word earns its place

**Technical but accessible:**
- Precise terminology
- Explain when needed
- Assume technical audience
- No hand-holding

**Confident, not boastful:**
- State facts plainly
- Let work speak for itself
- No superlatives
- No marketing speak

## Punctuation

**Em dashes: Never**
Use en dashes (–) or restructure the sentence. See `writing/no-em-dashes.md`.

**Colons: Sparingly**
Use when introducing a list or explanation. Prefer periods for full sentences.

**Semicolons: Rarely**
Prefer splitting into two sentences.

**Oxford comma: Yes**
"tokens, motion, and sound" not "tokens, motion and sound"

## Sentence Structure

**Short sentences:**
```
Good: "I designed this. It's live."
Bad:  "I designed this and it's live now."
```

**Active voice:**
```
Good: "I built the site."
Bad:  "The site was built by me."
```

**No passive constructions:**
```
Good: "The system handles this."
Bad:  "This is handled by the system."
```

## Capitalization

**Sentence case for headings:**
```
Good: "About the work"
Bad:  "About The Work"
```

**Product names as styled:**
- saleh.digital (lowercase)
- Marathon (capitalized)
- Inter Display, Shinka (proper case)

## Common Phrases

**Preferred:**
- "I'm working on"
- "the site"
- "this experiment"
- "the design system"

**Avoid:**
- "I'm currently working on" (drop "currently")
- "the website" (too formal)
- "this particular experiment" (drop "particular")
- "the comprehensive design system" (drop adjectives)

## Numbers

**Spell out one through nine:**
- "three experiments"
- "10 projects"

**Use numerals for measurements:**
- "16px"
- "0.5s"
- "24-bit"

**Use commas for thousands:**
- "1,000 lines"
- "10,000 users"

## Lists

**Use bulleted lists for:**
- Unordered items
- Features
- Examples

**Use numbered lists for:**
- Steps
- Procedures
- Ranked items

**Keep list items parallel:**
```
Good:
- Design the interface
- Build the prototype
- Test with users

Bad:
- Design the interface
- Building the prototype
- Users were tested
```

## Code & Technical Terms

**Inline code for:**
- Variable names: `--paper`
- File names: `tokens.css`
- Class names: `.item`
- Function names: `calculateOffset()`

**Code blocks for:**
- Multi-line code
- Complete examples
- Terminal commands

**Technical terms:**
- First use: explain briefly
- Subsequent uses: use freely
- Never patronize

## Links

**Link text should be descriptive:**
```
Good: "Read the design harness specification"
Bad:  "Click here to read more"
```

**No "click here":**
Always describe the destination.

## Arabic Text

**Inline Arabic:**
Use `lang="ar" dir="rtl"` attributes:
```html
Ahmed Saleh <span lang="ar" dir="rtl">أحمد صالح</span>
```

**Unicode isolation:**
```css
[lang="ar"] { unicode-bidi: isolate; }
```

## Editing Checklist

Before publishing:
- [ ] Remove filler words (just, really, very, actually)
- [ ] Convert passive to active voice
- [ ] Check for em dashes (use en dashes)
- [ ] Verify first-person voice throughout
- [ ] Remove adjectives that don't add meaning
- [ ] Break long sentences into short ones
- [ ] Ensure parallel structure in lists
- [ ] Check that every word earns its place

## Examples

**Good:**
> I designed the Marathon theme for high-contrast work. It uses neon accents and strong shadows. The system adapts to five accent colors.

**Bad:**
> The Marathon theme was carefully designed to provide a really high-contrast working environment. It utilizes vibrant neon accents and employs strong shadows to create depth. The innovative system can easily adapt to five different accent colors—lime, cyan, red, amber, and green.

**Analysis:**
- Passive voice removed
- "carefully", "really", "innovative", "easily" deleted
- Long sentences split
- Em dash removed
- First-person voice restored
