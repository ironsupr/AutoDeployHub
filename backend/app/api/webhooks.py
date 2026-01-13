from fastapi import APIRouter, Request, Header, HTTPException, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.project import Project
from app.services.orchestrator import orchestrator
import hmac
import hashlib
from app.core.config import settings

router = APIRouter()

@router.post("/github")
async def github_webhook(
    request: Request,
    db: Session = Depends(get_db),
    x_hub_signature_256: str = Header(None)
):
    # Verify signature
    if settings.GITHUB_WEBHOOK_SECRET:
        if not x_hub_signature_256:
            raise HTTPException(status_code=401, detail="X-Hub-Signature-256 header missing")
        
        body = await request.body()
        signature = hmac.new(
            settings.GITHUB_WEBHOOK_SECRET.encode(),
            body,
            hashlib.sha256
        ).hexdigest()
        
        if not hmac.compare_digest(f"sha256={signature}", x_hub_signature_256):
            raise HTTPException(status_code=401, detail="Invalid signature")
    
    payload = await request.json()
    
    event = request.headers.get("X-GitHub-Event")
    if event == "push":
        repo_url = payload.get("repository", {}).get("clone_url")
        # Handle both ssh and https urls if needed, for MVP we focus on exact match or basic transform
        
        project = db.query(Project).filter(Project.github_url == repo_url).first()
        if not project:
            # Try without .git suffix
            if repo_url.endswith(".git"):
                project = db.query(Project).filter(Project.github_url == repo_url[:-4]).first()
        
        if not project:
            return {"message": "Project not registered", "url": repo_url}

        branch = payload.get("ref", "").replace("refs/heads/", "")
        if branch != project.branch:
            return {"message": "Push to non-monitored branch", "branch": branch}

        commit_hash = payload.get("after")
        
        print(f"Triggering deployment for {project.name}...")
        # In a real environment, this should be a background task (celery/arq)
        # For MVP we'll run it and return
        deployment = orchestrator.trigger_deployment(db, project, commit_hash)
        
        return {"message": "Deployment triggered", "deployment_id": deployment.id}
    
    return {"message": "Webhook received", "action": "none"}
