# Projeto Desenvolvido na Data Science Academy
"""Fixtures de teste — Banco em memoria, client HTTP e dados mock."""

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database import Base, dsa_get_db
from app.main import app
from app.models.customer import Customer
from app.models.order import Order, OrderItem
from app.models.product import Product

# Banco SQLite em memoria para testes
TEST_DATABASE_URL = "sqlite+aiosqlite://"

engine_test = create_async_engine(TEST_DATABASE_URL, echo=False)
async_session_test = async_sessionmaker(engine_test, class_=AsyncSession, expire_on_commit=False)


async def dsa_override_get_db():
    """Override da dependency dsa_get_db para usar DB de teste."""
    async with async_session_test() as session:
        try:
            yield session
        finally:
            await session.close()


app.dependency_overrides[dsa_get_db] = dsa_override_get_db


@pytest_asyncio.fixture(autouse=True)
async def dsa_setup_database():
    """Cria e destroi tabelas para cada teste."""
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def dsa_db_session():
    """Fixture de sessao de banco de dados."""
    async with async_session_test() as session:
        yield session


@pytest_asyncio.fixture
async def dsa_client():
    """Fixture de AsyncClient para testar endpoints."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test", follow_redirects=True) as ac:
        yield ac


@pytest_asyncio.fixture
async def dsa_sample_products(dsa_db_session: AsyncSession):
    """Fixture de produtos de teste."""
    products = [
        Product(
            id="PROD-001",
            name="iPhone 15 Pro 256GB",
            description="Smartphone Apple com chip A17 Pro",
            category="smartphones",
            brand="Apple",
            price=7999.90,
            stock=45,
            specs={"display": "6.1 OLED", "processor": "A17 Pro"},
            image_url="/static/products/iphone-15-pro.jpg",
            rating=4.8,
            reviews_count=1247,
        ),
        Product(
            id="PROD-002",
            name="Galaxy S24 Ultra 512GB",
            description="Smartphone Samsung com S Pen integrada",
            category="smartphones",
            brand="Samsung",
            price=6499.90,
            stock=30,
            specs={"display": "6.8 AMOLED", "processor": "Snapdragon 8 Gen 3"},
            rating=4.7,
            reviews_count=890,
        ),
        Product(
            id="PROD-009",
            name="MacBook Air M3 256GB",
            description="Notebook Apple ultrafino com chip M3",
            category="notebooks",
            brand="Apple",
            price=12499.90,
            stock=20,
            specs={"display": "13.6 Liquid Retina", "processor": "M3"},
            rating=4.9,
            reviews_count=567,
        ),
        Product(
            id="PROD-020",
            name="Carregador USB-C 65W",
            description="Carregador rapido universal",
            category="acessorios",
            brand="Anker",
            price=249.90,
            stock=0,
            specs={"potencia": "65W", "portas": "2x USB-C"},
            rating=4.5,
            reviews_count=234,
        ),
    ]
    for p in products:
        dsa_db_session.add(p)
    await dsa_db_session.commit()
    return products


@pytest_asyncio.fixture
async def dsa_sample_customer(dsa_db_session: AsyncSession):
    """Fixture de cliente de teste."""
    customer = Customer(
        id="CUST-001",
        name="Maria Silva",
        email="maria.silva@email.com",
    )
    dsa_db_session.add(customer)
    await dsa_db_session.commit()
    return customer


@pytest_asyncio.fixture
async def dsa_sample_orders(dsa_db_session: AsyncSession, dsa_sample_customer, dsa_sample_products):
    """Fixture de pedidos de teste."""
    order = Order(
        id="ORD-001",
        customer_id="CUST-001",
        status="shipped",
        total=7999.90,
        tracking_code="BR100000001XX",
    )
    item = OrderItem(
        id="ORD-001-PROD-001",
        order_id="ORD-001",
        product_id="PROD-001",
        quantity=1,
        unit_price=7999.90,
    )
    dsa_db_session.add(order)
    dsa_db_session.add(item)
    await dsa_db_session.commit()
    return [order]
