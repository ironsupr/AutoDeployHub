from fastapi import FastAPI
from app.api.webhooks import router as webhook_router
from app.api.projects import router as project_router
from app.api.dashboard import router as dashboard_router
from app.api.auth import router as auth_router
from app.api.images import router as image_router

app = FastAPI(title="AutoDeployHub API")

app.include_router(webhook_router, prefix="/webhooks", tags=["webhooks"])
app.include_router(project_router, prefix="/projects", tags=["projects"])
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(image_router, prefix="/admin", tags=["images"])
app.include_router(dashboard_router, tags=["dashboard"])

@app.get("/")
async def root():
    return {"message": "Welcome to AutoDeployHub API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
