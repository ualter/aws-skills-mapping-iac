import os
from dataclasses import dataclass


@dataclass
class GitHubConnection:
    Repository: str
    ConnectionArn: str
    Owner: str
    TrunkBranch: str


class Repositories:
    def __init__(self) -> None:
        self._GITHUB_CONNECTION_ARN = os.environ.get(
            "CDK_GITHUB_CONNECTION_ARN", "NOTSETENVVAR_CDK_GITHUB_CONNECTION_ARN"
        )
        self._GITHUB_OWNER = os.environ.get(
            "CDK_GITHUB_OWNER", "NOTSETENVVAR_CDK_GITHUB_OWNER"
        )
        self._GITHUB_REPO = os.environ.get(
            "CDK_GITHUB_REPO", "NOTSETENVVAR_CDK_GITHUB_REPO"
        )
        self._GITHUB_TRUNK_BRANCH = os.environ.get(
            "CDK_GITHUB_TRUNK_BRANCH", "NOTSETENVVAR_CDK_GITHUB_TRUNK_BRANCH"
        )

    def github_connection(self) -> GitHubConnection:
        g = GitHubConnection(
            Repository=self._GITHUB_REPO,
            ConnectionArn=self._GITHUB_CONNECTION_ARN,
            Owner=self._GITHUB_OWNER,
            TrunkBranch=self._GITHUB_TRUNK_BRANCH,
        )
        return g
