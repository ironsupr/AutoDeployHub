from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from app.db.session import Base

class Deployment(Base):
    __tablename__ = "deployments"

    id: int = Column(Integer, primary_key=True, index=True)
    project_id: int = Column(Integer, ForeignKey("projects.id"))
    commit_hash: str = Column(String)
    status: str = Column(String)  # pending, building, deploying, success, failed
    logs: str = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    finished_at = Column(DateTime(timezone=True), nullable=True)
