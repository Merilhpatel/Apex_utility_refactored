# Apex Utility

Multi-page marketing site for Apex Industrial Utility Consultancy and Services — boilers, water treatment, cooling towers, air compressors, industrial chemicals, and utility consultancy.

**Live:** https://apex-utility-refactored.vercel.app

---

## Structure

```
├── src/
│   ├── partials/        # shared header.html & footer.html
│   └── pages/           # source content for every page
├── build.py             # stitches partials + pages → final static HTML
├── assets/
│   ├── css/style.css
│   ├── js/main.js
│   └── img/
├── index.html            ┐
├── about.html             │
├── services.html          │  generated output — do not edit directly,
├── products.html          │  edit the matching file in src/pages/ instead
├── industries.html        │
├── projects.html          │
├── why-us.html            │
├── contact.html           ┘
└── services/
    ├── boilers.html
    ├── water-treatment.html
    ├── industrial-chemicals.html
    ├── cooling-towers.html
    ├── air-compressors.html
    └── utility-consultancy.html
```

The root-level and `services/` HTML files are **generated**. Content lives in `src/pages/` and `src/partials/`; running the build writes the final pages back out to the root.

## Editing content

1. Edit the relevant file in `src/pages/` (or `src/partials/` for the shared header/footer).
2. Regenerate the site:
   ```bash
   python3 build.py
   ```
3. Preview by opening `index.html` directly in a browser — no server or build tools required.

## Deploying

No build step is needed at deploy time; the repo already contains the generated static output.

- **Vercel / Netlify:** drag and drop the folder, or connect the repo — deploys as-is.
- **GitHub Pages:** push to the repo and enable Pages on `main`.
- **Any static host (cPanel, Hostinger, etc.):** upload everything to `public_html/`.

## Contact form

`contact.html` doesn't use a backend — it opens WhatsApp with the visitor's Name / Company / Email / Phone / Message pre-filled. The number is set in `assets/js/main.js` and reused across the site.

## Known issues

- A few images in `services/` are missing the `../` prefix on their path (they were written as if the page lived at the site root), and `air-compressors.html` additionally references a filename that doesn't match the file on disk. Fix in `src/pages/services/`, then rerun `build.py`.
- Several image files use spaces in their names (`boiler cover.jpg`, etc.). This works on Vercel but is fragile on stricter hosts — recommend renaming to hyphenated filenames.
- `products.html` / `projects.html` currently hotlink images from Unsplash rather than `assets/img/`. Fine for a prototype; swap in your own hosted photos before going fully live.

## Brand

| | |
|---|---|
| Primary Navy | `#0B1F3A` |
| Brand Blue | `#1476FF` |
| Accent Sky | `#1E90FF` |
| Background Ice | `#EEF4FB` |

---
© 2026 Apex Industrial Utility Consultancy and Services
