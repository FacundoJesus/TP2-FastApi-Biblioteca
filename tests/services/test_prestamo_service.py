from datetime import date, timedelta

import pytest
from sqlmodel import Session

from api.payload.prestamo_dto import PrestamoCreateRequest
from exceptions import (
    LibroNoEncontradoException,
    LibroSinStockException,
    PrestamoNoEncontradoException,
    PrestamoYaDevueltoException,
    SocioInactivoException,
    SocioLimitePrestamosException,
    SocioNoEncontradoException,
)
from models.libro import LibroDB
from repositories.libro_repository import LibroRepository
from repositories.prestamo_repository import PrestamoRepository
from repositories.socio_repository import SocioRepository
from services.prestamo_service import (
    MAX_PRESTAMOS_ACTIVOS,
    PLAZO_PRESTAMO_DIAS,
    PrestamoService,
)


# Obtener listado de préstamos en el servicio
def test_prestamo_service_get_prestamos(session: Session, seed: None) -> None:
    service = PrestamoService(
        PrestamoRepository(session),
        SocioRepository(session),
        LibroRepository(session),
    )
    prestamos = service.get_prestamos(offset=0, limit=10)
    assert len(prestamos) == 3


# Obtener préstamo por ID existente
def test_prestamo_service_get_prestamo_by_id_ok(session: Session, seed: None) -> None:
    service = PrestamoService(
        PrestamoRepository(session),
        SocioRepository(session),
        LibroRepository(session),
    )
    prestamo = service.get_prestamo_by_id(1)
    assert prestamo.id == 1
    assert prestamo.socio_id == 1


# Error al obtener préstamo por ID inexistente (PrestamoNoEncontradoException)
def test_prestamo_service_get_prestamo_by_id_not_found(session: Session, seed: None) -> None:
    service = PrestamoService(
        PrestamoRepository(session),
        SocioRepository(session),
        LibroRepository(session),
    )
    with pytest.raises(PrestamoNoEncontradoException):
        service.get_prestamo_by_id(999)


# Crear préstamo válido (plazo de 14 días y descuento de stock)
def test_prestamo_service_create_prestamo_ok(session: Session, seed: None) -> None:
    libro_repo = LibroRepository(session)
    service = PrestamoService(
        PrestamoRepository(session),
        SocioRepository(session),
        libro_repo,
    )
    libro = libro_repo.get_libro_by_id(2)
    assert libro is not None
    stock_inicial = libro.stock

    payload = PrestamoCreateRequest(socio_id=1, libro_id=2)
    creado = service.create_prestamo(payload)

    assert creado.id is not None
    assert creado.socio_id == 1
    assert creado.libro_id == 2
    assert creado.fecha_prestamo == date.today()
    assert creado.fecha_vencimiento == date.today() + timedelta(days=PLAZO_PRESTAMO_DIAS)
    assert creado.fecha_devolucion is None

    libro_actualizado = libro_repo.get_libro_by_id(2)
    assert libro_actualizado is not None
    assert libro_actualizado.stock == stock_inicial - 1


# Error al crear préstamo con socio inexistente (SocioNoEncontradoException)
def test_prestamo_service_create_prestamo_socio_no_encontrado(session: Session, seed: None) -> None:
    service = PrestamoService(
        PrestamoRepository(session),
        SocioRepository(session),
        LibroRepository(session),
    )
    payload = PrestamoCreateRequest(socio_id=999, libro_id=1)
    with pytest.raises(SocioNoEncontradoException):
        service.create_prestamo(payload)


# Error al crear préstamo con socio inactivo (SocioInactivoException)
def test_prestamo_service_create_prestamo_socio_inactivo(session: Session, seed: None) -> None:
    service = PrestamoService(
        PrestamoRepository(session),
        SocioRepository(session),
        LibroRepository(session),
    )
    # Socio 3 está inactivo en el seed
    payload = PrestamoCreateRequest(socio_id=3, libro_id=1)
    with pytest.raises(SocioInactivoException):
        service.create_prestamo(payload)


# Error al crear préstamo cuando el socio alcanza el límite de préstamos activos (SocioLimitePrestamosException)
def test_prestamo_service_create_prestamo_limite_alcanzado(session: Session, seed: None) -> None:
    service = PrestamoService(
        PrestamoRepository(session),
        SocioRepository(session),
        LibroRepository(session),
    )
    # Socio 1 tiene 1 préstamo activo en el seed. Agregamos 2 más para alcanzar 3 (el máximo permitido).
    service.create_prestamo(PrestamoCreateRequest(socio_id=1, libro_id=1))
    service.create_prestamo(PrestamoCreateRequest(socio_id=1, libro_id=1))

    # El 4to préstamo debe ser rechazado
    with pytest.raises(SocioLimitePrestamosException):
        service.create_prestamo(PrestamoCreateRequest(socio_id=1, libro_id=1))


# Error al crear préstamo con libro inexistente (LibroNoEncontradoException)
def test_prestamo_service_create_prestamo_libro_no_encontrado(session: Session, seed: None) -> None:
    service = PrestamoService(
        PrestamoRepository(session),
        SocioRepository(session),
        LibroRepository(session),
    )
    payload = PrestamoCreateRequest(socio_id=1, libro_id=999)
    with pytest.raises(LibroNoEncontradoException):
        service.create_prestamo(payload)


# Error al crear préstamo cuando el libro no tiene stock (LibroSinStockException)
def test_prestamo_service_create_prestamo_libro_sin_stock(session: Session, seed: None) -> None:
    libro_repo = LibroRepository(session)
    service = PrestamoService(
        PrestamoRepository(session),
        SocioRepository(session),
        libro_repo,
    )
    # Dejar el libro 2 con stock 0
    libro = libro_repo.get_libro_by_id(2)
    assert libro is not None
    libro_repo.update_libro(libro, {"stock": 0})

    payload = PrestamoCreateRequest(socio_id=1, libro_id=2)
    with pytest.raises(LibroSinStockException):
        service.create_prestamo(payload)


# Devolución a término sin multa (repone stock del libro)
def test_prestamo_service_registrar_devolucion_sin_multa(session: Session, seed: None) -> None:
    libro_repo = LibroRepository(session)
    service = PrestamoService(
        PrestamoRepository(session),
        SocioRepository(session),
        libro_repo,
    )
    libro_1 = libro_repo.get_libro_by_id(1)
    assert libro_1 is not None
    stock_previo = libro_1.stock

    # Préstamo 1 no está vencido (vence en 11 días)
    devuelto = service.registrar_devolucion(1)
    assert devuelto.fecha_devolucion == date.today()
    assert devuelto.multa == 0.0

    session.refresh(libro_1)
    assert libro_1.stock == stock_previo + 1


# Devolución con atraso y cálculo de multa ($100 por día de atraso)
def test_prestamo_service_registrar_devolucion_con_multa(session: Session, seed: None) -> None:
    service = PrestamoService(
        PrestamoRepository(session),
        SocioRepository(session),
        LibroRepository(session),
    )
    # Préstamo 3 venció hace 1 día (multa = 100.0)
    devuelto = service.registrar_devolucion(3)
    assert devuelto.fecha_devolucion == date.today()
    assert devuelto.multa == 100.0


# Error al devolver un préstamo ya devuelto (PrestamoYaDevueltoException)
def test_prestamo_service_registrar_devolucion_ya_devuelto(session: Session, seed: None) -> None:
    service = PrestamoService(
        PrestamoRepository(session),
        SocioRepository(session),
        LibroRepository(session),
    )
    # Préstamo 2 ya fue devuelto en el seed
    with pytest.raises(PrestamoYaDevueltoException):
        service.registrar_devolucion(2)


# Error al devolver un préstamo inexistente (PrestamoNoEncontradoException)
def test_prestamo_service_registrar_devolucion_inexistente(session: Session, seed: None) -> None:
    service = PrestamoService(
        PrestamoRepository(session),
        SocioRepository(session),
        LibroRepository(session),
    )
    with pytest.raises(PrestamoNoEncontradoException):
        service.registrar_devolucion(999)
