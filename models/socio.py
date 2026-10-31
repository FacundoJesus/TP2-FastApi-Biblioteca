from sqlmodel import Field, Relationship, SQLModel
from models.prestamo import PrestamoDB


class Socio(SQLModel):
    nombre: str = Field(min_length=3, max_length=100)
    email: str = Field(index=True, unique=True)
    activo: bool = Field(default=True)


class SocioDB(Socio, table=True):
    __tablename__ = "socios"
    
    id: int | None = Field(default=None, primary_key=True)
    # Relación 1 a N: Un socio tiene una lista de préstamos
    prestamos: list["PrestamoDB"] = Relationship(back_populates="socio")