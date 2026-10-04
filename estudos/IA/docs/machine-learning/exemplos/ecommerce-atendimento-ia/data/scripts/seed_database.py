# Projeto Desenvolvido na Data Science Academy

"""Script de seed — Carrega dados iniciais no PostgreSQL.

Lê os arquivos JSON de data/ e insere produtos, clientes, pedidos e itens
no banco de dados. Idempotente via ON CONFLICT DO NOTHING.
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from pathlib import Path
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://ecommerce_user:ecommerce_pass@localhost:5432/ecommerce",
)

DATA_DIR = Path(__file__).parent.parent


def dsa_load_json(filename: str) -> list[dict]:
    """Carrega um arquivo JSON do diretório data/."""
    filepath = DATA_DIR / filename
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def dsa_parse_dt(value: str) -> datetime:
    """Converte string ISO 8601 para datetime naive (UTC).

    asyncpg requer datetime naive para colunas TIMESTAMP WITH TIME ZONE.
    """
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return dt.replace(tzinfo=None)


async def dsa_seed_products(session: AsyncSession, products: list[dict]) -> int:
    """Insere produtos no banco de dados."""
    count = 0
    for p in products:
        result = await session.execute(
            text("""
                INSERT INTO products (id, name, description, category, brand, price, stock, specs, image_url, rating, reviews_count, created_at)
                VALUES (:id, :name, :description, :category, :brand, :price, :stock, CAST(:specs AS jsonb), :image_url, :rating, :reviews_count, NOW())
                ON CONFLICT (id) DO NOTHING
            """),
            {
                "id": p["id"],
                "name": p["name"],
                "description": p["description"],
                "category": p["category"],
                "brand": p["brand"],
                "price": p["price"],
                "stock": p["stock"],
                "specs": json.dumps(p["specs"]),  # CAST AS jsonb no SQL
                "image_url": p["image_url"],
                "rating": p["rating"],
                "reviews_count": p["reviews_count"],
            },
        )
        count += result.rowcount
    return count


async def dsa_seed_customers(session: AsyncSession, customers: list[dict]) -> int:
    """Insere clientes no banco de dados."""
    count = 0
    for c in customers:
        result = await session.execute(
            text("""
                INSERT INTO customers (id, name, email, created_at)
                VALUES (:id, :name, :email, :created_at)
                ON CONFLICT (id) DO NOTHING
            """),
            {
                "id": c["id"],
                "name": c["name"],
                "email": c["email"],
                "created_at": dsa_parse_dt(c["created_at"]),
            },
        )
        count += result.rowcount
    return count


async def dsa_seed_orders(session: AsyncSession, orders: list[dict]) -> int:
    """Insere pedidos e itens de pedido no banco de dados."""
    order_count = 0
    for o in orders:
        result = await session.execute(
            text("""
                INSERT INTO orders (id, customer_id, status, total, tracking_code, created_at, updated_at)
                VALUES (:id, :customer_id, :status, :total, :tracking_code, :created_at, :updated_at)
                ON CONFLICT (id) DO NOTHING
            """),
            {
                "id": o["id"],
                "customer_id": o["customer_id"],
                "status": o["status"],
                "total": o["total"],
                "tracking_code": o.get("tracking_code"),
                "created_at": dsa_parse_dt(o["created_at"]),
                "updated_at": dsa_parse_dt(o["updated_at"]),
            },
        )
        # Insere itens somente se o pedido foi inserido (idempotência)
        if result.rowcount > 0:
            order_count += 1
            for item in o["items"]:
                item_id = f"{o['id']}-{item['product_id']}"
                await session.execute(
                    text("""
                        INSERT INTO order_items (id, order_id, product_id, quantity, unit_price)
                        VALUES (:id, :order_id, :product_id, :quantity, :unit_price)
                        ON CONFLICT (id) DO NOTHING
                    """),
                    {
                        "id": item_id,
                        "order_id": o["id"],
                        "product_id": item["product_id"],
                        "quantity": item["quantity"],
                        "unit_price": item["unit_price"],
                    },
                )

    return order_count


async def dsa_create_tables(engine):
    """Cria as tabelas se não existirem."""
    async with engine.begin() as conn:
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS products (
                id VARCHAR(20) PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                description TEXT,
                category VARCHAR(50) NOT NULL,
                brand VARCHAR(100) NOT NULL,
                price NUMERIC(10, 2) NOT NULL,
                stock INTEGER NOT NULL DEFAULT 0,
                specs JSONB,
                image_url VARCHAR(500),
                rating FLOAT DEFAULT 0,
                reviews_count INTEGER DEFAULT 0,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
        """))
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS customers (
                id VARCHAR(20) PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
        """))
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS orders (
                id VARCHAR(20) PRIMARY KEY,
                customer_id VARCHAR(20) REFERENCES customers(id),
                status VARCHAR(20) NOT NULL DEFAULT 'confirmed',
                total NUMERIC(10, 2) NOT NULL,
                tracking_code VARCHAR(50),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
        """))
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS order_items (
                id VARCHAR(50) PRIMARY KEY,
                order_id VARCHAR(20) REFERENCES orders(id),
                product_id VARCHAR(20) REFERENCES products(id),
                quantity INTEGER NOT NULL,
                unit_price NUMERIC(10, 2) NOT NULL
            )
        """))
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS conversations (
                id VARCHAR(50) PRIMARY KEY,
                customer_id VARCHAR(20) REFERENCES customers(id),
                messages JSONB DEFAULT '[]'::jsonb,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
        """))
        await conn.execute(text(
            "CREATE INDEX IF NOT EXISTS idx_products_category ON products(category)"
        ))
        await conn.execute(text(
            "CREATE INDEX IF NOT EXISTS idx_products_brand ON products(brand)"
        ))
        await conn.execute(text(
            "CREATE INDEX IF NOT EXISTS idx_products_name ON products(name)"
        ))
        await conn.execute(text(
            "CREATE INDEX IF NOT EXISTS idx_orders_customer ON orders(customer_id)"
        ))
        await conn.execute(text(
            "CREATE INDEX IF NOT EXISTS idx_orders_tracking ON orders(tracking_code)"
        ))


async def dsa_main():
    """Executa o seed completo do banco de dados."""
    logger.info("Iniciando seed do banco de dados...")

    engine = create_async_engine(DATABASE_URL, echo=False)

    logger.info("Criando tabelas...")
    await dsa_create_tables(engine)

    products = dsa_load_json("products.json")
    customers = dsa_load_json("customers.json")
    orders = dsa_load_json("orders.json")

    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        async with session.begin():
            products_count = await dsa_seed_products(session, products)
            customers_count = await dsa_seed_customers(session, customers)
            orders_count = await dsa_seed_orders(session, orders)

    await engine.dispose()

    logger.info("Seed concluído!")
    logger.info(f"  Produtos inseridos: {products_count}")
    logger.info(f"  Clientes inseridos: {customers_count}")
    logger.info(f"  Pedidos inseridos: {orders_count}")
    logger.info(f"  Total de registros: {products_count + customers_count + orders_count}")


if __name__ == "__main__":
    asyncio.run(dsa_main())




    
