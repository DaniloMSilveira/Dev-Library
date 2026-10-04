# Projeto Desenvolvido na Data Science Academy

"""Router de Clientes — Endpoints de criação e consulta de clientes."""

from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import dsa_get_db
from app.models.customer import Customer
from app.schemas.customer_schema import CustomerCreate, CustomerResponse

# Cria instância do roteador
router = APIRouter(prefix="/api/v1/customers", tags=["Clientes"])


@router.post("/", response_model=CustomerResponse, status_code=201)
async def dsa_create_customer(customer_data: CustomerCreate, db: AsyncSession = Depends(dsa_get_db)) -> CustomerResponse:
    """Cria um novo cliente (idempotente — retorna existente se email já cadastrado)."""
    result = await db.execute(select(Customer).where(Customer.email == customer_data.email))
    existing = result.scalar_one_or_none()
    if existing:
        return CustomerResponse.model_validate(existing)

    customer = Customer(
        id=f"CUST-{uuid4().hex[:6].upper()}",
        name=customer_data.name,
        email=customer_data.email,
    )
    db.add(customer)
    await db.flush()
    await db.refresh(customer)
    await db.commit()
    return CustomerResponse.model_validate(customer)


@router.get("/{customer_id}", response_model=CustomerResponse)
async def dsa_get_customer(customer_id: str, db: AsyncSession = Depends(dsa_get_db)) -> CustomerResponse:
    """Retorna dados do cliente."""
    result = await db.execute(select(Customer).where(Customer.id == customer_id))
    customer = result.scalar_one_or_none()
    if not customer:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return CustomerResponse.model_validate(customer)


@router.get("/email/{email}", response_model=CustomerResponse)
async def dsa_get_customer_by_email(email: str, db: AsyncSession = Depends(dsa_get_db)) -> CustomerResponse:
    """Busca cliente por e-mail."""
    result = await db.execute(select(Customer).where(Customer.email == email))
    customer = result.scalar_one_or_none()
    if not customer:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return CustomerResponse.model_validate(customer)



