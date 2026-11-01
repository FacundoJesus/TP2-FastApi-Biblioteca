from collections.abc import Sequence
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status

from api.payload.prestamo_dto import PrestamoCreateRequest, PrestamoResponse
from dependencies import PrestamoServiceDep
from exceptions import (
    ConflictoNegocioException,
    OperacionProhibidaException,
    PrestamoNoEncontradoException,
    PrestamoYaDevueltoException,
    RecursoNoEncontradoException,
)
from models import PrestamoDB

router = APIRouter(prefix="/prestamos", tags=["Préstamos"])


# Obtener Préstamos
@router.get("", response_model=Sequence[PrestamoResponse], status_code=status.HTTP_200_OK)
def get_prestamos(
    service: PrestamoServiceDep,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=50)] = 50,
) -> Sequence[PrestamoDB]:
    return service.get_prestamos(offset=offset, limit=limit)


# Obtener Préstamo por ID
@router.get("/{id}", response_model=PrestamoResponse, status_code=status.HTTP_200_OK)
def get_prestamo(id: int, service: PrestamoServiceDep) -> PrestamoDB:
    try:
        return service.get_prestamo_by_id(id)
    except PrestamoNoEncontradoException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


# Registrar un Préstamo
@router.post("", response_model=PrestamoResponse, status_code=status.HTTP_201_CREATED)
def create_prestamo(
    prestamo: PrestamoCreateRequest,
    service: PrestamoServiceDep,
) -> PrestamoDB:
    try:
        return service.create_prestamo(prestamo)
    except RecursoNoEncontradoException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except OperacionProhibidaException as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except ConflictoNegocioException as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


# Registrar la Devolución de un Préstamo
@router.post(
    "/{id}/devolucion",
    response_model=PrestamoResponse,
    status_code=status.HTTP_200_OK,
)
def registrar_devolucion(id: int, service: PrestamoServiceDep) -> PrestamoDB:
    try:
        return service.registrar_devolucion(id)
    except RecursoNoEncontradoException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except PrestamoYaDevueltoException as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
