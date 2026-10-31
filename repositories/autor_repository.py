from collections.abc import Sequence

from sqlmodel import select

from dependencies import SessionDep
from models import AutorDB


class AutorRepository:
    def __init__(self, session: SessionDep) -> None:
        self.session = session

    def get_autores(self, offset: int = 0, limit: int = 50) -> Sequence[AutorDB]:
        statement = select(AutorDB).offset(offset).limit(limit)
        result = self.session.exec(statement)
        return result.all()

    def get_autor_by_id(self, autor_id: int) -> AutorDB | None:
        return self.session.get(AutorDB, autor_id)

    def create_autor(self, autor: AutorDB) -> AutorDB:
        self.session.add(autor)
        self.session.commit()
        self.session.refresh(autor)
        return autor

    def update_autor(self, autor: AutorDB, datos: dict[str, object]) -> AutorDB:
        autor.sqlmodel_update(datos)
        self.session.add(autor)
        self.session.commit()
        self.session.refresh(autor)
        return autor

    def delete_autor(self, autor: AutorDB) -> None:
        self.session.delete(autor)
        self.session.commit()
