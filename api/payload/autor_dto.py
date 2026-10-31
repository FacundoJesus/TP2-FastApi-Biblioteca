from sqlmodel import Field, SQLModel

from api.payload.libro_dto import LibroResponse


class AutorResponse(SQLModel):
    id: int
    nombre: str
    nacionalidad: str | None = None
    libros: list[LibroResponse] = []


GetAutoresResponse = AutorResponse


class AutorCreate(SQLModel):
    nombre: str = Field(min_length=3, max_length=100)
    nacionalidad: str | None = Field(default=None, max_length=50)


class AutorUpdate(SQLModel):
    nombre: str = Field(min_length=3, max_length=100)
    nacionalidad: str | None = Field(default=None, max_length=50)


class AutorPatch(SQLModel):
    nombre: str | None = Field(default=None, min_length=3, max_length=100)
    nacionalidad: str | None = Field(default=None, max_length=50)
