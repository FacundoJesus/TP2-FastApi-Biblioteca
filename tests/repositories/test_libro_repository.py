from sqlmodel import Session

from models.autor import AutorDB
from models.libro import LibroDB
from repositories.libro_repository import LibroRepository


# Obtener listado de libros con paginación
def test_libro_repository_get_libros(session: Session, seed: None) -> None:
    repo = LibroRepository(session)
    libros = repo.get_libros(offset=0, limit=10)
    assert len(libros) == 3

    paginados = repo.get_libros(offset=1, limit=1)
    assert len(paginados) == 1
    assert paginados[0].id == 2


# Filtrar libros por disponibilidad de stock (disponibles=True / False)
def test_libro_repository_get_libros_disponibles(session: Session, seed: None) -> None:
    repo = LibroRepository(session)
    # Libro con stock 0
    repo.create_libro(
        LibroDB(
            titulo="Libro Agotado",
            isbn="978-0000000001",
            stock=0,
        )
    )

    disponibles = repo.get_libros(disponibles=True)
    assert len(disponibles) == 3
    assert all(l.stock > 0 for l in disponibles)

    agotados = repo.get_libros(disponibles=False)
    assert len(agotados) == 1
    assert agotados[0].stock == 0


# Obtener libro por ID (existente e inexistente)
def test_libro_repository_get_by_id(session: Session, seed: None) -> None:
    repo = LibroRepository(session)
    libro = repo.get_libro_by_id(1)
    assert libro is not None
    assert libro.titulo == "El Aleph"

    inexistente = repo.get_libro_by_id(999)
    assert inexistente is None


# Obtener libro por ISBN (existente e inexistente)
def test_libro_repository_get_by_isbn(session: Session, seed: None) -> None:
    repo = LibroRepository(session)
    libro = repo.get_libro_by_isbn("978-950-07-2575-0")
    assert libro is not None
    assert libro.id == 1

    inexistente = repo.get_libro_by_isbn("978-0000000000")
    assert inexistente is None


# Crear un nuevo libro en la base de datos
def test_libro_repository_create_libro(session: Session) -> None:
    repo = LibroRepository(session)
    nuevo_libro = LibroDB(
        titulo="Ficciones",
        anio=1944,
        isbn="978-950-07-0000-1",
        stock=10,
    )
    creado = repo.create_libro(nuevo_libro)

    assert creado.id is not None
    assert creado.titulo == "Ficciones"
    assert repo.get_libro_by_id(creado.id) is not None


# Actualizar datos de un libro existente
def test_libro_repository_update_libro(session: Session, seed: None) -> None:
    repo = LibroRepository(session)
    libro = repo.get_libro_by_id(1)
    assert libro is not None

    actualizado = repo.update_libro(libro, {"stock": 15, "titulo": "El Aleph (Edición Especial)"})
    assert actualizado.stock == 15
    assert actualizado.titulo == "El Aleph (Edición Especial)"

    recuperado = repo.get_libro_by_id(1)
    assert recuperado is not None
    assert recuperado.stock == 15


# Asociar un autor a un libro en la base de datos
def test_libro_repository_add_autor_to_libro(session: Session, seed: None) -> None:
    repo = LibroRepository(session)
    libro = repo.get_libro_by_id(1)
    autor = session.get(AutorDB, 2)
    assert libro is not None
    assert autor is not None

    repo.add_autor_to_libro(libro, autor)
    recuperado = repo.get_libro_by_id(1)
    assert recuperado is not None
    assert len(recuperado.autores) == 2
    assert any(a.id == 2 for a in recuperado.autores)


# Eliminar un libro de la base de datos
def test_libro_repository_delete_libro(session: Session) -> None:
    repo = LibroRepository(session)
    libro = repo.create_libro(
        LibroDB(
            titulo="Libro a Borrar",
            isbn="978-1111111111",
            stock=1,
        )
    )
    libro_id = libro.id
    assert libro_id is not None

    repo.delete_libro(libro)
    assert repo.get_libro_by_id(libro_id) is None
