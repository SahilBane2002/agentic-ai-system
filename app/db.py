from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, JSON, DateTime, ForeignKey, create_engine
from sqlalchemy.orm import DeclarativeBase, relationship, sessionmaker
from app.config import settings


class Base(DeclarativeBase):
    pass


class WorkflowORM(Base):
    __tablename__ = "workflows"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    status = Column(String, nullable=False, default="created")
    goal = Column(Text, default="")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    tasks = relationship("TaskORM", back_populates="workflow", cascade="all, delete-orphan")


class TaskORM(Base):
    __tablename__ = "tasks"

    id = Column(String, primary_key=True)
    workflow_id = Column(String, ForeignKey("workflows.id"), nullable=False)
    type = Column(String, nullable=False)
    state = Column(String, nullable=False, default="pending")
    payload = Column(JSON, default=dict)
    result = Column(JSON, nullable=True)
    workflow = relationship("WorkflowORM", back_populates="tasks")


def _make_engine():
    url = settings.database_url
    connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
    return create_engine(url, connect_args=connect_args)


engine = _make_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
