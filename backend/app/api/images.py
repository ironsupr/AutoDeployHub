from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from app.services.docker import docker_service
from app.api.auth import get_current_user

router = APIRouter()

@router.get("/images")
async def list_docker_images(user: str = Depends(get_current_user)):
    if not user:
        return RedirectResponse(url="/auth/login")
    return docker_service.list_images()

@router.post("/images/{image_id}/delete")
async def delete_docker_image(image_id: str, user: str = Depends(get_current_user)):
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    try:
        docker_service.delete_image(image_id)
        return {"message": f"Image {image_id} deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
