/**
 * tailwind-config.js
 * --------------------
 * Tailwind Play CDN configuration for Apex Utility.
 *
 * This must be loaded BEFORE `https://cdn.tailwindcss.com` in every page's
 * <head> (same order the site already used when this was an inline
 * <script> block) so the brand colors/fonts below are picked up by the
 * Tailwind CDN build.
 *
 * Previously this object literal was duplicated inline in the <head> of
 * all 14 HTML pages. It now lives here once - update brand colors or
 * fonts in this single file and every page picks up the change.
 */
tailwind.config = {
  theme: {
    extend: {
      colors: {
        "brand-navy": "#0B1F3A",
        "brand-navy-deep": "#061229",
        "brand-blue": "#1476FF",
        "brand-sky": "#1E90FF",
        "brand-ice": "#EEF4FB",
        "brand-ink": "#45526A",
        "brand-line": "#DCE5F0",
        "brand-warm": "#E8451A"
      },
      fontFamily: {
        display: ['"Space Grotesk"', "sans-serif"],
        body: ["Inter", "sans-serif"],
        mono: ['"IBM Plex Mono"', "monospace"]
      }
    }
  }
};
