"""Markdown and HTML sanitisation utilities.

Provides two public helpers:

- :func:`sanitise_markdown` — converts Markdown to HTML, then scrubs unsafe
  tags/attributes to prevent XSS when the content is rendered in a browser.
- :func:`sanitise_html` — scrubs raw HTML directly without any Markdown
  conversion step.

Both functions use ``bleach`` for sanitisation and allow only a curated
allowlist of tags and attributes appropriate for educational course content.
"""

import bleach
import markdown as md_lib

# ---------------------------------------------------------------------------
# Allowlists
# ---------------------------------------------------------------------------

ALLOWED_TAGS: list[str] = [
    "h1", "h2", "h3", "h4", "h5", "h6",
    "p", "br", "hr",
    "ul", "ol", "li",
    "strong", "em", "code", "pre", "blockquote",
    "a", "img",
    "table", "thead", "tbody", "tr", "th", "td",
]
"""HTML tags permitted after sanitisation."""

ALLOWED_ATTRIBUTES: dict[str, list[str]] = {
    "a": ["href", "title", "target"],
    "img": ["src", "alt", "title", "width", "height"],
    "code": ["class"],
    "pre": ["class"],
}
"""HTML attributes permitted on specific tags after sanitisation."""


# ---------------------------------------------------------------------------
# Public helpers
# ---------------------------------------------------------------------------


def sanitise_markdown(raw_markdown: str) -> str:
    """Convert Markdown to HTML and sanitise the result to prevent XSS.

    The conversion step uses ``markdown`` with ``fenced_code`` and ``tables``
    extensions so that code blocks and tables in lesson content render
    correctly.  The resulting HTML is then passed through ``bleach`` to strip
    any disallowed tags or attributes.

    Args:
        raw_markdown: Source text in Markdown format.

    Returns:
        A sanitised HTML string safe for direct injection into the DOM.

    Example::

        html = sanitise_markdown("# Hello\\n<script>alert(1)</script>")
        # Returns "<h1>Hello</h1>" — the script tag is stripped.
    """
    html = md_lib.markdown(raw_markdown, extensions=["fenced_code", "tables"])
    return bleach.clean(html, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES, strip=True)


def sanitise_html(raw_html: str) -> str:
    """Sanitise raw HTML to prevent XSS without any Markdown conversion.

    Use this helper when the input is already HTML (e.g. rich-text editor
    output) rather than Markdown source.

    Args:
        raw_html: Untrusted HTML string.

    Returns:
        A sanitised HTML string with only allowlisted tags and attributes.
    """
    return bleach.clean(raw_html, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES, strip=True)
