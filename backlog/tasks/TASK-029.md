# Task: Implement GitHub Models API Client

| Field        | Value                |
|--------------|----------------------|
| **Task ID**  | TASK-029             |
| **Story**    | STORY-013            |
| **Status**   | To Do                |
| **Assignee** | 4-develop-agent      |
| **Estimate** | 5h                   |

## Description

Implement the Model Invocation Layer (`src/ai_generation/model_client.py`) — a thin async wrapper around `httpx.AsyncClient` that calls the GitHub Models chat completions API with exponential backoff retry on 429/5xx, 60-second timeout enforcement, and structured error mapping. The API key must never appear in logs.

## Implementation Details

**Files to create/modify:**
- `src/ai_generation/model_client.py` — `GitHubModelsClient` class

**Approach:**
```python
import asyncio
import httpx
import logging
from src.config import get_settings
from .exceptions import GenerationFailedError

logger = logging.getLogger(__name__)

class GitHubModelsClient:
    def __init__(self):
        self.settings = get_settings()
    
    async def generate(self, prompt: str, model: str = "gpt-4o") -> str:
        """Call GitHub Models API and return raw response content string."""
        headers = {
            "Authorization": f"Bearer {self.settings.github_models_api_key.get_secret_value()}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "response_format": {"type": "json_object"}
        }
        
        last_error = None
        for attempt in range(self.settings.ai_max_retries + 1):
            try:
                async with httpx.AsyncClient(
                    timeout=httpx.Timeout(self.settings.ai_request_timeout_seconds)
                ) as client:
                    response = await client.post(
                        f"{self.settings.github_models_endpoint}/chat/completions",
                        headers=headers, json=payload
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        return data["choices"][0]["message"]["content"]
                    
                    elif response.status_code == 429 or response.status_code >= 500:
                        if attempt < self.settings.ai_max_retries:
                            wait_seconds = 2 ** attempt
                            logger.warning(f"GitHub Models API {response.status_code}, retry {attempt+1}/{self.settings.ai_max_retries} in {wait_seconds}s")
                            await asyncio.sleep(wait_seconds)
                            last_error = f"HTTP {response.status_code}"
                            continue
                        raise GenerationFailedError(f"GitHub Models API failed after {self.settings.ai_max_retries} retries: HTTP {response.status_code}")
                    
                    else:
                        # Log full error internally; surface sanitised message
                        logger.error(f"GitHub Models API error: status={response.status_code}")
                        raise GenerationFailedError(f"GitHub Models API returned unexpected status: {response.status_code}")
            
            except httpx.TimeoutException:
                logger.error("GitHub Models API request timed out")
                raise GenerationFailedError("AI generation request timed out. Please retry.")
        
        raise GenerationFailedError(f"GitHub Models API failed: {last_error}")
```

Note: API key value must NOT appear in any log statement. Use `get_secret_value()` only in the Authorization header.

## API Changes

N/A — internal HTTP client.

## Data Model Changes

N/A

## Dependencies

| Prerequisite Task | Reason                                       |
|-------------------|----------------------------------------------|
| TASK-002          | Settings module (API key, endpoint, timeout) |
| TASK-030          | AI models (GenerationRequest) must exist     |

**Wave:** 4

## Acceptance Criteria

- [ ] Successful 200 response returns the `choices[0].message.content` string
- [ ] HTTP 429 triggers exponential backoff: 1s, 2s, 4s waits before raising after 3 retries
- [ ] HTTP 5xx triggers the same retry strategy
- [ ] `httpx.TimeoutException` raises `GenerationFailedError` (no retry)
- [ ] API key value never appears in log output (use `SecretStr.get_secret_value()` only in header construction)
- [ ] Client is tested with `respx` mock — no real API calls in tests

## Test Requirements

- **Unit tests:** Mock `httpx.AsyncClient.post` with `respx`; test 200 success path; test 429 retry (3 retries); test timeout; test 5xx
- **Integration tests:** N/A (real API calls not in test suite)
- **Edge cases:** API returns non-JSON body; API returns malformed choices array; max retries exhausted

## Parent References

| Ref Type | ID               |
|----------|------------------|
| Story    | STORY-013        |
| Epic     | EPIC-005         |
| BRD      | BRD-INT-001, BRD-INT-002, BRD-INT-003, BRD-INT-004, BRD-INT-005, BRD-NFR-005 |

## Definition of Done

- [ ] Code written and follows project conventions
- [ ] All tests passing (`pytest`)
- [ ] No linting errors
- [ ] PR opened and reviewed
- [ ] Acceptance criteria verified
