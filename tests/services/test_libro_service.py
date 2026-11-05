import pytest
from sqlmodel import Session

from api.payload.libro_dto import (
    LibroCreateRequest,
    LibroPatchRequest,
    LibroUpdateRequest,
)
from exceptions import (
    AutorNoEncontradoException,
    AutorYaAsociadoException,
    DatosLibroInvalidosException,
    IsbnDuplicadoException,
    LibroConPrestamosException,
    LibroNoEncontradoException,
)
from repositories.autor_repository import AutorRepository
from repositories.libro_repository import LibroRepository
from services.libro_service import LibroService


# Obtener listado de libros en el servicio
def test_libro_service_get_libros(session: Session, seed: None) -> None:
    service = LibroService(LibroRepository(session), AutorRepository(session))
    libros = service.get_libros(offset=0, limit=10)
    assert len(libros) == 3


# Filtrar libros por disponibilidad de stock
def test_libro_service_get_libros_disponibles(session: Session, seed: None) -> None:
    service = LibroService(LibroRepository(session), AutorRepository(session))
    # Crear libro agotado
    service.create_libro(LibroCreateRequest(titulo="Libro Sin Stock", isbn="978-0000000099", stock=0))

    disponibles = service.get_libros(disponibles=True)
    assert len(disponibles) == 3
    assert all(l.stock > 0 for l in disponibles)

    agotados = service.get_libros(disponibles=False)
    assert len(agotados) == 1
    assert agotados[0].stock == 0


# Obtener libro por ID existente
def test_libro_service_get_libro_by_id_ok(session: Session, seed: None) -> None:
    service = LibroService(LibroRepository(session), AutorRepository(session))
    libro = service.get_libro_by_id(1)
    assert libro.id == 1
    assert libro.titulo == "El Aleph"


# Error al obtener libro por ID inexistente (LibroNoEncontradoException)
def test_libro_service_get_libro_by_id_not_found(session: Session, seed: None) -> None:
    service = LibroService(LibroRepository(session), AutorRepository(session))
    with pytest.raises(LibroNoEncontradoException):
        service.get_libro_by_id(999)


# Crear un libro válido en el servicio
def test_libro_service_create_libro_ok(session: Session) -> None:
    service = LibroService(LibroRepository(session), AutorRepository(session))
    payload = LibroCreateRequest(
        titulo="Ficciones",
        anio=1944,
        isbn="978-950-07-0000-1",
        stock=5,
    )
    creado = service.create_libro(payload)
    assert creado.id is not None
    assert creado.titulo == "Ficciones"


# Error al crear libro con ISBN duplicado (IsbnDuplicadoException)
def test_libro_service_create_libro_isbn_duplicado(session: Session, seed: None) -> None:
    service = LibroService(LibroRepository(session), AutorRepository(session))
    payload = LibroCreateRequest(
        titulo="Otro Aleph",
        isbn="978-950-07-2575-0",  # ya existe en el seed
        stock=2,
    )
    with pytest.raises(IsbnDuplicadoException):
        service.create_libro(payload)


# Reemplazo completo de un libro existente (PUT)
def test_libro_service_replace_libro_ok(session: Session, seed: None) -> None:
    service = LibroService(LibroRepository(session), AutorRepository(session))
    payload = LibroUpdateRequest(
        titulo="El Aleph Modificado",
        anio=1950,
        isbn="978-950-07-2575-0",
        stock=10,
    )
    reemplazado = service.replace_libro(1, payload)
    assert reemplazado.titulo == "El Aleph Modificado"
    assert reemplazado.stock == 10


# Error al reemplazar libro con ISBN de otro libro existente
def test_libro_service_replace_libro_isbn_duplicado(session: Session, seed: None) -> None:
    service = LibroService(LibroRepository(session), AutorRepository(session))
    # Intentar asignar al libro 1 el ISBN del libro 2
    payload = LibroUpdateRequest(
        titulo="Conflicto ISBN",
        isbn="978-84-376-0494-7",
        stock=5,
    )
    with pytest.raises(IsbnDuplicadoException):
        service.replace_libro(1, payload)


# Actualización parcial de un libro (PATCH)
def test_libro_service_update_libro_patch_ok(session: Session, seed: None) -> None:
    service = LibroService(LibroRepository(session), AutorRepository(session))
    payload = LibroPatchRequest(stock=20)
    actualizado = service.update_libro(1, payload)
    assert actualizado.stock == 20
    assert actualizado.titulo == "El Aleph"


# Error al actualizar libro con campos nulos prohibidos (DatosLibroInvalidosException)
def test_libro_service_update_libro_patch_invalid_null(session: Session, seed: None) -> None:
    service = LibroService(LibroRepository(session), AutorRepository(session))
    with pytest.raises(DatosLibroInvalidosException):
        service.update_libro(1, LibroPatchRequest.model_construct(titulo=None))

    with pytest.raises(DatosLibroInvalidosException):
        service.update_libro(1, LibroPatchRequest.model_construct(isbn=None))

    with pytest.raises(DatosLibroInvalidosException):
        service.update_libro(1, LibroPatchRequest.model_construct(stock=None))


# Error al actualizar libro parcialmente con ISBN duplicado
def test_libro_service_update_libro_patch_isbn_duplicado(session: Session, seed: None) -> None:
    service = LibroService(LibroRepository(session), AutorRepository(session))
    payload = LibroPatchRequest(isbn="978-84-376-0494-7")  # ISBN del libro 2
    with pytest.raises(IsbnDuplicadoException):
        service.update_libro(1, payload)


# Asociar un autor a un libro con éxito
def test_libro_service_asociar_autor_ok(session: Session, seed: None) -> None:
    service = LibroService(LibroRepository(session), AutorRepository(session))
    libro = service.asociar_autor(libro_id=1, autor_id=2)
    assert len(libro.autores) == 2
    assert any(a.id == 2 for a in libro.autores)


# Error al asociar autor a libro inexistente
def test_libro_service_asociar_autor_libro_no_encontrado(session: Session, seed: None) -> None:
    service = LibroService(LibroRepository(session), AutorRepository(session))
    with pytest.raises(LibroNoEncontradoException):
        service.asociar_autor(libro_id=999, autor_id=1)


# Error al asociar autor inexistente a un libro
def test_libro_service_asociar_autor_autor_no_encontrado(session: Session, seed: None) -> None:
    service = LibroService(LibroRepository(session), AutorRepository(session))
    with pytest.raises(AutorNoEncontradoException):
        service.asociar_autor(libro_id=1, autor_id=999)


# Error al asociar autor que ya se encuentra asociado al libro (AutorYaAsociadoException)
def test_libro_service_asociar_autor_ya_asociado(session: Session, seed: None) -> None:
    service = LibroService(LibroRepository(session), AutorRepository(session))
    # Autor 1 ya está asociado a Libro 1 en el seed
    with pytest.raises(AutorYaAsociadoException):
        service.asociar_autor(libro_id=1, autor_id=1)


# Eliminar un libro sin préstamos con éxito
def test_libro_service_delete_libro_ok(session: Session) -> None:
    service = LibroService(LibroRepository(session), AutorRepository(session))
    creado = service.create_libro(
        LibroCreateRequest(
            titulo="Libro Sin Prestamos",
            isbn="978-9999999999",
            stock=1,
        )
    )
    libro_id = creado.id
    assert libro_id is not None

    service.delete_libro(libro_id)
    with pytest.raises(LibroNoEncontradoException):
        service.get_libro_by_id(libro_id)


# Error al eliminar un libro que tiene préstamos asociados (LibroConPrestamosException)
def test_libro_service_delete_libro_con_prestamos(session: Session, seed: None) -> None:
    service = LibroService(LibroRepository(session), AutorRepository(session))
    # Libro 1 tiene préstamos asociados en el seed
    with pytest.raises(LibroConPrestamosException):
        service.delete_libro(1)
