from __future__ import annotations

import json
import logging
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
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    LOGGER.info("Written: %s", path)


def build_vote_body(meta: dict[str, Any]) -> str:
    title = str(meta.get("title", ""))
    repo = str(meta.get("repo", ""))
    one_line_why = str(meta.get("one_line_why", ""))
    original_url = str(meta.get("original_url", ""))
    impact_score = int(meta.get("impact_score", 0))

    return (
        f"## Community Vote: {title}\n\n"
        f"- **Repository:** `{repo}`\n"
        f"- **Why this matters:** {one_line_why}\n"
        f"- **Original issue:** {original_url}\n"
        f"- **Impact score:** {impact_score}/10\n\n"
        "👍 React with +1 to vote FOR | 👎 React with -1 to vote AGAINST"
    )


def create_github_discussion(token: str, repo: str, title: str, body: str) -> dict[str, str]:
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
    first_category = categories[0] if isinstance(categories, list) and categories else {}
    category_id = first_category.get("id")

    if not repository_id or not category_id:
        LOGGER.error("Missing repository/category IDs for repo %s", repo)
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
        "title": title,
        "body": body,
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
