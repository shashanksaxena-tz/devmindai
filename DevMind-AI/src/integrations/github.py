"""GitHub integration client."""

import os
from typing import Any

from github import Auth, Github, GithubException

from src.core.config import settings


class GitHubClient:
    """Wrapper around PyGitHub client."""

    def __init__(self, token: str | None = None):
        """Initialize GitHub client."""
        auth = None
        if token:
            auth = Auth.Token(token)

        self.gh = Github(auth=auth)

    def get_pull(self, owner: str, repo_name: str, number: int) -> dict[str, Any]:
        """Get PR details."""
        repo = self.gh.get_repo(f"{owner}/{repo_name}")
        pr = repo.get_pull(number)

        return {
            "number": pr.number,
            "title": pr.title,
            "body": pr.body,
            "base": {"ref": pr.base.ref},
            "head": {"sha": pr.head.sha},
            "labels": [{"name": l.name} for l in pr.labels],
            "user": {"login": pr.user.login},
            "requested_reviewers": [{"login": r.login} for r in pr.requested_reviewers],
        }

    def get_pr_files(self, owner: str, repo_name: str, number: int) -> list[dict[str, Any]]:
        """Get files changed in PR."""
        repo = self.gh.get_repo(f"{owner}/{repo_name}")
        pr = repo.get_pull(number)
        files = pr.get_files()

        return [
            {
                "filename": f.filename,
                "status": f.status,
                "patch": f.patch,
                "additions": f.additions,
                "deletions": f.deletions,
                "changes": f.changes,
            }
            for f in files
        ]

    def search_code(self, owner: str, repo_name: str, query: str) -> list[dict[str, Any]]:
        """Search code in repo."""
        full_query = f"{query} repo:{owner}/{repo_name}"
        results = self.gh.search_code(full_query)
        return [{"path": f.path} for f in results]

    def get_file_content(self, owner: str, repo_name: str, path: str, ref: str) -> str | bytes:
        """Get file content at ref."""
        repo = self.gh.get_repo(f"{owner}/{repo_name}")
        try:
            content_file = repo.get_contents(path, ref=ref)
            if isinstance(content_file, list):
                raise ValueError(f"Path {path} points to a directory")
            return content_file.decoded_content
        except GithubException:
            # Re-raise or handle? ContextGatherer catches Exception.
            raise

    def get_commits(self, owner: str, repo_name: str, path: str, per_page: int = 10) -> list[dict[str, Any]]:
        """Get recent commits for a file."""
        repo = self.gh.get_repo(f"{owner}/{repo_name}")
        commits = repo.get_commits(path=path)

        result = []
        for i, c in enumerate(commits):
            if i >= per_page:
                break
            result.append({
                "sha": c.sha,
                "commit": {
                    "message": c.commit.message,
                    "author": {
                        "name": c.commit.author.name,
                        "date": c.commit.author.date.isoformat() if c.commit.author.date else None
                    }
                }
            })
        return result


def get_github_client() -> GitHubClient:
    """Get GitHub client instance."""
    # Try to get token from env var as it's not in settings
    token = os.environ.get("GITHUB_TOKEN")
    return GitHubClient(token=token)
