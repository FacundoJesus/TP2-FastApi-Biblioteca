from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from datetime import date, timedelta

from fastapi import FastAPI
from sqlmodel import Session, select

from api import autor_controller, libro_controller, socio_controller
from models.autor import AutorDB
from models.libro import LibroDB
from models.prestamo import PrestamoDB
from models.socio import SocioDB
from repositories.database import create_db_and_tables, engine


app = FastAPI(title="TP2 - Biblioteca API")

# Aca van los routers
app.include_router(libro_controller.router)
app.include_router(autor_controller.router)
app.include_router(socio_controller.router)


def create_dummy_data() -> None:
    with Session(engine) as session:
        # 1. Cláusula de salvaguarda: si ya hay libros en la BD, no hace nada
        if session.exec(select(LibroDB)).first():
            return

        # 2. Creamos algunos Autores primero
        autor1 = AutorDB(nombre="Jorge Luis Borges", nacionalidad="Argentino")
        autor2 = AutorDB(nombre="Julio Cortázar", nacionalidad="Argentino")
        autor3 = AutorDB(nombre="Gabriel García Márquez", nacionalidad="Colombiano")

        session.add_all([autor1, autor2, autor3])
        session.commit()  # Guardamos para que la BD les asigne IDs

        # 3. Creamos los Libros asignándoles sus autores directamente
        # ¡SQLModel se encarga de llenar la tabla LibroAutorLink por detrás!
        libro1 = LibroDB(
            titulo="El Aleph",
            anio=1949,
            isbn="978-950-07-2575-0",
            stock=5,
            autores=[autor1],  # Relación N a N
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

        # 4. Guardamos los libros con sus relaciones
        session.add_all([libro1, libro2, libro3])
        session.commit()

        # 5. Creamos 3 Socios (2 activos y 1 inactivo para pruebas)
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

        # 6. Creamos algunos Préstamos de prueba (activos, vencidos y devueltos)
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


@app.on_event("startup")
def on_startup() -> None:
    create_db_and_tables()
    create_dummy_data()