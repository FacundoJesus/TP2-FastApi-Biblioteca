from collections.abc import Sequence
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status

from api.payload.autor_dto import AutorCreateRequest, AutorPatchRequest, AutorResponse, AutorUpdateRequest
from dependencies import AutorServiceDep
from exceptions import (
    AutorConLibrosException,
    AutorNoEncontradoException,
    DatosAutorInvalidosException,
)
from models import AutorDB

router = APIRouter(prefix="/autores", tags=["Autores"])


# Obtener Autores
@router.get("", response_model=Sequence[AutorResponse], status_code=status.HTTP_200_OK)
def get_autores(
    service: AutorServiceDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=50)] = 50,
) -> Sequence[AutorDB]:
    return service.get_autores(offset, limit)


# Obtener Autor por ID
@router.get("/{autor_id}", response_model=AutorResponse, status_code=status.HTTP_200_OK)
def get_autor(autor_id: int, service: AutorServiceDep) -> AutorDB:
    try:
        return service.get_autor_by_id(autor_id)
    except AutorNoEncontradoException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


# Crear Autor
@router.post("", response_model=AutorResponse, status_code=status.HTTP_201_CREATED)
def create_autor(autor: AutorCreateRequest, service: AutorServiceDep) -> AutorDB:
    return service.create_autor(autor)


# Actualizar Autor (reemplazo completo)
@router.put("/{autor_id}", response_model=AutorResponse, status_code=status.HTTP_200_OK)
def replace_autor(autor_id: int, autor: AutorUpdateRequest, service: AutorServiceDep) -> AutorDB:
    try:
        return service.replace_autor(autor_id, autor)
    except AutorNoEncontradoException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


# Actualizar Autor (parcial)
@router.patch("/{autor_id}", response_model=AutorResponse, status_code=status.HTTP_200_OK)
def update_autor(autor_id: int, autor: AutorPatchRequest, service: AutorServiceDep) -> AutorDB:
    try:
        return service.update_autor(autor_id, autor)
    except AutorNoEncontradoException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except DatosAutorInvalidosException as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


# Eliminar Autor
@router.delete("/{autor_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_autor(autor_id: int, service: AutorServiceDep) -> None:
    try:
        service.delete_autor(autor_id)
    except AutorNoEncontradoException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except AutorConLibrosException as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
