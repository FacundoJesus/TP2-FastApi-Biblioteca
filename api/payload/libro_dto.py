from sqlmodel import Field, SQLModel


class AutorResumenResponse(SQLModel):
    id: int
    nombre: str
    nacionalidad: str


class LibroResumenResponse(SQLModel):
    id: int
    titulo: str
    anio: int | None = None
    isbn: str
    stock: int


class LibroResponse(LibroResumenResponse):
    autores: list[AutorResumenResponse] = []


class LibroCreateRequest(SQLModel):
    titulo: str = Field(min_length=4, max_length=72)
    anio: int | None = Field(default=None, ge=1900, le=2026)
    isbn: str = Field(min_length=10, max_length=17)
    stock: int = Field(default=0, ge=0)


class LibroUpdateRequest(SQLModel):
    titulo: str = Field(min_length=4, max_length=72)
    anio: int | None = Field(default=None, ge=1900, le=2026)
    isbn: str = Field(min_length=10, max_length=17)
    stock: int = Field(ge=0)


class LibroPatchRequest(SQLModel):
    titulo: str | None = Field(default=None, min_length=4, max_length=72)
    anio: int | None = Field(default=None, ge=1900, le=2026)
    isbn: str | None = Field(default=None, min_length=10, max_length=17)
    stock: int | None = Field(default=None, ge=0)
