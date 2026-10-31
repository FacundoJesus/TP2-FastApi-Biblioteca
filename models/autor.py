from sqlmodel import Field, Relationship, SQLModel
from models.libro import LibroDB;
from models.libro_autor import LibroAutorLink;

class Autor(SQLModel):
    nombre: str = Field(min_length=3, max_length=100)
    nacionalidad: str | None = Field(default=None, max_length=50)



class AutorDB(Autor, table=True):
    __tablename__ = "autores"
    
    id: int | None = Field(default=None, primary_key=True)
    # Relación N a N: Un autor tiene una lista de libros
    libros: list["LibroDB"] = Relationship(back_populates="autores", link_model=LibroAutorLink)