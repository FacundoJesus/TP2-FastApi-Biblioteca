from sqlmodel import Field, SQLModel


# Esta es la tabla intermedia entre Libro y Autor
class LibroAutorLink(SQLModel, table=True):
    __tablename__ = "libros_autores"

    libro_id: int = Field(foreign_key="libros.id", primary_key=True)
    autor_id: int = Field(foreign_key="autores.id", primary_key=True)
