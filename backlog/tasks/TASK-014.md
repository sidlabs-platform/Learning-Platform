# Task: Implement Markdown Sanitiser (bleach wrapper)

| Field        | Value                |
|--------------|----------------------|
| **Task ID**  | TASK-014             |
| **Story**    | STORY-006            |
| **Status**   | To Do                |
| **Assignee** | 4-develop-agent      |
| **Estimate** | 2h                   |

## Description

Implement the `sanitise_markdown()` function using `bleach` that strips all unsafe HTML tags and attributes from Markdown/HTML content before it is stored or rendered, preventing XSS attacks from user-submitted or AI-generated content.

## Implementation Details

**Files to create/modify:**
- `src/course_management/sanitiser.py` — `sanitise_markdown(raw_content: str) -> str`

**Approach:**
```python
import bleach
from bleach.linkifier import LinkifyFilter

ALLOWED_TAGS = [
    "p", "h1", "h2", "h3", "h4", "h5", "h6",
    "ul", "ol", "li", "blockquote", "pre", "code",
    "strong", "em", "b", "i", "u", "s",
    "a", "img", "br", "hr",
    "table", "thead", "tbody", "tr", "th", "td",
]

ALLOWED_ATTRIBUTES = {
    "a": ["href", "title", "rel"],
    "img": ["src", "alt", "title", "width", "height"],
    "code": ["class"],  # For syntax highlighting class names
    "*": ["id"],  # Anchor links
}

def sanitise_markdown(raw_content: str) -> str:
    """
    Sanitise HTML/Markdown content to prevent XSS.
    Called on every lesson create/update and AI-generated content persist.
    """
    if not raw_content:
        return ""
    return bleach.clean(
        raw_content,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        strip=True,  # Strip disallowed tags rather than escaping them
    )
```

Note: `sanitise_markdown` is called at write-time in `create_lesson()`, `update_lesson()`, and in the AI content persistence layer. This is the primary defence; template rendering provides secondary defence-in-depth.

## API Changes

N/A — utility function only.

## Data Model Changes

N/A

## Dependencies

| Prerequisite Task | Reason                             |
|-------------------|------------------------------------|
| TASK-001          | `bleach` must be in dependencies   |

**Wave:** 3

## Acceptance Criteria

- [ ] `sanitise_markdown('<script>alert(1)</script><p>Hello</p>')` returns `<p>Hello</p>` (script stripped)
- [ ] `sanitise_markdown('<a href="javascript:alert(1)">click</a>')` strips the `javascript:` href
- [ ] `sanitise_markdown('<p class="safe">text</p>')` preserves allowed tags
- [ ] `sanitise_markdown('')` returns `''` without error
- [ ] `sanitise_markdown(None)` returns `''` without error

## Test Requirements

- **Unit tests:** Test with `<script>` tag, `javascript:` href, `onerror=` attribute, `<img>` with `onload`, plain Markdown text (no HTML), `<pre><code>` blocks (should be preserved)
- **Integration tests:** Test that lesson creation rejects `<script>` in `markdownContent`
- **Edge cases:** Nested `<script>` tags; encoded entities `&lt;script&gt;`; SVG with event handlers

## Parent References

| Ref Type | ID               |
|----------|------------------|
| Story    | STORY-006        |
| Epic     | EPIC-003         |
| BRD      | BRD-FR-037, BRD-NFR-006 |

## Definition of Done

- [ ] Code written and follows project conventions
- [ ] All tests passing (`pytest`)
- [ ] No linting errors
- [ ] PR opened and reviewed
- [ ] Acceptance criteria verified
