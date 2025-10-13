import pytest
import asyncio
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from httpx import AsyncClient
from faker import Faker

from app.main import app
from app.database import get_db
from app.models import Base, SearchItem
from app.config import settings

# Test database URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Create test engine
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
)

TestSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create test database session"""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with TestSessionLocal() as session:
        yield session
    
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create test client"""
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def faker_instance():
    """Create Faker instance"""
    return Faker(['ko_KR', 'en_US'])


@pytest.fixture(scope="function")
async def sample_items(db_session: AsyncSession, faker_instance: Faker):
    """Create sample search items"""
    items = []
    categories = ['전자제품', '의류', '도서', '식품', '가구', '스포츠', '완구', '화장품']
    
    for i in range(100):
        item = SearchItem(
            title=faker_instance.sentence(nb_words=3),
            description=faker_instance.text(max_nb_chars=200),
            category=faker_instance.random_element(categories),
            tags=','.join(faker_instance.words(nb=3)),
            price=round(faker_instance.random.uniform(1000, 1000000), 2),
            popularity=faker_instance.random_int(0, 1000)
        )
        items.append(item)
        db_session.add(item)
    
    await db_session.commit()
    return items


@pytest.fixture(scope="function")
def test_queries():
    """Test query patterns"""
    return [
        {"q": "테스트", "category": None, "sort": "relevance"},
        {"q": "검색", "category": "전자제품", "sort": "price"},
        {"q": "상품", "category": None, "sort": "popularity"},
        {"q": "아이템", "category": "의류", "sort": "date"},
    ]

