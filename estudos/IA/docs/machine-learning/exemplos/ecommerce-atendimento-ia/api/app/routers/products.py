# Projeto Desenvolvido na Data Science Academy

"""Router de Produtos — Endpoints de catálogo, busca e detalhes."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import dsa_get_db
from app.schemas.product_schema import ProductListResponse, ProductResponse
from app.services.product_service import ProductService

router = APIRouter(prefix="/api/v1/products", tags=["Produtos"])


# Rotas específicas (/search, /categories) devem vir ANTES de /{product_id}
@router.get("/search", response_model=ProductListResponse)
async def dsa_search_products(
    q: str = Query(..., min_length=1, description="Texto de busca"),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(dsa_get_db),
) -> ProductListResponse:
    """Busca produtos por texto com paginação."""
    service = ProductService(db)
    products = await service.dsa_search_products(q)
    total = len(products)
    offset = (page - 1) * per_page
    paginated = products[offset : offset + per_page]
    return ProductListResponse(
        items=[ProductResponse.model_validate(p) for p in paginated],
        total=total,
        page=page,
        per_page=per_page,
    )


@router.get("/categories", response_model=list[str])
async def dsa_list_categories(
    db: AsyncSession = Depends(dsa_get_db),
) -> list[str]:
    """Lista categorias disponíveis."""
    service = ProductService(db)
    return await service.dsa_get_categories()


@router.get("/{product_id}", response_model=ProductResponse)
async def dsa_get_product(
    product_id: str,
    db: AsyncSession = Depends(dsa_get_db),
) -> ProductResponse:
    """Retorna detalhes de um produto."""
    service = ProductService(db)
    product = await service.dsa_get_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return ProductResponse.model_validate(product)


@router.get("/", response_model=ProductListResponse)
async def dsa_list_products(
    category: str | None = Query(None),
    brand: str | None = Query(None),
    min_price: float | None = Query(None, ge=0),
    max_price: float | None = Query(None, ge=0),
    search: str | None = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(12, ge=1, le=100),
    db: AsyncSession = Depends(dsa_get_db),
) -> ProductListResponse:
    """Lista produtos com filtros e paginação."""
    service = ProductService(db)
    return await service.dsa_list_products(
        category=category,
        brand=brand,
        min_price=min_price,
        max_price=max_price,
        search=search,
        page=page,
        per_page=per_page,
    )
