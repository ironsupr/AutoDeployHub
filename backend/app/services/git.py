import os
import subprocess
import shutil
from pathlib import Path

class GitService:
    def __init__(self, base_path: str = "/tmp/autodeployhub"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def clone_repo(self, repo_url: str, project_name: str, branch: str = "main") -> Path:
        project_path = self.base_path / project_name
        
        # Clean up if exists
        if project_path.exists():
            shutil.rmtree(project_path)
            
        try:
            subprocess.run(
                ["git", "clone", "--branch", branch, repo_url, str(project_path)],
                check=True,
                capture_output=True,
                text=True
            )
            return project_path
        except subprocess.CalledProcessError as e:
            print(f"Error cloning repo: {e.stderr}")
            raise Exception(f"Failed to clone repository: {e.stderr}")

git_service = GitService()
