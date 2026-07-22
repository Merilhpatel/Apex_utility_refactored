#!/usr/bin/env python3
"""
reformat_css.py
================
A tiny, content-safe CSS pretty-printer for assets/css/style.css.

Unlike HTML, whitespace between CSS tokens (outside of string literals and
comments) never affects rendering, so this is much simpler than the HTML
reformatter: walk the file character by character, and insert a newline +
indentation after every `{`, before every `}`, after every `}`, and after
every top-level `;` - while never touching anything inside a quoted string
or a /* comment */, so no selector, property value, or comment text is ever
altered.

A round-trip check strips all whitespace from both the original and the
reformatted file and asserts they are identical.
"""
import re
import sys
from pathlib import Path


def reformat(css_text, indent_unit="  "):
    out = []
    depth = 0
    i = 0
    n = len(css_text)
    in_string = None        # None, or the quote character we're inside
    pending_indent = False  # True once the next write() owes a fresh indent
    line_has_content = False  # True once something real is on the current line

    def write(s):
        nonlocal pending_indent, line_has_content
        if not s:
            return
        if pending_indent:
            out.append(indent_unit * depth)
            pending_indent = False
        out.append(s)
        line_has_content = True

    def newline():
        nonlocal pending_indent, line_has_content
        if pending_indent:
            return  # already on a fresh, not-yet-indented line
        if not line_has_content:
            return  # nothing written yet at all, or already just broke
        out.append("\n")
        pending_indent = True
        line_has_content = False

    while i < n:
        ch = css_text[i]

        if in_string:
            write(ch)
            if ch == "\\" and i + 1 < n:
                write(css_text[i + 1])
                i += 2
                continue
            if ch == in_string:
                in_string = None
            i += 1
            continue

        if ch in ("'", '"'):
            in_string = ch
            write(ch)
            i += 1
            continue

        if css_text[i:i + 2] == "/*":
            end = css_text.find("*/", i + 2)
            end = end + 2 if end != -1 else n
            newline()
            write(css_text[i:end])
            newline()
            i = end
            continue

        if ch == "{":
            if out and out[-1] == " ":
                out.pop()
            write(" {")
            depth += 1
            newline()
            i += 1
            while i < n and css_text[i] in " \t\r\n":
                i += 1
            continue

        if ch == "}":
            depth = max(depth - 1, 0)
            newline()
            write("}")
            newline()
            i += 1
            while i < n and css_text[i] in " \t\r\n":
                i += 1
            continue

        if ch == ";":
            write(";")
            newline()
            i += 1
            while i < n and css_text[i] in " \t\r\n":
                i += 1
            continue

        if ch in " \t\r\n":
            j = i
            while j < n and css_text[j] in " \t\r\n":
                j += 1
            if line_has_content:
                write(" ")
            i = j
            continue

        write(ch)
        i += 1

    result = "".join(out)
    result = re.sub(r"[ \t]+\n", "\n", result)
    result = re.sub(r"\n{3,}", "\n\n", result)
    return result.strip() + "\n"


def strip_all_ws(s):
    return re.sub(r"\s+", "", s)


def verify(original, reformatted):
    return strip_all_ws(original) == strip_all_ws(reformatted)


def main():
    if len(sys.argv) != 3:
        print("usage: reformat_css.py <input.css> <output.css>")
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
