import requests
from typing import Dict, Optional

class GithubService:
    def __init__(self, access_token: Optional[str] = None):
        """
        Initialize the GitHub service.

        Args:
            access_token (str, optional): GitHub personal access token
        """
        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github.v3+json"
        }
        if access_token:
            self.headers["Authorization"] = f"Bearer {access_token}"

    def get_current_user(self) -> Dict:
        """
        Get details of the authenticated user.

        Returns:
            Dict: User information including login, name, email, etc.

        Raises:
            requests.exceptions.RequestException: If the API request fails
        """
        response = requests.get(
            f"{self.base_url}/user",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def get_repository_details(self, repo: str) -> Dict:
        """
        Get details of a specific repository.

        Args:
            owner (str): Repository owner's username
            repo (str): Repository name

        Returns:
            Dict: Repository information including name, description, stars, etc.

        Raises:
            requests.exceptions.RequestException: If the API request fails
        """
        response = requests.get(
            f"{self.base_url}/repos/{repo}",
            headers=self.headers
        )
        response.raise_for_status()
        return response

    def check_repo_access(self, repo: str) -> Dict:
        """
        Check if the authenticated user has read and write access to a specific repository.

        Args:
            repo (str): Repository name in the format "owner/repo"
        """
        response = self.get_repository_details(repo)
        if response.status_code == 404:
            return {
                "has_access": False,
                "detail": "Repository not found or no access"
            }
        elif response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to check repository access"
            )

        repo_data = response.json()
        permissions = repo_data.get("permissions", {})

        return {
            "has_access": True,
            "permissions": {
                "admin": permissions.get("admin", False),
                "push": permissions.get("push", False),
                "pull": permissions.get("pull", False)
            }
        }