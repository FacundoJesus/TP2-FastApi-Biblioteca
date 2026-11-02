from collections.abc import Sequence
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from api.payload.prestamo_dto import PrestamoCreateRequest, PrestamoResponse
from dependencies import (
    ROL_BIBLIOTECARIO,
    ROL_SOCIO,
    PrestamoServiceDep,
    RoleDep,
    SocioIdDep,
    SocioServiceDep,
    require_role,
)
from exceptions import (
    ConflictoNegocioException,
    OperacionProhibidaException,
    PrestamoNoEncontradoException,
    PrestamoYaDevueltoException,
    RecursoNoEncontradoException,
    SocioNoEncontradoException,
)
from models import PrestamoDB

router = APIRouter(prefix="/prestamos", tags=["Préstamos"])


# Obtener Préstamos (el bibliotecario ve todos; el socio solo ve los suyos vía X-Socio-Id)
@router.get("", response_model=Sequence[PrestamoResponse], status_code=status.HTTP_200_OK)
def get_prestamos(
    service: PrestamoServiceDep,
    socio_service: SocioServiceDep,
    rol: RoleDep,
    socio_id: SocioIdDep,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=50)] = 50,
) -> Sequence[PrestamoDB]:
    if rol == ROL_SOCIO:
        if socio_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Debe incluir la cabecera 'X-Socio-Id' con su ID de socio al operar como socio",
            )
        try:
            return socio_service.get_prestamos_socio(socio_id)
        except SocioNoEncontradoException as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    return service.get_prestamos(offset=offset, limit=limit)


# Obtener Préstamo por ID (el bibliotecario ve cualquiera; el socio solo si le pertenece)
@router.get("/{id}", response_model=PrestamoResponse, status_code=status.HTTP_200_OK)
def get_prestamo(
    id: int,
    service: PrestamoServiceDep,
    rol: RoleDep,
    socio_id: SocioIdDep,
) -> PrestamoDB:
    try:
        prestamo = service.get_prestamo_by_id(id)
    except PrestamoNoEncontradoException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    if rol == ROL_SOCIO:
        if socio_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Debe incluir la cabecera 'X-Socio-Id' con su ID de socio al operar como socio",
            )
        if prestamo.socio_id != socio_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Un socio solo puede consultar sus propios préstamos",
            )

    return prestamo


# Registrar un Préstamo (solo bibliotecario)
@router.post(
    "",
    response_model=PrestamoResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role([ROL_BIBLIOTECARIO]))],
)
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


# Registrar la Devolución de un Préstamo (solo bibliotecario)
@router.post(
    "/{id}/devolucion",
    response_model=PrestamoResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_role([ROL_BIBLIOTECARIO]))],
)
def registrar_devolucion(id: int, service: PrestamoServiceDep) -> PrestamoDB:
    try:
        return service.registrar_devolucion(id)
    except RecursoNoEncontradoException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except PrestamoYaDevueltoException as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
