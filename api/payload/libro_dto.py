from sqlmodel import SQLModel


class LibroResponse(SQLModel):
    titulo: str
    anio: int | None = None
    isbn: str
    stock: int
