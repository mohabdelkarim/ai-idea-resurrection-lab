from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

import requests

from config import STATS_FILE, VOTES_FILE


logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
LOGGER = logging.getLogger(__name__)

OWN_REPO = "mohabdelkarim/ai-idea-resurrection-lab"


def _safe_str(value: Any) -> str:
    """Convert value to string and strip surrogate characters that break UTF-8 encoding."""
    text = str(value) if not isinstance(value, str) else value
    return text.encode("utf-8", errors="ignore").decode("utf-8", errors="ignore")


def load_votes() -> dict[str, Any]:
    path = Path(VOTES_FILE)
    if not path.exists():
        return {}
    try:
        parsed = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as error:
        LOGGER.warning("Failed to load votes file %s: %s", path, error)
        return {}
    if isinstance(parsed, dict):
        return parsed
    LOGGER.warning("Votes file %s does not contain a JSON object.", path)
    return {}


def save_votes(data: dict[str, Any]) -> None:
    path = Path(VOTES_FILE)
    path.parent.mkdir(parents=True, exist_ok=True)
    safe_data = {
        k: _safe_str(v) if isinstance(v, str) else v
        for k, v in data.items()
    }
    path.write_text(
        json.dumps(safe_data, indent=2, ensure_ascii=True),
        encoding="utf-8",
    )
    LOGGER.info("Written: %s", path)


def build_vote_body(meta: dict[str, Any]) -> str:
    title = _safe_str(meta.get("title", ""))
    repo = _safe_str(meta.get("repo", ""))
    one_line_why = _safe_str(meta.get("one_line_why", ""))
    original_url = _safe_str(meta.get("original_url", ""))
    impact_score = int(meta.get("impact_score", 0))

    return (
        f"## Community Vote: {title}\n\n"
        f"- **Repository:** `{repo}`\n"
        f"- **Why this matters:** {one_line_why}\n"
        f"- **Original issue:** {original_url}\n"
        f"- **Impact score:** {impact_score}/10\n\n"
        "+1 to vote FOR | -1 to vote AGAINST"
    )


def create_github_discussion(token: str, repo: str, title: str, body: str) -> dict[str, str]:
    """Creates a GitHub Discussion in the given repo (always OWN_REPO)."""
    if not token.strip():
        LOGGER.error("Missing GitHub token; cannot create discussion.")
        return {"id": "", "url": ""}

    try:
        owner, name = repo.split("/", maxsplit=1)
    except ValueError:
        LOGGER.error("Invalid repository format: %s", repo)
        return {"id": "", "url": ""}

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    endpoint = "https://api.github.com/graphql"

    repo_query = """
    query GetRepoInfo($owner: String!, $name: String!) {
      repository(owner: $owner, name: $name) {
        id
        discussionCategories(first: 10) {
          nodes {
            id
            name
          }
        }
      }
    }
    """

    try:
        repo_response = requests.post(
            endpoint,
            headers=headers,
            json={"query": repo_query, "variables": {"owner": owner, "name": name}},
            timeout=30,
        )
        repo_response.raise_for_status()
        repo_payload = repo_response.json()
    except (requests.RequestException, ValueError) as error:
        LOGGER.error("Failed fetching repo discussion info: %s", error)
        return {"id": "", "url": ""}

    if repo_payload.get("errors"):
        LOGGER.error("GraphQL repo query errors: %s", repo_payload["errors"])
        return {"id": "", "url": ""}

    repository = repo_payload.get("data", {}).get("repository", {})
    repository_id = repository.get("id")
    categories = repository.get("discussionCategories", {}).get("nodes", [])

    preferred_names = {"general", "ideas", "polls", "community"}
    category_id = None
    for cat in categories:
        if str(cat.get("name", "")).lower() in preferred_names:
            category_id = cat.get("id")
            break
    if not category_id and categories:
        category_id = categories[0].get("id")

    if not repository_id or not category_id:
        LOGGER.error(
            "Missing repository/category IDs for repo %s. "
            "Make sure GitHub Discussions are ENABLED on the repo.",
            repo,
        )
        return {"id": "", "url": ""}

    create_mutation = """
    mutation CreateDiscussion(
      $repositoryId: ID!,
      $categoryId: ID!,
      $title: String!,
      $body: String!
    ) {
      createDiscussion(input: {
        repositoryId: $repositoryId,
        categoryId: $categoryId,
        title: $title,
        body: $body
      }) {
        discussion {
          id
          url
        }
      }
    }
    """

    variables = {
        "repositoryId": repository_id,
        "categoryId": category_id,
        "title": _safe_str(title),
        "body": _safe_str(body),
    }
    try:
        create_response = requests.post(
            endpoint,
            headers=headers,
            json={"query": create_mutation, "variables": variables},
            timeout=30,
        )
        create_response.raise_for_status()
        create_payload = create_response.json()
    except (requests.RequestException, ValueError) as error:
        LOGGER.error("Failed creating GitHub discussion: %s", error)
        return {"id": "", "url": ""}

    if create_payload.get("errors"):
        LOGGER.error("GraphQL discussion mutation errors: %s", create_payload["errors"])
        return {"id": "", "url": ""}

    discussion = create_payload.get("data", {}).get("createDiscussion", {}).get("discussion", {})
    discussion_id = str(discussion.get("id", ""))
    discussion_url = str(discussion.get("url", ""))
    if not discussion_id or not discussion_url:
        LOGGER.error("Missing discussion id/url in GraphQL response.")
        return {"id": "", "url": ""}

    return {"id": discussion_id, "url": discussion_url}


def update_readme_vote_section(votes: dict[str, Any]) -> None:
    try:
        from scripts.readme_generator import replace_section
    except ImportError:
        import sys
        from pathlib import Path as _Path
        sys.path.insert(0, str(_Path(__file__).parent))
        from readme_generator import replace_section

    if votes and _safe_str(votes.get("discussion_url", "")).strip():
        discussion_url = _safe_str(votes.get("discussion_url", ""))
        current_issue_title = _safe_str(votes.get("current_issue_title", ""))
        section_body = (
            "## \U0001f5f3\ufe0f Community Vote\n\n"
            "Should we implement this?\n"
            f"**[{current_issue_title}]({discussion_url})**\n"
            f"> Vote on GitHub Discussions \u2192 [{discussion_url}]({discussion_url})"
        )
    else:
        section_body = (
            "## \U0001f5f3\ufe0f Community Vote\n"
            "> *Vote opens daily after the resurrection is published.*"
        )

    section = (
        "<!-- SECTION:community-vote -->\n"
        f"{section_body}\n"
        "<!-- END:community-vote -->"
    )

    readme_path = Path(STATS_FILE).parent.parent / "README.md"
    current_content = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""
    updated_content = replace_section(current_content, "community-vote", section)
    readme_path.write_text(updated_content, encoding="utf-8")
    LOGGER.info("Written: %s", readme_path)


def run_vote(meta: dict[str, Any], token: str) -> None:
    discussion_title = _safe_str(f"Should we implement: {meta.get('title', '')}?")
    discussion_body = build_vote_body(meta)
    discussion = create_github_discussion(token, OWN_REPO, discussion_title, discussion_body)

    votes_data = {
        "current_issue_title": _safe_str(meta.get("title", "")),
        "current_issue_url": _safe_str(meta.get("original_url", "")),
        "discussion_url": _safe_str(discussion.get("url", "")),
        "discussion_id": _safe_str(discussion.get("id", "")),
        "vote_date": datetime.now().strftime("%Y-%m-%d"),
        "votes_for": 0,
        "votes_against": 0,
        "status": "open",
    }
    save_votes(votes_data)
    update_readme_vote_section(votes_data)
    LOGGER.info("Vote created: %s", votes_data["discussion_url"])


if __name__ == "__main__":
    import os
    from dotenv import load_dotenv

    load_dotenv()
    token = os.environ.get("GITHUB_TOKEN", "")

    meta_path = Path(STATS_FILE).parent.parent / "resurrections"
    candidates = sorted(meta_path.glob("day-*/meta.json"), reverse=True)
    if candidates:
        with candidates[0].open(encoding="utf-8") as handle:
            meta = json.load(handle)
        run_vote(meta, token)
    else:
        print("No resurrection found to vote on.")
