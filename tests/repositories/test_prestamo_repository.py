from datetime import date, timedelta

from sqlmodel import Session

from models.libro import LibroDB
from models.prestamo import PrestamoDB
from repositories.prestamo_repository import PrestamoRepository


# Obtener listado de préstamos con paginación
def test_prestamo_repository_get_prestamos(session: Session, seed: None) -> None:
    repo = PrestamoRepository(session)
    prestamos = repo.get_prestamos(offset=0, limit=10)
    assert len(prestamos) == 3

    paginados = repo.get_prestamos(offset=1, limit=1)
    assert len(paginados) == 1
    assert paginados[0].id == 2


# Obtener préstamo por ID (existente e inexistente)
def test_prestamo_repository_get_by_id(session: Session, seed: None) -> None:
    repo = PrestamoRepository(session)
    prestamo = repo.get_prestamo_by_id(1)
    assert prestamo is not None
    assert prestamo.socio_id == 1
    assert prestamo.libro_id == 1

    inexistente = repo.get_prestamo_by_id(999)
    assert inexistente is None


# Crear un nuevo préstamo descontando stock del libro asociado
def test_prestamo_repository_create_prestamo(session: Session, seed: None) -> None:
    repo = PrestamoRepository(session)
    libro = session.get(LibroDB, 1)
    assert libro is not None
    stock_inicial = libro.stock

    nuevo_prestamo = PrestamoDB(
        socio_id=2,
        libro_id=1,
        fecha_prestamo=date.today(),
        fecha_vencimiento=date.today() + timedelta(days=14),
        fecha_devolucion=None,
        multa=0.0,
    )
    creado = repo.create_prestamo(nuevo_prestamo, libro)

    assert creado.id is not None
    assert creado.socio_id == 2
    assert creado.libro_id == 1
    # Verifica que el stock se haya descontado en la BD
    session.refresh(libro)
    assert libro.stock == stock_inicial - 1


# Registrar la devolución de un préstamo reponiendo stock del libro
def test_prestamo_repository_registrar_devolucion(session: Session, seed: None) -> None:
    repo = PrestamoRepository(session)
    prestamo = repo.get_prestamo_by_id(1)
    libro = session.get(LibroDB, 1)
    assert prestamo is not None
    assert libro is not None

    stock_previo = libro.stock
    fecha_dev = date.today()
    devuelto = repo.registrar_devolucion(
        prestamo=prestamo,
        libro=libro,
        fecha_devolucion=fecha_dev,
        multa=150.0,
    )

    assert devuelto.fecha_devolucion == fecha_dev
    assert devuelto.multa == 150.0

    session.refresh(libro)
    assert libro.stock == stock_previo + 1
