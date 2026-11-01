from collections.abc import Sequence
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status

from api.payload.prestamo_dto import PrestamoResponse
from api.payload.socio_dto import (
    SocioCreateRequest,
    SocioPatchRequest,
    SocioResponse,
    SocioUpdateRequest,
)
from dependencies import SocioServiceDep
from exceptions import (
    DatosSocioInvalidosException,
    EmailDuplicadoException,
    SocioConPrestamosException,
    SocioNoEncontradoException,
)
from models import PrestamoDB, SocioDB

router = APIRouter(prefix="/socios", tags=["Socios"])


# Obtener Socios
@router.get("", response_model=Sequence[SocioResponse], status_code=status.HTTP_200_OK)
def get_socios(
    service: SocioServiceDep,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=50)] = 50,
) -> Sequence[SocioDB]:
    return service.get_socios(offset, limit)


# Obtener Socio por ID
@router.get("/{id}", response_model=SocioResponse, status_code=status.HTTP_200_OK)
def get_socio(id: int, service: SocioServiceDep) -> SocioDB:
    try:
        return service.get_socio_by_id(id)
    except SocioNoEncontradoException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


# Obtener Préstamos de un Socio (incluye GET /socios/{id}/prestamos?activos=true)
@router.get(
    "/{id}/prestamos",
    response_model=Sequence[PrestamoResponse],
    status_code=status.HTTP_200_OK,
)
def get_prestamos_socio(
    id: int,
    service: SocioServiceDep,
    activos: bool | None = None,
) -> Sequence[PrestamoDB]:
    try:
        return service.get_prestamos_socio(id, activos=activos)
    except SocioNoEncontradoException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


# Crear Socio
@router.post("", response_model=SocioResponse, status_code=status.HTTP_201_CREATED)
def create_socio(socio: SocioCreateRequest, service: SocioServiceDep) -> SocioDB:
    try:
        return service.create_socio(socio)
    except EmailDuplicadoException as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


# Actualizar Socio (reemplazo completo)
@router.put("/{id}", response_model=SocioResponse, status_code=status.HTTP_200_OK)
def replace_socio(
    id: int,
    socio: SocioUpdateRequest,
    service: SocioServiceDep,
) -> SocioDB:
    try:
        return service.replace_socio(id, socio)
    except SocioNoEncontradoException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except EmailDuplicadoException as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


# Actualizar Socio (parcial)
@router.patch("/{id}", response_model=SocioResponse, status_code=status.HTTP_200_OK)
def update_socio(
    id: int,
    socio: SocioPatchRequest,
    service: SocioServiceDep,
) -> SocioDB:
    try:
        return service.update_socio(id, socio)
    except SocioNoEncontradoException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except EmailDuplicadoException as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except DatosSocioInvalidosException as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


# Eliminar Socio
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_socio(id: int, service: SocioServiceDep) -> None:
    try:
        service.delete_socio(id)
    except SocioNoEncontradoException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except SocioConPrestamosException as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
