from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.project import Project
from app.models.deployment import Deployment
from app.api.auth import get_current_user
from app.services.docker import docker_service
from pathlib import Path

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).parent.parent / "templates"))

@router.get("/dashboard")
async def dashboard(request: Request, db: Session = Depends(get_db), user: str = Depends(get_current_user)):
    if not user:
        return RedirectResponse(url="/auth/login")
    
    projects = db.query(Project).all()
    deployments = db.query(Deployment).order_by(Deployment.created_at.desc()).limit(10).all()
    images = docker_service.list_images()
    
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request, 
            "projects": projects, 
            "deployments": deployments, 
            "images": images,
            "user": user
        }
    )

@router.get("/project/{project_id}")
async def project_detail(request: Request, project_id: int, db: Session = Depends(get_db), user: str = Depends(get_current_user)):
    if not user:
        return RedirectResponse(url="/auth/login")
        
    project = db.query(Project).filter(Project.id == project_id).first()
    deployments = db.query(Deployment).filter(Deployment.project_id == project_id).order_by(Deployment.created_at.desc()).all()
    return templates.TemplateResponse(
        "project_detail.html",
        {"request": request, "project": project, "deployments": deployments, "user": user}
    )
