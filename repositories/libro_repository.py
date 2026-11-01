from collections.abc import Sequence

from sqlmodel import col, select

from dependencies import SessionDep
from models import AutorDB, LibroDB


class LibroRepository:
    def __init__(self, session: SessionDep) -> None:
        self.session = session

    def get_libros(
        self,
        offset: int = 0,
        limit: int = 50,
        disponibles: bool | None = None,
    ) -> Sequence[LibroDB]:
        statement = select(LibroDB)

        if disponibles is True:
            statement = statement.where(col(LibroDB.stock) > 0)
        elif disponibles is False:
            statement = statement.where(col(LibroDB.stock) == 0)

        statement = statement.offset(offset).limit(limit)
        return self.session.exec(statement).all()

    def get_libro_by_id(self, libro_id: int) -> LibroDB | None:
        return self.session.get(LibroDB, libro_id)

    def get_libro_by_isbn(self, isbn: str) -> LibroDB | None:
        statement = select(LibroDB).where(col(LibroDB.isbn) == isbn)
        return self.session.exec(statement).first()

    def create_libro(self, libro: LibroDB) -> LibroDB:
        self.session.add(libro)
        self.session.commit()
        self.session.refresh(libro)
        return libro

    def update_libro(self, libro: LibroDB, datos: dict[str, object]) -> LibroDB:
        libro.sqlmodel_update(datos)
        self.session.add(libro)
        self.session.commit()
        self.session.refresh(libro)
        return libro

    def add_autor_to_libro(self, libro: LibroDB, autor: AutorDB) -> LibroDB:
        libro.autores.append(autor)
        self.session.add(libro)
        self.session.commit()
        self.session.refresh(libro)
        return libro

    def delete_libro(self, libro: LibroDB) -> None:
        self.session.delete(libro)
        self.session.commit()
