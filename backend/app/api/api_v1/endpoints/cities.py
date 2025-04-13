from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.database.session import get_db
from app.schemas.city import City, CityCreate
from app.crud.crud_city import city_crud

router = APIRouter()

@router.get("/", response_model=List[City])
async def read_cities(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    name: Optional[str] = None,
    state: Optional[str] = None
):
    """
    Recuperar listado de ciudades con posibilidad de filtrado por nombre y estado.
    """
    cities = await city_crud.get_multi(
        db, skip=skip, limit=limit, filters={"name": name, "state": state}
    )
    return cities

@router.get("/{city_id}", response_model=City)
async def read_city(
    city_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Recuperar información de una ciudad específica por ID.
    """
    city = await city_crud.get(db, id=city_id)
    if city is None:
        raise HTTPException(status_code=404, detail="Ciudad no encontrada")
    return city

@router.get("/by-name/{city_name}", response_model=List[City])
async def read_city_by_name(
    city_name: str,
    db: AsyncSession = Depends(get_db),
    state: Optional[str] = None
):
    """
    Buscar ciudades por nombre (búsqueda parcial).
    Opcionalmente filtrar por estado.
    """
    cities = await city_crud.get_by_name(db, name=city_name, state=state)
    return cities

@router.post("/", response_model=City)
async def create_city(
    city_in: CityCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Crear una nueva ciudad en la base de datos.
    """
    city = await city_crud.create(db, obj_in=city_in)
    return city
