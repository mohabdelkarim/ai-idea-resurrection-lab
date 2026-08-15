# Contributing / local development

## Secrets

| Variable | Required | Purpose |
|----------|----------|---------|
| `GROQ_API_KEY` | yes | Analyzer model calls |
| `GITHUB_TOKEN` | yes | Scan issues, write to this repo |
| `COMMENT_GITHUB_TOKEN` | no | Cross-repo issue comments (PAT) |

Create `COMMENT_GITHUB_TOKEN` as a classic PAT with `public_repo`, or a fine-grained token with Issues: Write on public repositories. Add it under GitHub → Settings → Secrets → Actions.

## Pipeline contract

1. Scanner writes graveyard entries (includes `state_reason`).
2. Analyzer hard-rejects junk / by-design / already-solved / failed validation.
3. PoC syntax validation runs before ship; failure demotes to analysis/RFC-only.
4. Generator raises on failure; `mark_resurrected` / `mark_repo_used` only after artifacts exist.
5. Commenter uses `COMMENT_GITHUB_TOKEN` and truthful copy.

## Discoverability (why the repo may look “invisible”)

GitHub Explore/search heavily weights: stars, topics, accurate description, recent activity, and social shares.

This repo previously had:
- **0 topics** (now set: ai, groq, github-actions, llm, …)
- **Outdated description** saying OpenAI while the stack is Groq
- **No homepage**
- Soft social proof (0 stars) until people find it via topics + LinkedIn/Twitter/Show HN

After pushing these changes, share the repo URL with the updated About blurb. Stars come from distribution, not from more resurrections.

## Tests

```bash
pip install -r requirements.txt
pytest -q
ruff check scripts tests
```
