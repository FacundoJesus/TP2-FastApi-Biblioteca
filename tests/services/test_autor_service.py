import pytest
from sqlmodel import Session

from api.payload.autor_dto import AutorCreateRequest, AutorPatchRequest, AutorUpdateRequest
from exceptions import (
    AutorConLibrosException,
    AutorNoEncontradoException,
    DatosAutorInvalidosException,
)
from repositories.autor_repository import AutorRepository
from services.autor_service import AutorService


# Obtener listado de autores en el servicio
def test_autor_service_get_autores(session: Session, seed: None) -> None:
    service = AutorService(AutorRepository(session))
    autores = service.get_autores(offset=0, limit=10)
    assert len(autores) == 3


# Obtener autor por ID existente
def test_autor_service_get_autor_by_id_ok(session: Session, seed: None) -> None:
    service = AutorService(AutorRepository(session))
    autor = service.get_autor_by_id(1)
    assert autor.id == 1
    assert autor.nombre == "Jorge Luis Borges"


# Error al obtener autor por ID inexistente (AutorNoEncontradoException)
def test_autor_service_get_autor_by_id_not_found(session: Session, seed: None) -> None:
    service = AutorService(AutorRepository(session))
    with pytest.raises(AutorNoEncontradoException):
        service.get_autor_by_id(999)


# Crear un autor válido en el servicio
def test_autor_service_create_autor(session: Session) -> None:
    service = AutorService(AutorRepository(session))
    payload = AutorCreateRequest(nombre="Ernesto Sabato", nacionalidad="Argentino")
    creado = service.create_autor(payload)

    assert creado.id is not None
    assert creado.nombre == "Ernesto Sabato"


# Reemplazo completo de un autor existente (PUT)
def test_autor_service_replace_autor_ok(session: Session, seed: None) -> None:
    service = AutorService(AutorRepository(session))
    payload = AutorUpdateRequest(nombre="J. L. Borges Modificado", nacionalidad="Argentino")
    reemplazado = service.replace_autor(1, payload)

    assert reemplazado.id == 1
    assert reemplazado.nombre == "J. L. Borges Modificado"


# Error al reemplazar autor inexistente
def test_autor_service_replace_autor_not_found(session: Session, seed: None) -> None:
    service = AutorService(AutorRepository(session))
    payload = AutorUpdateRequest(nombre="Inexistente", nacionalidad="Desconocida")
    with pytest.raises(AutorNoEncontradoException):
        service.replace_autor(999, payload)


# Actualización parcial de un autor (PATCH)
def test_autor_service_update_autor_patch_ok(session: Session, seed: None) -> None:
    service = AutorService(AutorRepository(session))
    payload = AutorPatchRequest(nacionalidad="Rioplatense")
    actualizado = service.update_autor(1, payload)

    assert actualizado.nacionalidad == "Rioplatense"
    assert actualizado.nombre == "Jorge Luis Borges"


# Error al actualizar autor con campo nulo (DatosAutorInvalidosException)
def test_autor_service_update_autor_patch_invalid_null(session: Session, seed: None) -> None:
    service = AutorService(AutorRepository(session))
    payload = AutorPatchRequest.model_construct(nombre=None)
    with pytest.raises(DatosAutorInvalidosException):
        service.update_autor(1, payload)

    payload_nac = AutorPatchRequest.model_construct(nacionalidad=None)
    with pytest.raises(DatosAutorInvalidosException):
        service.update_autor(1, payload_nac)


# Error al actualizar parcialmente un autor inexistente
def test_autor_service_update_autor_patch_not_found(session: Session, seed: None) -> None:
    service = AutorService(AutorRepository(session))
    payload = AutorPatchRequest(nombre="Nuevo Nombre")
    with pytest.raises(AutorNoEncontradoException):
        service.update_autor(999, payload)


# Eliminar un autor sin libros con éxito
def test_autor_service_delete_autor_ok(session: Session) -> None:
    service = AutorService(AutorRepository(session))
    creado = service.create_autor(AutorCreateRequest(nombre="Autor Solitario", nacionalidad="Uruguayo"))
    autor_id = creado.id
    assert autor_id is not None

    service.delete_autor(autor_id)
    with pytest.raises(AutorNoEncontradoException):
        service.get_autor_by_id(autor_id)


# Error al eliminar un autor que tiene libros asociados (AutorConLibrosException)
def test_autor_service_delete_autor_con_libros(session: Session, seed: None) -> None:
    service = AutorService(AutorRepository(session))
    # Autor 1 tiene libros asociados en el seed
    with pytest.raises(AutorConLibrosException):
        service.delete_autor(1)
