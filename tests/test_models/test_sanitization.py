"""Unit tests for XSS sanitisation utilities.

Validates that the sanitise_markdown function correctly strips dangerous
HTML while preserving safe markup, and that sanitize_log prevents
log injection.

Traceability:
    BRD-NFR-005: XSS prevention on rendered content
    BRD-FR-011: Lesson markdown_content sanitised
    TASK-016: sanitiser.py implementation
"""

import pytest

from src.course_management.sanitiser import sanitise_markdown
from src.sanitize import is_safe_id, sanitize_log


# ---------------------------------------------------------------------------
# sanitise_markdown — dangerous tags
# ---------------------------------------------------------------------------


class TestSanitiseMarkdownDangerousTags:
    def test_script_tag_and_content_is_stripped(self):
        """<script> tag and its content are completely removed. [BRD-NFR-005]"""
        dirty = "<script>alert('xss')</script><p>Safe</p>"
        clean = sanitise_markdown(dirty)
        assert "<script>" not in clean
        assert "alert(" not in clean
        assert "<p>Safe</p>" in clean

    def test_script_tag_with_src_attribute_stripped(self):
        """<script src=...> is stripped. [BRD-NFR-005]"""
        dirty = '<script src="https://evil.com/xss.js"></script><p>OK</p>'
        clean = sanitise_markdown(dirty)
        assert "<script" not in clean
        assert "evil.com" not in clean

    def test_style_tag_and_content_is_stripped(self):
        """<style> tag and all CSS are removed. [BRD-NFR-005]"""
        dirty = "<style>body{background:red}</style><p>Content</p>"
        clean = sanitise_markdown(dirty)
        assert "<style>" not in clean
        assert "background:red" not in clean

    def test_iframe_tag_is_stripped(self):
        """<iframe> is removed. [BRD-NFR-005]"""
        dirty = '<iframe src="https://evil.com/"></iframe><p>Text</p>'
        clean = sanitise_markdown(dirty)
        assert "<iframe" not in clean

    def test_object_tag_is_stripped(self):
        """<object> is removed. [BRD-NFR-005]"""
        dirty = '<object data="evil.swf"></object><p>Text</p>'
        clean = sanitise_markdown(dirty)
        assert "<object" not in clean

    def test_onload_event_attribute_is_stripped(self):
        """Event handlers (onerror, onload) on allowed tags are removed. [BRD-NFR-005]"""
        dirty = '<img src="x" onerror="alert(1)" alt="img">'
        clean = sanitise_markdown(dirty)
        assert "onerror" not in clean

    def test_javascript_href_is_stripped(self):
        """javascript: hrefs are stripped. [BRD-NFR-005]"""
        dirty = '<a href="javascript:alert(1)">Click me</a>'
        clean = sanitise_markdown(dirty)
        # bleach strips href with javascript: scheme
        assert "javascript:" not in clean

    def test_nested_script_in_allowed_tag_stripped(self):
        """script nested inside an allowed tag is stripped."""
        dirty = "<p><script>evil()</script>Safe text</p>"
        clean = sanitise_markdown(dirty)
        assert "<script>" not in clean
        assert "evil()" not in clean


# ---------------------------------------------------------------------------
# sanitise_markdown — safe tags preserved
# ---------------------------------------------------------------------------


class TestSanitiseMarkdownSafeTags:
    def test_paragraph_tag_preserved(self):
        """<p> tags are preserved. [BRD-FR-011]"""
        content = "<p>This is a paragraph.</p>"
        assert sanitise_markdown(content) == content

    def test_heading_tags_preserved(self):
        """Heading tags h1-h6 are preserved."""
        for i in range(1, 7):
            content = f"<h{i}>Heading {i}</h{i}>"
            assert f"<h{i}>" in sanitise_markdown(content)

    def test_code_block_preserved(self):
        """<pre><code> blocks are preserved."""
        content = "<pre><code>print('hello')</code></pre>"
        clean = sanitise_markdown(content)
        assert "<pre>" in clean
        assert "<code>" in clean

    def test_strong_and_em_preserved(self):
        """<strong> and <em> are preserved."""
        content = "<strong>Bold</strong> and <em>italic</em>."
        clean = sanitise_markdown(content)
        assert "<strong>Bold</strong>" in clean
        assert "<em>italic</em>" in clean

    def test_ordered_and_unordered_lists_preserved(self):
        """<ul>, <ol>, and <li> tags are preserved."""
        content = "<ul><li>Item 1</li><li>Item 2</li></ul>"
        clean = sanitise_markdown(content)
        assert "<ul>" in clean
        assert "<li>Item 1</li>" in clean

    def test_anchor_with_safe_href_preserved(self):
        """Anchor with safe href is preserved."""
        content = '<a href="https://github.com" rel="noopener">GitHub</a>'
        clean = sanitise_markdown(content)
        # Check that the exact href attribute is preserved (not a substring URL check)
        assert 'href="https://github.com"' in clean

    def test_image_with_safe_src_preserved(self):
        """Image tag with safe src is preserved."""
        content = '<img src="https://example.com/img.png" alt="Example">'
        clean = sanitise_markdown(content)
        assert 'src="https://example.com/img.png"' in clean

    def test_empty_string_returns_empty(self):
        """Empty string returns empty string."""
        assert sanitise_markdown("") == ""

    def test_none_input_returns_empty(self):
        """None input returns empty string."""
        assert sanitise_markdown(None) == ""

    def test_plain_text_preserved(self):
        """Plain text without HTML is returned as-is."""
        text = "Just plain text without any HTML."
        assert sanitise_markdown(text) == text


# ---------------------------------------------------------------------------
# sanitize_log — log injection prevention
# ---------------------------------------------------------------------------


class TestSanitizeLog:
    def test_removes_newlines(self):
        """sanitize_log strips newlines to prevent log injection."""
        value = "user\ninjected\nlines"
        result = sanitize_log(value)
        assert "\n" not in result
        assert result == "userinjectedlines"

    def test_removes_carriage_returns(self):
        """sanitize_log strips carriage returns."""
        value = "user\rinjected"
        result = sanitize_log(value)
        assert "\r" not in result

    def test_preserves_normal_string(self):
        """sanitize_log preserves normal strings."""
        value = "normal-user-id-123"
        assert sanitize_log(value) == value

    def test_converts_non_string_to_string(self):
        """sanitize_log converts non-string values to string."""
        result = sanitize_log(123)
        assert result == "123"

    def test_handles_none(self):
        """sanitize_log handles None without error."""
        result = sanitize_log(None)
        assert result == "None"


# ---------------------------------------------------------------------------
# is_safe_id — UUID validation
# ---------------------------------------------------------------------------


class TestIsSafeId:
    def test_valid_uuid_returns_true(self):
        """Valid UUID returns True."""
        assert is_safe_id("550e8400-e29b-41d4-a716-446655440000") is True

    def test_invalid_string_returns_false(self):
        """Non-UUID string returns False."""
        assert is_safe_id("not-a-uuid") is False

    def test_sql_injection_string_returns_false(self):
        """SQL injection attempt returns False."""
        assert is_safe_id("'; DROP TABLE users; --") is False

    def test_empty_string_returns_false(self):
        """Empty string returns False."""
        assert is_safe_id("") is False
