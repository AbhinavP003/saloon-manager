---
name: deploy
description: >-
  Merge the current branch into main, push to origin, and monitor the GCP Cloud
  Run deployment triggered by GitHub Actions. Use when the user invokes /deploy.
disable-model-invocation: true
---
# Deploy to Production

Ship changes by merging into `main`. Pushing `main` triggers [`.github/workflows/deploy.yml`](../../.github/workflows/deploy.yml): pytest → build → deploy backend and frontend to GCP Cloud Run (asia-south1).

## When to use

Only when the user explicitly invokes `/deploy` (optionally with a branch name, e.g. `/deploy from feature/foo`).

## Step 1 — Inspect repo state

Run in parallel:

```bash
git status
git branch --show-current
git log --oneline -5
git fetch origin
```

Determine:

- Current branch (`SOURCE_BRANCH`)
- Whether there are uncommitted or unstaged changes
- Whether `main` is behind/ahead of `origin/main`

If the user named a branch in the prompt, use that as `SOURCE_BRANCH`. Otherwise use the current branch.

**Stop** if there are uncommitted changes — ask the user to commit or stash first.

**Stop** if `SOURCE_BRANCH` is `main` and the user did not explicitly ask to push `main` directly. Confirm intent before continuing.

## Step 2 — Run tests locally

```bash
uv run pytest tests/ -v
```

Set env vars if needed (PowerShell):

```powershell
$env:DATABASE_URL="sqlite+aiosqlite:///./test.db"
$env:SECRET_KEY="dummy_test_secret_key"
```

If `uv` is unavailable, try `python -m pytest tests/ -v` with the same env vars.

**Stop and report failures** — do not merge if tests fail.

## Step 3 — Confirm with the user

Ask explicitly:

> Merge `SOURCE_BRANCH` → `main` and push to trigger GCP deployment?

Do not proceed until the user confirms.

## Step 4 — Merge and push

```bash
git checkout main
git pull origin main
git merge SOURCE_BRANCH --no-edit
git push origin main
```

Replace `SOURCE_BRANCH` with the actual branch name.

### Safety rules (mandatory)

- NEVER `git push --force` to `main` or `master`
- NEVER use `--no-verify` or skip hooks
- NEVER amend commits unless the user explicitly requests it
- If merge conflicts occur, **stop** — do not auto-resolve; ask the user

After a successful push, switch back to `SOURCE_BRANCH` if the user was working on a feature branch:

```bash
git checkout SOURCE_BRANCH
```

## Step 5 — Monitor GitHub Actions

Requires `gh` CLI and GitHub auth:

```bash
gh run list --workflow=deploy.yml --branch main --limit 1
gh run watch
```

If `gh` is unavailable, tell the user to check Actions at:
`https://github.com/AbhinavP003/saloon-manager/actions`

Report:

- Workflow conclusion (success / failure)
- Which jobs failed (test, deploy-backend, deploy-frontend)
- Link to the run

## Step 6 — Post-deploy checks

On success, remind the user:

1. Production DB migrations may still be needed — see [docs/GCP_DEPLOYMENT.md](../../docs/GCP_DEPLOYMENT.md) §6
2. Frontend must be built with `BACKEND_URL` secret set so API calls hit the live backend
3. `FRONTEND_URL` must be in GitHub secrets for CORS on the backend

Live beta URLs (if unchanged): see [docs/gcp_deployment_context.md](../../docs/gcp_deployment_context.md).

## Response format

Keep the final summary short:

1. Branch merged and pushed (commit SHA)
2. CI result
3. Any blockers or follow-up steps
