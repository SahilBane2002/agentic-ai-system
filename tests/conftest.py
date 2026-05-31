import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

os.environ.setdefault("GROQ_API_KEY", "dummy-key-for-tests")
os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")

from app.main import app
from app.db import Base, get_db

_engine = create_engine("sqlite:///./test.db", connect_args={"check_same_thread": False})
_Session = sessionmaker(autocommit=False, autoflush=False, bind=_engine)


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=_engine)
    yield
    Base.metadata.drop_all(bind=_engine)


@pytest.fixture
def db_session():
    db = _Session()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c
    app.dependency_overrides.clear()
