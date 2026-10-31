from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from models.libro_autor import LibroAutorLink

if TYPE_CHECKING:
    from models.autor import AutorDB
    from models.prestamo import PrestamoDB


class Libro(SQLModel):
    titulo: str = Field(max_length=72, min_length=4)
    anio: int | None = Field(default=None, ge=1900, le=2026)
    isbn: str = Field(min_length=10, max_length=17, unique=True, index=True)
    stock: int = Field(default=0, ge=0)


class LibroDB(Libro, table=True):
    __tablename__ = "libros"

    id: int | None = Field(default=None, primary_key=True)
    # Relación 1 a N: Un libro tiene una lista de préstamos
    prestamos: list["PrestamoDB"] = Relationship(back_populates="libro")
    # Relación N a N: Un libro tiene una lista de autores
    autores: list["AutorDB"] = Relationship(back_populates="libros", link_model=LibroAutorLink)
