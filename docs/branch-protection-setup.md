# Branch Protection Setup Guide

This guide explains how to configure GitHub branch protection rules so that
wave PRs cannot be merged without passing CI checks and a code review.

## Prerequisites

- Repository hosted on GitHub (public or GitHub Pro/Team/Enterprise for private repos).
- The **CI — Build & Test** workflow (`.github/workflows/ci.yml`) has run at least once
  so GitHub registers the check names.

## Steps

### 1. Navigate to Branch Protection Settings

1. Go to your repository on GitHub.
2. Click **Settings** → **Branches** (under "Code and automation").
3. Under **Branch protection rules**, click **Add branch protection rule**.

### 2. Configure the Rule

| Setting | Value |
|---------|-------|
| **Branch name pattern** | `main` |
| **Require a pull request before merging** | ✅ Enabled |
| → Require approvals | `1` (or more) |
| → Dismiss stale pull request approvals when new commits are pushed | ✅ Enabled |
| **Require status checks to pass before merging** | ✅ Enabled |
| → Require branches to be up to date before merging | ✅ Enabled |
| → **Status checks that are required:** | `Build Check`, `Test Suite` |
| **Require conversation resolution before merging** | ✅ Recommended |
| **Do not allow bypassing the above settings** | ✅ Recommended for team repos |

### 3. Save

Click **Create** (or **Save changes** if editing an existing rule).

## How It Works with the Wave Orchestrator

The `@3.5-build-orchestrator-agent` creates one PR per wave:

```
Wave 0 branch → PR #1 → CI runs → Review → Merge ✅
Wave 1 branch → PR #2 → CI runs → Review → Merge ✅
Wave 2 branch → PR #3 → CI runs → Review → Merge ✅
```

With branch protection enabled:

- **CI must pass** — the `Build Check` and `Test Suite` jobs must succeed before
  the merge button is enabled.
- **Review required** — at least one approving review is needed.
- **Up-to-date branch** — the wave branch must include the latest `main` commits
  (i.e., all prior waves).

If CI fails, the orchestrator will fix the issues on the wave branch and push
a new commit. CI re-runs automatically.

## Required Check Names

These names come from the `ci.yml` workflow job names:

| Job Name | Required? | Purpose |
|----------|-----------|---------|
| `Build Check` | ✅ Yes | Syntax check + import validation |
| `Test Suite` | ✅ Yes | Runs pytest |
| `Lint (optional)` | ❌ No | Ruff linting (advisory, `continue-on-error`) |

## GitHub CLI Alternative

You can also configure branch protection via the GitHub CLI:

```bash
gh api repos/{owner}/{repo}/branches/main/protection \
  --method PUT \
  --field required_status_checks='{"strict":true,"contexts":["Build Check","Test Suite"]}' \
  --field required_pull_request_reviews='{"required_approving_review_count":1,"dismiss_stale_reviews":true}' \
  --field enforce_admins=true
```

## Rulesets (Alternative for GitHub Enterprise / newer repos)

If your repository uses the newer **Rulesets** feature instead of classic branch
protection:

1. **Settings** → **Rules** → **Rulesets** → **New ruleset** → **New branch ruleset**.
2. Set target to branches matching `main`.
3. Add rule: **Require a pull request before merging** (1 approval).
4. Add rule: **Require status checks to pass** → add `Build Check` and `Test Suite`.
5. Save the ruleset.
