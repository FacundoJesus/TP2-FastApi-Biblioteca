from collections.abc import Sequence
from typing import Annotated

from fastapi import APIRouter, Query, status

from api.payload.autor_dto import GetAutoresResponse
from dependencies import AutorServiceDep
from models import AutorDB

router = APIRouter(prefix="/autores", tags=["Autores"])


# Obtener Autores
@router.get("", response_model=Sequence[GetAutoresResponse], status_code=status.HTTP_200_OK)
def get_autores(
    service: AutorServiceDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=50)] = 50,
) -> Sequence[AutorDB]:
    return service.get_autores(offset, limit)


# Obtener Autor por ID

# Crear Autor

# Actualizar Autor

