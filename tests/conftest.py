from collections.abc import Generator
from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from main import app
from models.autor import AutorDB
from models.libro import LibroDB
from models.prestamo import PrestamoDB
from models.socio import SocioDB
from repositories.database import get_session


@pytest.fixture(name="session")
def session_fixture() -> Generator[Session, None, None]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    engine.dispose()


@pytest.fixture(name="client")
def client_fixture(session: Session) -> Generator[TestClient, None, None]:
    def get_session_override() -> Session:
        return session

    app.dependency_overrides[get_session] = get_session_override
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture(name="seed")
def seed_fixture(session: Session) -> None:
    # 1. Autores iniciales
    autor1 = AutorDB(nombre="Jorge Luis Borges", nacionalidad="Argentino")
    autor2 = AutorDB(nombre="Julio Cortázar", nacionalidad="Argentino")
    autor3 = AutorDB(nombre="Gabriel García Márquez", nacionalidad="Colombiano")
    session.add_all([autor1, autor2, autor3])
    session.commit()

    # 2. Libros asociados a autores
    libro1 = LibroDB(
        titulo="El Aleph",
        anio=1949,
        isbn="978-950-07-2575-0",
        stock=5,
        autores=[autor1],
    )
    libro2 = LibroDB(
        titulo="Rayuela",
        anio=1963,
        isbn="978-84-376-0494-7",
        stock=3,
        autores=[autor2],
    )
    libro3 = LibroDB(
        titulo="Cien años de soledad",
        anio=1967,
        isbn="978-0307474728",
        stock=4,
        autores=[autor3],
    )
    session.add_all([libro1, libro2, libro3])
    session.commit()

    # 3. Socios (activos e inactivos)
    socio1 = SocioDB(
        nombre="Juan Pérez",
        email="juan.perez@utn.edu.ar",
        activo=True,
    )
    socio2 = SocioDB(
        nombre="María López",
        email="maria.lopez@utn.edu.ar",
        activo=True,
    )
    socio3 = SocioDB(
        nombre="Carlos Gómez",
        email="carlos.gomez@utn.edu.ar",
        activo=False,
    )
    session.add_all([socio1, socio2, socio3])
    session.commit()

    # 4. Préstamos (activos, devueltos y vencidos)
    hoy = date.today()
    prestamo1 = PrestamoDB(
        socio=socio1,
        libro=libro1,
        fecha_prestamo=hoy - timedelta(days=3),
        fecha_vencimiento=hoy + timedelta(days=11),
        fecha_devolucion=None,
        multa=0.0,
    )
    prestamo2 = PrestamoDB(
        socio=socio1,
        libro=libro2,
        fecha_prestamo=hoy - timedelta(days=20),
        fecha_vencimiento=hoy - timedelta(days=6),
        fecha_devolucion=hoy - timedelta(days=4),
        multa=200.0,
    )
    prestamo3 = PrestamoDB(
        socio=socio2,
        libro=libro3,
        fecha_prestamo=hoy - timedelta(days=15),
        fecha_vencimiento=hoy - timedelta(days=1),
        fecha_devolucion=None,
        multa=0.0,
    )
    session.add_all([prestamo1, prestamo2, prestamo3])
    session.commit()


@pytest.fixture(name="bibliotecario_headers")
def bibliotecario_headers_fixture() -> dict[str, str]:
    return {"X-Rol": "bibliotecario"}


@pytest.fixture(name="socio_headers")
def socio_headers_fixture() -> dict[str, str]:
    return {"X-Rol": "socio", "X-Socio-Id": "1"}


@pytest.fixture(name="socio2_headers")
def socio2_headers_fixture() -> dict[str, str]:
    return {"X-Rol": "socio", "X-Socio-Id": "2"}
