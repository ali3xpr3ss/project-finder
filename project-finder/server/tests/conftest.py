import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.database import Base
from core.config import settings
from fastapi.testclient import TestClient
from main import app
from core.security import create_access_token
from models.user import User
from models.project import Project

# Создаем тестовую базу данных
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
def db_engine():
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db(db_engine):
    connection = db_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope="function")
def client():
    return TestClient(app)

@pytest.fixture(scope="function")
def test_user(db):
    user = User(
        email="test@example.com",
        name="Test User",
        hashed_password="hashed_password",
        role="user"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture(scope="function")
def test_admin(db):
    admin = User(
        email="admin@example.com",
        name="Admin User",
        hashed_password="hashed_password",
        role="admin"
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin

@pytest.fixture(scope="function")
def test_user_token(test_user):
    return create_access_token({"sub": test_user.email})

@pytest.fixture(scope="function")
def test_admin_token(test_admin):
    return create_access_token({"sub": test_admin.email})

@pytest.fixture(scope="function")
def test_project(db, test_user):
    project = Project(
        name="Test Project",
        description="Test Description",
        user_id=test_user.id,
        required_roles=["developer", "designer"],
        technologies=["Python", "FastAPI", "React"]
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project 