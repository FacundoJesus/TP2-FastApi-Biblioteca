from sqlmodel import Session

from models.socio import SocioDB
from repositories.socio_repository import SocioRepository


# Obtener listado de socios con paginación
def test_socio_repository_get_socios(session: Session, seed: None) -> None:
    repo = SocioRepository(session)
    socios = repo.get_socios(offset=0, limit=10)
    assert len(socios) == 3

    paginados = repo.get_socios(offset=1, limit=1)
    assert len(paginados) == 1
    assert paginados[0].id == 2


# Filtrar socios por estado activo (activos=True / False)
def test_socio_repository_get_socios_filtrar_activos(session: Session, seed: None) -> None:
    repo = SocioRepository(session)
    activos = repo.get_socios(activos=True)
    assert len(activos) == 2
    assert all(s.activo for s in activos)

    inactivos = repo.get_socios(activos=False)
    assert len(inactivos) == 1
    assert not inactivos[0].activo
    assert inactivos[0].id == 3


# Obtener socio por ID (existente e inexistente)
def test_socio_repository_get_by_id(session: Session, seed: None) -> None:
    repo = SocioRepository(session)
    socio = repo.get_socio_by_id(1)
    assert socio is not None
    assert socio.nombre == "Juan Pérez"

    inexistente = repo.get_socio_by_id(999)
    assert inexistente is None


# Obtener socio por email (existente e inexistente)
def test_socio_repository_get_by_email(session: Session, seed: None) -> None:
    repo = SocioRepository(session)
    socio = repo.get_socio_by_email("juan.perez@utn.edu.ar")
    assert socio is not None
    assert socio.id == 1

    inexistente = repo.get_socio_by_email("no_existe@utn.edu.ar")
    assert inexistente is None


# Crear un nuevo socio en la base de datos
def test_socio_repository_create_socio(session: Session) -> None:
    repo = SocioRepository(session)
    nuevo_socio = SocioDB(
        nombre="Esteban Quito",
        email="esteban.quito@utn.edu.ar",
        activo=True,
    )
    creado = repo.create_socio(nuevo_socio)

    assert creado.id is not None
    assert creado.email == "esteban.quito@utn.edu.ar"
    assert repo.get_socio_by_id(creado.id) is not None


# Actualizar datos de un socio existente
def test_socio_repository_update_socio(session: Session, seed: None) -> None:
    repo = SocioRepository(session)
    socio = repo.get_socio_by_id(1)
    assert socio is not None

    actualizado = repo.update_socio(socio, {"activo": False, "nombre": "Juan Pérez Modificado"})
    assert not actualizado.activo
    assert actualizado.nombre == "Juan Pérez Modificado"

    recuperado = repo.get_socio_by_id(1)
    assert recuperado is not None
    assert not recuperado.activo


# Eliminar un socio de la base de datos
def test_socio_repository_delete_socio(session: Session, seed: None) -> None:
    repo = SocioRepository(session)
    # Socio 3 no tiene préstamos asociados
    socio = repo.get_socio_by_id(3)
    assert socio is not None

    repo.delete_socio(socio)
    assert repo.get_socio_by_id(3) is None


# Obtener préstamos de un socio (todos, activos y devueltos)
def test_socio_repository_get_prestamos_by_socio(session: Session, seed: None) -> None:
    repo = SocioRepository(session)
    # Socio 1 tiene 2 préstamos: 1 activo y 1 devuelto
    todos = repo.get_prestamos_by_socio(1)
    assert len(todos) == 2

    activos = repo.get_prestamos_by_socio(1, activos=True)
    assert len(activos) == 1
    assert activos[0].fecha_devolucion is None

    devueltos = repo.get_prestamos_by_socio(1, activos=False)
    assert len(devueltos) == 1
    assert devueltos[0].fecha_devolucion is not None
