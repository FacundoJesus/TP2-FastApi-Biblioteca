from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlmodel import Session, select

from api import autor_controller, libro_controller, socio_controller
from models.autor import AutorDB
from models.libro import LibroDB
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


@app.on_event("startup")
def on_startup() -> None:
    create_db_and_tables()
    create_dummy_data()