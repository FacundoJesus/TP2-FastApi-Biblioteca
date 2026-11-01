from sqlmodel import Field, SQLModel

from api.payload.libro_dto import LibroResumenResponse


class AutorResponse(SQLModel):
    id: int
    nombre: str
    nacionalidad: str
    libros: list[LibroResumenResponse] = []


GetAutoresResponse = AutorResponse


class AutorCreateRequest(SQLModel):
    nombre: str = Field(min_length=3, max_length=100)
    nacionalidad: str = Field(min_length=2, max_length=50)


class AutorUpdateRequest(SQLModel):
    nombre: str = Field(min_length=3, max_length=100)
    nacionalidad: str = Field(min_length=2, max_length=50)


class AutorPatchRequest(SQLModel):
    nombre: str | None = Field(default=None, min_length=3, max_length=100)
    nacionalidad: str | None = Field(default=None, min_length=2, max_length=50)
