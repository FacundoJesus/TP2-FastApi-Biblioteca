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
        autores = result.all()
        return autores
