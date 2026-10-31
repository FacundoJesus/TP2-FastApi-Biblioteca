from sqlmodel import SQLModel

from api.payload.libro_dto import LibroResponse


class GetAutoresResponse(SQLModel):
    id: int
    nombre: str
    nacionalidad: str | None = None
    libros: list[LibroResponse] = []
