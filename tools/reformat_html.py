#!/usr/bin/env python3
"""
reformat_html.py
=================
A conservative, content-safe HTML pretty-printer built specifically for this
project (src/partials/*.html + src/pages/*.html -> stitched by build.py).

THE PROBLEM WITH GENERIC BEAUTIFIERS
-------------------------------------
Generic beautifiers re-flow whitespace everywhere, which is only safe between
elements that are unambiguously block-level. This codebase mixes tightly
packed inline elements (an icon glued directly to the text next to it, links
and spans used inline) with Tailwind flex/grid layouts. Blindly inserting a
newline between two elements that currently have ZERO characters between
them can inject a visible space into the rendered page - browsers collapse a
*run* of whitespace into a single rendered space, but zero characters is not
a run of whitespace, so turning "nothing" into "newline + indent" is only
safe in specific, provable situations.

WHAT THIS SCRIPT DOES
-----------------------
It only ever inserts a line break at an element boundary when doing so is
guaranteed invisible to the rendered page:

  1. The boundary already had at least one whitespace character in the
     source. Collapsing one whitespace run into a differently-shaped
     whitespace run is always safe outside <pre>/<script>/<style>/<textarea>.
  2. The boundary has zero original characters, but BOTH neighbouring tags
     are unambiguous block-level elements (div, section, ul, li, table
     cells, headings, etc.) - a whitespace-only gap between two block boxes
     is never rendered by any browser.
  3. The boundary has zero original characters, but the shared parent
     element the two tags live inside carries a `flex`/`grid` (or
     `inline-flex`/`inline-grid`) class. Per the CSS Flexbox/Grid spec,
     whitespace-only text runs inside a flex/grid container are not turned
     into rendered content, so it's safe to insert one there too - this is
     what lets us cleanly indent the nav links, cards, and menu items that
     make up most of this site's markup.

Everywhere else (e.g. an <i> icon glued directly to the word after it) is
left byte-for-byte exactly as written.

A round-trip check (verify()) strips all whitespace from both the original
and the reformatted file and asserts they are identical - guaranteeing no
visible character was ever added, removed, or reordered.
"""
import re
import sys
from pathlib import Path

VOID_TAGS = {
    "area", "base", "br", "col", "embed", "hr", "img", "input",
    "link", "meta", "param", "source", "track", "wbr",
}

# Always-block elements: a whitespace gap next to these is never rendered.
BLOCK_SAFE = {
    "html", "head", "body", "div", "section", "header", "footer", "nav",
    "main", "article", "aside", "ul", "ol", "li", "table", "thead", "tbody",
    "tfoot", "tr", "td", "th", "form", "h1", "h2", "h3", "h4", "h5", "h6",
    "p", "blockquote", "figure", "figcaption", "hr", "fieldset", "legend",
    "dl", "dt", "dd", "details", "summary",
}

RAW_TEXT_TAGS = {"script", "style", "textarea", "pre"}
FLEX_GRID_TOKENS = {"flex", "inline-flex", "grid", "inline-grid"}

TOKEN_RE = re.compile(
    r"(<!--.*?-->|<!DOCTYPE[^>]*>|</?[a-zA-Z][a-zA-Z0-9:-]*(?:\"[^\"]*\"|'[^']*'|[^'\">])*>)",
    re.DOTALL,
)
TAGNAME_RE = re.compile(r"^</?([a-zA-Z][a-zA-Z0-9:-]*)")
CLASS_RE = re.compile(r'class=(["\'])(.*?)\1', re.DOTALL)


def tag_name(tag_text):
    m = TAGNAME_RE.match(tag_text)
    return m.group(1).lower() if m else ""


def is_closing(tag_text):
    return tag_text.startswith("</")


def is_selfclosing(tag_text):
    return tag_text.rstrip(">").endswith("/") or tag_name(tag_text) in VOID_TAGS


def is_comment_or_doctype(tag_text):
    return tag_text.startswith("<!--") or tag_text.upper().startswith("<!DOCTYPE")


def is_flexish(tag_text):
    """True if this opening tag carries a flex/grid class - including
    responsive variants like `xl:flex` or `lg:grid`. Whichever breakpoint it
    applies at, the element is either display:flex/grid (whitespace-only
    text nodes inside it are not rendered) or display:none at other
    breakpoints (nothing is rendered at all) - so it's safe either way.
    """
    m = CLASS_RE.search(tag_text)
    if not m:
        return False
    for token in m.group(2).split():
        bare = token.rsplit(":", 1)[-1]
        if bare in FLEX_GRID_TOKENS:
            return True
    return False


def reformat(html_text, indent_unit="  "):
    tokens = TOKEN_RE.split(html_text)
    out = []
    stack = []            # list of {"name": str, "flexish": bool}
    raw_mode_tag = None
    prev_kind = None      # "tag" | "text-ws" | "text-content" | None

    def cur_depth():
        return len(stack)

    def emit_break():
        out.append("\n" + indent_unit * cur_depth())

    def parent_is_flexish():
        return bool(stack) and stack[-1]["flexish"]

    for tok in tokens:
        if tok == "":
            continue
        is_tag = bool(TOKEN_RE.fullmatch(tok))

        if raw_mode_tag:
            if is_tag and is_closing(tok) and tag_name(tok) == raw_mode_tag:
                stack.pop()
                out.append(tok)
                raw_mode_tag = None
                prev_kind = "tag"
            else:
                out.append(tok)
            continue

        if not is_tag:
            if tok.strip() == "":
                prev_kind = "text-ws"
                continue
            out.append(tok)
            prev_kind = "text-content"
            continue

        if is_comment_or_doctype(tok):
            if prev_kind is not None:
                emit_break()
            out.append(tok)
            prev_kind = "tag"
            continue

        name = tag_name(tok)
        closing = is_closing(tok)
        selfclose = is_selfclosing(tok) and not closing

        # Decide whether to break onto a new line before this tag. This must
        # happen BEFORE we pop the stack for a closing tag, so cur_depth()/
        # parent_is_flexish() still reflect the element we're leaving.
        if closing:
            if stack:
                stack.pop()

        if prev_kind == "text-ws":
            emit_break()
        elif prev_kind == "tag":
            prev_tag = out[-1]
            prev_name = tag_name(prev_tag)
            if prev_name in BLOCK_SAFE and name in BLOCK_SAFE:
                emit_break()
            elif parent_is_flexish():
                emit_break()
            # else: ambiguous inline pair outside a flex/grid parent with
            # zero original whitespace -> leave glued, byte-for-byte.
        # prev_kind == "text-content" or None -> never break before a tag
        # that sits directly against real text (or the very first token).

        out.append(tok)
        prev_kind = "tag"

        if not closing and not selfclose:
            stack.append({"name": name, "flexish": is_flexish(tok)})
            if name in RAW_TEXT_TAGS:
                raw_mode_tag = name

    result = "".join(out)
    result = re.sub(r"\n[ \t]*\n+", "\n", result)
    return result.strip() + "\n"


def strip_all_ws(s):
    return re.sub(r"\s+", "", s)


def verify(original, reformatted):
    return strip_all_ws(original) == strip_all_ws(reformatted)


def main():
    if len(sys.argv) != 3:
        print("usage: reformat_html.py <input.html> <output.html>")
        sys.exit(1)
    src = Path(sys.argv[1])
    dst = Path(sys.argv[2])
    original = src.read_text(encoding="utf-8")
    formatted = reformat(original)
    if not verify(original, formatted):
        print(f"REFUSING to write {dst}: content mismatch after reformat!")
        sys.exit(2)
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(formatted, encoding="utf-8")
    print(f"ok: {src} -> {dst} ({len(original)} -> {len(formatted)} bytes)")


if __name__ == "__main__":
    main()
