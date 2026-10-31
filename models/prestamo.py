from sqlmodel import Field, Relationship, SQLModel
from datetime import date
from models.libro import LibroDB
from models.socio import SocioDB

class Prestamo(SQLModel):
    fecha_prestamo: date = Field(default_factory=date.today)
    fecha_vencimiento: date
    fecha_devolucion: date | None = Field(default=None)
    multa: float = Field(default=0.0, ge=0.0)


class PrestamoDB(Prestamo, table=True):
    __tablename__ = "prestamos"

    id: int | None = Field(default=None, primary_key=True)
    socio_id: int = Field(foreign_key="socios.id")
    libro_id: int = Field(foreign_key="libros.id")
    # Préstamo N - 1 Libro
    libro: "LibroDB" = Relationship(back_populates="prestamos")
    # Préstamo N - 1 Socio
    socio: "SocioDB" = Relationship(back_populates="prestamos")