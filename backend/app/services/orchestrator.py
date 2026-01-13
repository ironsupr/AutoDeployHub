from sqlalchemy.orm import Session
from app.models.project import Project
from app.models.deployment import Deployment
from app.services.git import git_service
from app.services.docker import docker_service
from app.services.k8s import k8s_service
from datetime import datetime

class Orchestrator:
    def trigger_deployment(self, db: Session, project: Project, commit_hash: str):
        # 1. Create Deployment record
        deployment = Deployment(
            project_id=project.id,
            commit_hash=commit_hash,
            status="building",
            logs=""
        )
        db.add(deployment)
        db.commit()
        db.refresh(deployment)
        
        def add_log(message: str):
            timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            deployment.logs += f"[{timestamp}] {message}\n"
            db.commit()

        try:
            add_log(f"Starting deployment for {project.name}...")
            
            # 2. Clone Repo
            add_log(f"Cloning repository: {project.github_url} (branch: {project.branch})")
            project_path = git_service.clone_repo(project.github_url, project.name, project.branch)
            add_log("Clone successful.")
            
            # 3. Build Image
            image_name = f"autodeployhub/{project.name}"
            tag = commit_hash[:7] if commit_hash and commit_hash != "manual" else "latest"
            add_log(f"Building Docker image: {image_name}:{tag}")
            
            deployment.status = "building"
            db.commit()
            
            full_image_name, build_logs = docker_service.build_image(project_path, image_name, tag)
            deployment.logs += "\n--- DOCKER BUILD LOGS ---\n"
            deployment.logs += build_logs
            deployment.logs += "\n-------------------------\n"
            add_log(f"Image built successfully: {full_image_name}")
            
            deployment.status = "deploying"
            db.commit()
            
            # 4. Deploy to K8s
            add_log(f"Deploying to Kubernetes cluster...")
            success = k8s_service.deploy_project(project.name.lower(), full_image_name)
            
            if success:
                add_log("Kubernetes deployment/update applied successfully.")
                deployment.status = "success"
            else:
                add_log("ERROR: Kubernetes deployment failed.")
                deployment.status = "failed"
            
        except Exception as e:
            add_log(f"FATAL ERROR: {str(e)}")
            deployment.status = "failed"
        
        deployment.finished_at = datetime.utcnow()
        add_log(f"Deployment process finished with status: {deployment.status}")
        db.commit()
        return deployment

orchestrator = Orchestrator()
