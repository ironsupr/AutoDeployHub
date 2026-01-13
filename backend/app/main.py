from fastapi import FastAPI
from app.api.webhooks import router as webhook_router

app = FastAPI(title="AutoDeployHub API")

app.include_router(webhook_router, prefix="/webhooks", tags=["webhooks"])

@app.get("/")
async def root():
    return {"message": "Welcome to AutoDeployHub API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
