# Apex Utility - Code Structure Guide

This document explains what changed in this refactor, why, and how to
keep working with the site day to day. The original site (14 hand-written
HTML pages, each with its own copy of the header/footer and inline
`<style>`/`<script>` blocks) has been split into shared, reusable pieces
plus a tiny build step, with **no visual/UI changes** other than the
three unavoidable content unifications documented at the bottom of this
file.

## What changed

| Before | After |
|---|---|
| Header + footer duplicated in all 14 `.html` files | One `src/partials/header.html` and one `src/partials/footer.html` |
| Inline `<style>` block (AOS animation CSS) in every page's `<head>` | Merged into `assets/css/style.css` |
| Inline `<script>tailwind.config=...</script>` in every page | `assets/js/tailwind-config.js` |
| Inline `<script>` (AOS init) at the bottom of every page | `assets/js/aos-init.js` |
| Minified, single-line `main.js` | Reformatted with comments, same logic |
| No build step | `build.py` (pure Python, no dependencies) |

The **rendered result is pixel-identical** to before - this was verified
by parsing every original and every rebuilt page and comparing every
HTML tag, attribute, and piece of visible text. Nothing moved, resized,
recolored, or reflowed.

## Folder layout

```
Apex_utility/
├── build.py                    <- run this after editing partials/pages
├── STRUCTURE.md                <- this file
├── README.txt                  <- original project README (untouched)
├── index.html, about.html, ... <- GENERATED final pages (do not hand-edit)
├── services/*.html             <- GENERATED final pages (do not hand-edit)
├── assets/
│   ├── css/style.css           <- all shared styles (Tailwind extras + AOS)
│   ├── js/
│   │   ├── tailwind-config.js  <- Tailwind brand colors/fonts
│   │   ├── main.js             <- nav, mobile menu, FAQ, counters, contact form
│   │   └── aos-init.js         <- scroll-reveal animation logic
│   └── img/...                 <- unchanged
└── src/
    ├── partials/
    │   ├── header.html         <- EDIT THIS to change the header everywhere
    │   └── footer.html         <- EDIT THIS to change the footer everywhere
    └── pages/
        ├── index.html          <- unique content of the home page
        ├── about.html
        ├── ...
        └── services/*.html
```

## How to make a change

**To change the header or footer (nav links, logo, contact details, social
links, columns, anything):**
1. Edit `src/partials/header.html` or `src/partials/footer.html` once.
2. Run:
   ```
   python3 build.py
   ```
3. All 14 pages are regenerated instantly with the change applied.

**To change the unique content of one page** (e.g. the hero text on the
home page, a service's description): edit that page's file under
`src/pages/`, then run `python3 build.py` again.

**Do not hand-edit** the top-level `index.html`, `about.html`,
`services/boilers.html`, etc. - they are generated output and any edits
made directly there will be overwritten the next time `build.py` runs.

## Why a build step instead of live `<head>`/JS includes?

A common alternative is a small JavaScript snippet that does
`fetch('header.html')` and injects it into the page at runtime. That
was deliberately **not** used here, because it breaks when a page is
opened directly from a folder (`file://...`) - browsers block `fetch()`
across `file://` origins, so the header/footer would simply not appear
for anyone previewing the site locally by double-clicking `index.html`,
which the original README specifically calls out as a supported
workflow. The `build.py` approach keeps every deployed page as plain,
dependency-free static HTML (works from a double-click, works on
Netlify/Vercel/GitHub Pages, adds zero runtime cost) while still giving
you exactly one file to edit for the header and one for the footer.

## The only 3 content differences from the original site

Because a single shared header/footer can only contain one version of
each line of text, three **pre-existing inconsistencies between pages
in the original site** had to be resolved one way. In every case the
version used everywhere below is the one that already appeared on the
other 10+ pages (i.e., the outlier page was already inconsistent with
the rest of the site before this refactor):

1. **Header mobile-menu label for the chemicals service** - `services.html`
   alone said "Utility Chemicals & Material Supply"; the other 13 pages
   said "Industrial Chemicals". All pages now say "Industrial Chemicals".
2. **Footer address, missing space before comma** - 3 of the 6 service
   detail pages had "Vadodara ,India" (space before the comma); the
   other 11 pages had "Vadodara, India". All pages now use "Vadodara,
   India".
3. **Footer tagline on the Industrial Chemicals service page** - that
   one page had a custom sentence about chemicals in its footer, while
   every other page (including the other 5 service pages) used the
   standard "...your trusted engineering partner for boilers, water
   treatment, cooling towers, air compressors, industrial chemicals and
   plant utility consultancy." sentence. All pages now use the standard
   sentence, since a single shared footer cannot show two different
   sentences on different pages.

If you'd like any of these three reverted to their original, page-specific
wording, that's easy to do - just say which one and it can special-cased
in `build.py`.

## Changelog - navbar, mobile, and formatting pass

**1. Fixed: full nav required a hamburger click even on laptop screens.**
`src/partials/header.html` switched from the hamburger menu to the full
desktop nav at Tailwind's `xl` breakpoint (1280px). Many real laptops
render narrower than that once you account for browser chrome, side
panels, OS scaling, or simply not running the browser maximized, so the
hamburger was showing up on screens that should have gotten the full
nav. Changed to the `lg` breakpoint (1024px) - a standard "tablet
landscape and up" cutoff - in both the header partial and its CSS
fallback in `assets/css/style.css`.

**2. Fixed: open mobile menu could run off the bottom of short screens.**
The header (and the mobile menu inside it) is `position:fixed`, and the
menu had no scroll of its own. On short viewports - landscape phones,
small tablets, or a phone with the keyboard open - the last few links
(including the "Get a Quote" button) could end up below the visible
screen with no way to reach them. `#mob-menu.open` now caps its height to
the space below the header and scrolls internally instead
(`assets/css/style.css`).

**3. Accessibility: Services dropdown now also opens on keyboard focus**
(`:focus-within`), not only on mouse hover, so keyboard/tab users on a
desktop-width screen aren't stuck with an unreachable submenu.

**4. Safety net: `overflow-x:hidden` added to `html`/`body`** so nothing
can ever force an accidental horizontal scrollbar on mobile.

**5. Removed a stray `</style>` line** that had been left inside
`assets/css/style.css` (a leftover from when this CSS used to live in an
inline `<style>` block on every page - invalid in a standalone `.css`
file, though harmless since browsers just ignore it).

**6. Reformatted every file for readability.** `src/partials/header.html`,
`src/partials/footer.html`, all 14 files under `src/pages/`, and
`assets/css/style.css` were pretty-printed with proper nesting and
indentation - see "How the reformatting was done safely" below. `build.py`
then regenerated all 14 deployed pages from the cleaned-up sources, so
the indentation improvement is present everywhere, not just in `src/`.

None of the above changed any visible text, image, link, or color -
every page's content was diffed against the pre-fix version with all
whitespace stripped out, and the two matched exactly.

## How the reformatting was done safely

This project mixes tightly-packed inline HTML (an icon glued directly to
the word next to it, links used inline in running text) with Tailwind
flex/grid layouts. A generic "HTML beautifier" re-flows whitespace
everywhere, which can quietly inject a visible space into the page
wherever two inline elements previously had zero characters between
them (browsers collapse a *run* of whitespace into one rendered space,
but zero characters is not a whitespace run, so turning "nothing" into
"newline + indent" isn't always safe).

Two small custom scripts were used instead (kept in this delivery for
transparency, not needed for day-to-day editing):

- A line break/indent is only inserted where it's provably invisible to
  the rendered page: where the source already had whitespace there, where
  both neighbouring tags are unambiguous block-level elements (`div`,
  `section`, `li`, headings, etc.), or where the shared parent element
  carries a `flex`/`grid` class - the CSS spec guarantees whitespace-only
  text inside a flex/grid container is never rendered.
- Every file was verified with a round-trip check: strip all whitespace
  from the original and the reformatted version and require them to be
  byte-for-byte identical. Nothing was reworded, reordered, added, or
  removed - only whitespace changed.

## Note on a previously-flagged issue

An earlier pass of this document flagged some `<img>` tags using
Windows-style backslash paths (`assets\img\...`) instead of forward
slashes. That issue is **not present in this codebase** - checked
across every page, source and built - so no action was needed here.
