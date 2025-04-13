from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.database.session import get_db
from app.schemas.comparison import ComparisonRequest, ComparisonResponse
from app.services.comparison_service import generate_comparison

router = APIRouter()

@router.post("/", response_model=ComparisonResponse)
async def create_comparison(
    comparison_request: ComparisonRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Generar una comparación entre ciudades basada en los indicadores seleccionados.
    
    - **city_ids**: Lista de IDs de ciudades a comparar (2-5 ciudades)
    - **indicator_ids**: Lista de IDs de indicadores a comparar
    - **year**: Año para el cual realizar la comparación (opcional, por defecto el más reciente)
    """
    if len(comparison_request.city_ids) < 2:
        raise HTTPException(
            status_code=400,
            detail="Se requieren al menos 2 ciudades para la comparación"
        )
    
    if len(comparison_request.city_ids) > 5:
        raise HTTPException(
            status_code=400,
            detail="No se pueden comparar más de 5 ciudades simultáneamente"
        )
    
    if not comparison_request.indicator_ids:
        raise HTTPException(
            status_code=400,
            detail="Se requiere al menos un indicador para la comparación"
        )
    
    result = await generate_comparison(
        db, 
        city_ids=comparison_request.city_ids,
        indicator_ids=comparison_request.indicator_ids,
        year=comparison_request.year
    )
    
    return result

@router.get("/indicators", response_model=List[str])
async def get_comparison_categories():
    """
    Obtener las categorías disponibles para comparación.
    """
    categories = [
        "salud", 
        "educacion", 
        "seguridad", 
        "economia", 
        "infraestructura",
        "calidad_de_vida"
    ]
    return categories
