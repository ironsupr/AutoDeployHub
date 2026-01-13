from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.db.session import Base

class Project(Base):
    __tablename__ = "projects"

    id: int = Column(Integer, primary_key=True, index=True)
    name: str = Column(String, index=True)
    github_url: str = Column(String, unique=True, index=True)
    branch: str = Column(String, default="main")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
