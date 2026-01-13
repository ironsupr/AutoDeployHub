import os
from jinja2 import Template
from kubernetes import client, config, utils
from pathlib import Path
import yaml

class K8sService:
    def __init__(self):
        # Try to load in-cluster config, fallback to kube_config
        try:
            config.load_incluster_config()
        except config.ConfigException:
            try:
                config.load_kube_config()
            except config.ConfigException:
                print("Warning: Could not load Kubernetes config. K8s operations will fail.")

    def deploy_project(self, project_name: str, image_name: str, container_port: int = 8000):
        # Load template
        template_path = Path(__file__).parent.parent / "templates" / "k8s_deployment.yaml.j2"
        with open(template_path) as f:
            template = Template(f.read())
        
        # Render manifest
        manifest_yaml = template.render(
            project_name=project_name,
            image_name=image_name,
            container_port=container_port
        )
        
        # Save to temp file to use with utils.create_from_yaml
        temp_manifest = Path(f"/tmp/{project_name}-manifest.yaml")
        temp_manifest.parent.mkdir(parents=True, exist_ok=True)
        with open(temp_manifest, "w") as f:
            f.write(manifest_yaml)
            
        try:
            k8s_client = client.ApiClient()
            utils.create_from_yaml(k8s_client, str(temp_manifest), verbose=True)
            return True
        except utils.FailToCreateError as e:
            # If it already exists, we might want to patch/replace (for MVP we'll just log)
            print(f"Deployment already exists or failed to create: {e}")
            # In a real app, you would handle 'Replace' logic here
            return False
        finally:
            if temp_manifest.exists():
                os.remove(temp_manifest)

    def update_image(self, project_name: str, image_name: str):
        """
        Updates an existing deployment to use a new image.
        """
        try:
            api_instance = client.AppsV1Api()
            # Read current deployment
            deployment = api_instance.read_namespaced_deployment(name=project_name, namespace="default")
            
            # Update image
            deployment.spec.template.spec.containers[0].image = image_name
            
            # Patch deployment
            api_instance.patch_namespaced_deployment(name=project_name, namespace="default", body=deployment)
            return True
        except Exception as e:
            print(f"K8s Patch failed: {str(e)}")
            return False

k8s_service = K8sService()
