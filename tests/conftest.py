import pytest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import StaticPool
from app.main import app
from app.core.database import get_db, Base
from httpx import ASGITransport, AsyncClient

# Use an in-memory SQLite database
# StaticPool is required to keep the in-memory connection open across the session
SQLITE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(
    SQLITE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = async_sessionmaker(
    autocommit=False, autoflush=False, bind=engine, class_=AsyncSession
)


@pytest.fixture
async def client_fixture():
    """Provides an AsyncClient bound to the FastAPI app."""
    # We use ASGITransport to talk directly to the app without a real network
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test session."""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
async def setup_database():
    """Create tables once at the start of the test session."""
    # This loop_scope="session" tells pytest-asyncio to use the session loop
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# 2. Ensure your db_session is function scoped (default)
@pytest.fixture
async def db_session():
    """Provides a clean session and rolls back after every test."""
    async with TestingSessionLocal() as session:
        yield session
        await session.rollback()


# 3. Apply the override
@pytest.fixture(autouse=True)
def override_get_db(db_session):
    app.dependency_overrides[get_db] = lambda: db_session
