from collections.abc import Sequence
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from api.payload.libro_dto import (
    LibroCreateRequest,
    LibroPatchRequest,
    LibroResponse,
    LibroUpdateRequest,
)
from dependencies import LibroServiceDep, ROL_BIBLIOTECARIO, require_role
from exceptions import (
    AutorYaAsociadoException,
    DatosLibroInvalidosException,
    IsbnDuplicadoException,
    LibroConPrestamosException,
    LibroNoEncontradoException,
    RecursoNoEncontradoException,
)
from models import LibroDB

router = APIRouter(prefix="/libros", tags=["Libros"])


# Obtener Libros (incluye GET /libros?disponibles=true)
@router.get("", response_model=Sequence[LibroResponse], status_code=status.HTTP_200_OK)
def get_libros(
    service: LibroServiceDep,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=50)] = 50,
    disponibles: bool | None = None,
) -> Sequence[LibroDB]:
    return service.get_libros(
        offset=offset,
        limit=limit,
        disponibles=disponibles,
    )


# Obtener Libro por ID
@router.get("/{id}", response_model=LibroResponse, status_code=status.HTTP_200_OK)
def get_libro(id: int, service: LibroServiceDep) -> LibroDB:
    try:
        return service.get_libro_by_id(id)
    except LibroNoEncontradoException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


# Crear Libro
@router.post(
    "",
    response_model=LibroResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role([ROL_BIBLIOTECARIO]))],
)
def create_libro(libro: LibroCreateRequest, service: LibroServiceDep) -> LibroDB:
    try:
        return service.create_libro(libro)
    except IsbnDuplicadoException as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


# Asociar un Autor a un Libro
@router.post(
    "/{id}/autores/{autor_id}",
    response_model=LibroResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_role([ROL_BIBLIOTECARIO]))],
)
def asociar_autor_a_libro(id: int, autor_id: int, service: LibroServiceDep) -> LibroDB:
    try:
        return service.asociar_autor(id, autor_id)
    except RecursoNoEncontradoException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except AutorYaAsociadoException as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


# Actualizar Libro (reemplazo completo)
@router.put(
    "/{id}",
    response_model=LibroResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_role([ROL_BIBLIOTECARIO]))],
)
def replace_libro(
    id: int,
    libro: LibroUpdateRequest,
    service: LibroServiceDep,
) -> LibroDB:
    try:
        return service.replace_libro(id, libro)
    except LibroNoEncontradoException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except IsbnDuplicadoException as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


# Actualizar Libro (parcial)
@router.patch(
    "/{id}",
    response_model=LibroResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_role([ROL_BIBLIOTECARIO]))],
)
def update_libro(
    id: int,
    libro: LibroPatchRequest,
    service: LibroServiceDep,
) -> LibroDB:
    try:
        return service.update_libro(id, libro)
    except LibroNoEncontradoException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except IsbnDuplicadoException as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except DatosLibroInvalidosException as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


# Eliminar Libro
@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_role([ROL_BIBLIOTECARIO]))],
)
def delete_libro(id: int, service: LibroServiceDep) -> None:
    try:
        service.delete_libro(id)
    except LibroNoEncontradoException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except LibroConPrestamosException as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
