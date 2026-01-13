from pydantic import BaseModel, HttpUrl
from datetime import datetime
from typing import Optional

class ProjectBase(BaseModel):
    name: str
    github_url: str
    branch: Optional[str] = "main"

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(ProjectBase):
    name: Optional[str] = None
    github_url: Optional[str] = None

class Project(ProjectBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
