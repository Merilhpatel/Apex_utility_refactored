#!/usr/bin/env python3
"""
build.py
========
Regenerates every public HTML page of the Apex Utility website from:

    src/partials/header.html   <- ONE shared header, used on every page
    src/partials/footer.html   <- ONE shared footer, used on every page
    src/pages/**.html          <- the unique content of each page

Run this after editing anything in src/partials/ or src/pages/:

    python3 build.py

It requires nothing but the Python 3 standard library - no Node, no
npm, no build tools to install. Output files are written to the
project root (index.html, about.html, services/boilers.html, etc.),
exactly where they need to be for the site to be deployed as-is to
Netlify / Vercel / GitHub Pages / any static host - or opened directly
in a browser.

WHY A BUILD STEP AT ALL?
-------------------------
This site has no server and no JavaScript framework, so there is no
way to literally reuse an HTML snippet across pages *at request time*.
The two realistic options are:
  (a) client-side `fetch()` of a header.html/footer.html at runtime, or
  (b) a tiny build script that stitches the pieces together once,
      ahead of time, producing plain static HTML.

Option (a) breaks when a page is opened directly from disk
(file:// - a very common way to preview a static site) because browsers
block fetch() across file:// origins. Option (b) - what this script
does - keeps the deployed pages as plain, dependency-free HTML (works
double-clicked from a folder, on any host, with no runtime cost) while
still giving you a single place to edit the header and footer. That's
why this project uses a build step instead of a runtime include.

HOW IT WORKS
------------
1. Reads src/partials/header.html and src/partials/footer.html. Each
   contains small tokens:
     {{BASE}}          -> replaced with "."  for root-level pages
                           or ".." for pages inside services/
     {{ACT_HOME}}, {{ACT_ABOUT}}, {{ACT_SERVICES}}, {{ACT_PRODUCTS}},
     {{ACT_INDUSTRIES}}, {{ACT_PROJECTS}}, {{ACT_WHYUS}}, {{ACT_CONTACT}}
                       -> each becomes " act" (highlights that nav
                          link) on the one page it belongs to, and ""
                          everywhere else.
2. Reads each file under src/pages/ (page-specific content only - the
   header/footer were already extracted out of these into the tokens
   {{HEADER}} and {{FOOTER}}).
3. Substitutes {{HEADER}} / {{FOOTER}} with the rendered partials and
   writes the final, complete HTML file to the matching path at the
   project root.

ADDING A NEW PAGE
------------------
1. Add a new file under src/pages/ (copy an existing one as a starting
   point - keep its {{HEADER}} and {{FOOTER}} tokens).
2. Add one line to the PAGES dict below with its output path, base
   prefix ("." or ".."), and which nav item should be highlighted.
3. Run `python3 build.py`.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC_PARTIALS = ROOT / "src" / "partials"
SRC_PAGES = ROOT / "src" / "pages"

# Every nav key that can be highlighted in the header, in the order the
# links appear. Must match the {{ACT_*}} tokens in src/partials/header.html.
NAV_KEYS = ["home", "about", "services", "products", "industries", "projects", "whyus", "contact"]

# output path (relative to project root) -> (base prefix, active nav key)
PAGES = {
    "index.html":                          (".",  "home"),
    "about.html":                          (".",  "about"),
    "services.html":                       (".",  "services"),
    "products.html":                       (".",  "products"),
    "industries.html":                     (".",  "industries"),
    "projects.html":                       (".",  "projects"),
    # "why-us" highlights the "Services" nav item, matching this site's
    # original behaviour (the Why Us page has always shared the
    # Services nav item's active state - preserved here intentionally).
    "why-us.html":                         (".",  "services"),
    "contact.html":                        (".",  "contact"),
    "services/boilers.html":               ("..", "services"),
    "services/water-treatment.html":       ("..", "services"),
    "services/industrial-chemicals.html":  ("..", "services"),
    "services/cooling-towers.html":        ("..", "services"),
    "services/air-compressors.html":       ("..", "services"),
    "services/utility-consultancy.html":   ("..", "services"),
}


def render_partial(template: str, base: str, active_key: str) -> str:
    """Fill in {{BASE}} and every {{ACT_*}} token in a partial template."""
    rendered = template.replace("{{BASE}}", base)
    for key in NAV_KEYS:
        token = "{{ACT_%s}}" % key.upper()
        rendered = rendered.replace(token, " act" if key == active_key else "")
    return rendered


def main() -> None:
    header_tpl = (SRC_PARTIALS / "header.html").read_text(encoding="utf-8")
    footer_tpl = (SRC_PARTIALS / "footer.html").read_text(encoding="utf-8")

    built = 0
    for rel_path, (base, active_key) in PAGES.items():
        page_src = SRC_PAGES / rel_path
        if not page_src.exists():
            raise FileNotFoundError(f"Missing source page: {page_src}")

        page_content = page_src.read_text(encoding="utf-8")
        header_html = render_partial(header_tpl, base, active_key)
        footer_html = render_partial(footer_tpl, base, active_key)

        final_html = page_content.replace("{{HEADER}}", header_html).replace(
            "{{FOOTER}}", footer_html
        )

        out_path = ROOT / rel_path
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(final_html, encoding="utf-8")
        built += 1
        print(f"  built {rel_path}")

    print(f"\nDone - {built} pages built from the shared header/footer.")


if __name__ == "__main__":
    main()
