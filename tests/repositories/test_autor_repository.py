from sqlmodel import Session

from models.autor import AutorDB
from repositories.autor_repository import AutorRepository


# Obtener listado de autores con paginación
def test_autor_repository_get_autores(session: Session, seed: None) -> None:
    repo = AutorRepository(session)
    autores = repo.get_autores(offset=0, limit=10)
    assert len(autores) == 3

    paginados = repo.get_autores(offset=1, limit=1)
    assert len(paginados) == 1
    assert paginados[0].id == 2


# Obtener autor por ID (existente e inexistente)
def test_autor_repository_get_by_id(session: Session, seed: None) -> None:
    repo = AutorRepository(session)
    autor = repo.get_autor_by_id(1)
    assert autor is not None
    assert autor.nombre == "Jorge Luis Borges"

    inexistente = repo.get_autor_by_id(999)
    assert inexistente is None


# Crear un nuevo autor en la base de datos
def test_autor_repository_create_autor(session: Session) -> None:
    repo = AutorRepository(session)
    nuevo_autor = AutorDB(nombre="Adolfo Bioy Casares", nacionalidad="Argentino")
    creado = repo.create_autor(nuevo_autor)

    assert creado.id is not None
    assert creado.nombre == "Adolfo Bioy Casares"
    assert repo.get_autor_by_id(creado.id) is not None


# Actualizar datos de un autor existente
def test_autor_repository_update_autor(session: Session, seed: None) -> None:
    repo = AutorRepository(session)
    autor = repo.get_autor_by_id(1)
    assert autor is not None

    actualizado = repo.update_autor(autor, {"nombre": "Jorge L. Borges"})
    assert actualizado.nombre == "Jorge L. Borges"

    recuperado = repo.get_autor_by_id(1)
    assert recuperado is not None
    assert recuperado.nombre == "Jorge L. Borges"


# Eliminar un autor de la base de datos
def test_autor_repository_delete_autor(session: Session) -> None:
    repo = AutorRepository(session)
    autor = repo.create_autor(AutorDB(nombre="Autor Temporal", nacionalidad="Uruguayo"))
    autor_id = autor.id
    assert autor_id is not None

    repo.delete_autor(autor)
    assert repo.get_autor_by_id(autor_id) is None
