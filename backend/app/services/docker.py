import subprocess
from pathlib import Path

class DockerService:
    def build_image(self, project_path: Path, image_name: str, tag: str = "latest"):
        """
        Builds a docker image from a Dockerfile in the project_path.
        """
        full_image_name = f"{image_name}:{tag}"
        
        try:
            # Check if Dockerfile exists
            if not (project_path / "Dockerfile").exists():
                raise Exception("Dockerfile not found in project root")

            print(f"Building Docker image {full_image_name}...")
            result = subprocess.run(
                ["docker", "build", "-t", full_image_name, "."],
                cwd=str(project_path),
                check=True,
                capture_output=True,
                text=True
            )
            return full_image_name, result.stdout
        except subprocess.CalledProcessError as e:
            print(f"Docker build failed: {e.stderr}")
            raise Exception(f"Docker build failed: {e.stderr}")

    def delete_image(self, image_id: str):
        """
        Deletes a Docker image by ID.
        """
        try:
            print(f"Deleting Docker image {image_id}...")
            subprocess.run(
                ["docker", "rmi", "-f", image_id],
                check=True,
                capture_output=True,
                text=True
            )
            return True
        except subprocess.CalledProcessError as e:
            print(f"Docker delete failed: {e.stderr}")
            raise Exception(f"Docker delete failed: {e.stderr}")

    def list_images(self, filter_name: str = "autodeployhub"):
        """
        Lists Docker images, optionally filtered by name.
        """
        try:
            # Format: ID|Repository|Tag|CreatedAt
            result = subprocess.run(
                ["docker", "images", "--filter", f"reference={filter_name}*", "--format", "{{.ID}}|{{.Repository}}|{{.Tag}}|{{.CreatedAt}}"],
                check=True,
                capture_output=True,
                text=True
            )
            images = []
            for line in result.stdout.strip().split("\n"):
                if not line: continue
                parts = line.split("|")
                images.append({
                    "id": parts[0],
                    "repository": parts[1],
                    "tag": parts[2],
                    "created_at": parts[3]
                })
            return images
        except subprocess.CalledProcessError as e:
            print(f"Docker list failed: {e.stderr}")
            return []

docker_service = DockerService()
