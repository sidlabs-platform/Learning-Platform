"""Markdown / HTML sanitiser — strips unsafe tags and attributes to prevent XSS.

``sanitise_markdown`` is called at *write-time* whenever lesson content is created
or updated (both via the admin UI and from AI-generated drafts).  Template
rendering provides a secondary defence-in-depth layer, but this function is the
primary gate.

Two-pass strategy
-----------------
1. **Pre-pass** (``_strip_dangerous_content``): removes a known set of
   *executable* tags (``<script>``, ``<style>``, ``<iframe>``, …) together with
   their entire inner text using Python's ``html.parser``.  ``bleach`` with
   ``strip=True`` would remove the *tag* but preserve the inner text
   (``alert(1)`` would survive), so this extra step is necessary for tags whose
   text content is itself dangerous.
2. **Bleach pass** (``bleach.clean``): removes any remaining disallowed tags
   and attributes from the pre-cleaned string.
"""

import bleach
from html.parser import HTMLParser

# ---------------------------------------------------------------------------
# Tag sets
# ---------------------------------------------------------------------------

# Tags whose *entire content* (including inner text) should be discarded.
_STRIP_WITH_CONTENT: frozenset[str] = frozenset(
    {"script", "style", "iframe", "object", "embed", "noscript", "applet", "form"}
)

# Tags that are safe to render in lesson content.
ALLOWED_TAGS: list[str] = [
    "p",
    "h1", "h2", "h3", "h4", "h5", "h6",
    "ul", "ol", "li",
    "blockquote",
    "pre", "code",
    "strong", "em", "b", "i", "u", "s",
    "a",
    "img",
    "br", "hr",
    "table", "thead", "tbody", "tr", "th", "td",
]

# Per-tag and global attribute allow-list.
# ``"*"`` applies to every tag that is itself allowed.
ALLOWED_ATTRIBUTES: dict[str, list[str]] = {
    "a": ["href", "title", "rel"],
    "img": ["src", "alt", "title", "width", "height"],
    "code": ["class"],   # syntax-highlighting class names (e.g. language-python)
    "*": ["id"],         # anchor link targets
}


# ---------------------------------------------------------------------------
# Pre-pass: remove dangerous tags and all their inner content
# ---------------------------------------------------------------------------

class _ContentStripper(HTMLParser):
    """HTMLParser subclass that drops specified tags *and* their inner text.

    Ordinary ``strip=True`` bleach behaviour preserves inner text, which is
    unsafe for executable tags such as ``<script>``.  This parser completely
    discards those tag subtrees.
    """

    def __init__(self) -> None:
        super().__init__(convert_charrefs=False)
        self._skip_depth: int = 0
        self._buf: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        """Suppress dangerous tags; pass through everything else."""
        if tag in _STRIP_WITH_CONTENT:
            self._skip_depth += 1
        elif self._skip_depth == 0:
            attr_str = "".join(
                f' {k}="{v}"' if v is not None else f" {k}" for k, v in attrs
            )
            self._buf.append(f"<{tag}{attr_str}>")

    def handle_endtag(self, tag: str) -> None:
        """Restore normal output when a suppressed tag closes."""
        if tag in _STRIP_WITH_CONTENT:
            if self._skip_depth > 0:
                self._skip_depth -= 1
        elif self._skip_depth == 0:
            self._buf.append(f"</{tag}>")

    def handle_data(self, data: str) -> None:
        """Pass through text content only when not inside a suppressed tag."""
        if self._skip_depth == 0:
            self._buf.append(data)

    def handle_entityref(self, name: str) -> None:
        """Preserve named HTML entities."""
        if self._skip_depth == 0:
            self._buf.append(f"&{name};")

    def handle_charref(self, name: str) -> None:
        """Preserve numeric HTML character references."""
        if self._skip_depth == 0:
            self._buf.append(f"&#{name};")

    def result(self) -> str:
        """Return the accumulated safe output."""
        return "".join(self._buf)


def _strip_dangerous_content(html: str) -> str:
    """Remove dangerous executable tags and their inner content entirely.

    Args:
        html: Raw HTML string.

    Returns:
        HTML string with ``<script>``, ``<style>``, ``<iframe>``, and similar
        tags—plus all text nested inside them—removed.
    """
    parser = _ContentStripper()
    parser.feed(html)
    return parser.result()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def sanitise_markdown(raw_content: str | None) -> str:
    """Strip unsafe HTML tags and attributes from Markdown/HTML content.

    Applies a two-pass sanitisation strategy:

    1. Pre-pass strips executable tags (e.g. ``<script>``) *and* their inner
       text so that dangerous code is not preserved as plain text.
    2. ``bleach.clean`` removes any remaining disallowed tags and attributes.

    Args:
        raw_content: Raw HTML or Markdown string, possibly containing
            user-supplied or AI-generated markup.

    Returns:
        A sanitised HTML string with all disallowed tags *stripped* (not
        escaped) and all disallowed attributes removed.  Returns an empty
        string when *raw_content* is ``None`` or the empty string.

    Examples:
        >>> sanitise_markdown('<script>alert(1)</script><p>Hello</p>')
        '<p>Hello</p>'
        >>> sanitise_markdown('')
        ''
        >>> sanitise_markdown(None)
        ''
    """
    if not raw_content:
        return ""

    # Pass 1 — remove dangerous tag subtrees (including their text content)
    pre_cleaned = _strip_dangerous_content(raw_content)

    # Pass 2 — bleach removes remaining disallowed tags / attributes
    return bleach.clean(
        pre_cleaned,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        strip=True,   # remove disallowed tags entirely rather than HTML-escaping them
    )
