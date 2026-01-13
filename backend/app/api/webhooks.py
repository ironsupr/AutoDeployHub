from fastapi import APIRouter, Request, Header, HTTPException
import hmac
import hashlib
from app.core.config import settings

router = APIRouter()

@router.post("/github")
async def github_webhook(
    request: Request,
    x_hub_signature_256: str = Header(None)
):
    # In a real app, you'd verify the signature here
    # For MVP, we'll just log the event
    payload = await request.json()
    
    event = request.headers.get("X-GitHub-Event")
    if event == "push":
        repo_url = payload.get("repository", {}).get("clone_url")
        branch = payload.get("ref", "").replace("refs/heads/", "")
        commit_hash = payload.get("after")
        
        print(f"Received push for {repo_url} branch {branch} commit {commit_hash}")
        # TODO: Trigger deployment logic
        return {"message": "Webhook received", "action": "trigger_deploy"}
    
    return {"message": "Webhook received", "action": "none"}
