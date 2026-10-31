from abc import ABC, abstractmethod
from collections.abc import Sequence

from api.payload.autor_dto import AutorCreate, AutorPatch, AutorUpdate
from dependencies import AutorRepositoryDep
from exceptions import (
    AutorConLibrosException,
    AutorNoEncontradoException,
    DatosAutorInvalidosException,
)
from models import AutorDB


class AutorServiceInterface(ABC):
    @abstractmethod
    def get_autores(self, offset: int = 0, limit: int = 50) -> Sequence[AutorDB]:
        ...

    @abstractmethod
    def get_autor_by_id(self, autor_id: int) -> AutorDB:
        ...

    @abstractmethod
    def create_autor(self, payload: AutorCreate) -> AutorDB:
        ...

    @abstractmethod
    def replace_autor(self, autor_id: int, payload: AutorUpdate) -> AutorDB:
        ...

    @abstractmethod
    def update_autor(self, autor_id: int, payload: AutorPatch) -> AutorDB:
        ...

    @abstractmethod
    def delete_autor(self, autor_id: int) -> None:
        ...


class AutorService(AutorServiceInterface):
    def __init__(self, repo: AutorRepositoryDep) -> None:
        self.repo = repo

    def get_autores(self, offset: int = 0, limit: int = 50) -> Sequence[AutorDB]:
        return self.repo.get_autores(offset, limit)

    def get_autor_by_id(self, autor_id: int) -> AutorDB:
        autor = self.repo.get_autor_by_id(autor_id)
        if not autor:
            raise AutorNoEncontradoException(autor_id)
        return autor

    def create_autor(self, payload: AutorCreate) -> AutorDB:
        nuevo_autor = AutorDB.model_validate(payload)
        return self.repo.create_autor(nuevo_autor)

    def replace_autor(self, autor_id: int, payload: AutorUpdate) -> AutorDB:
        autor = self.get_autor_by_id(autor_id)
        datos = payload.model_dump()
        return self.repo.update_autor(autor, datos)

    def update_autor(self, autor_id: int, payload: AutorPatch) -> AutorDB:
        autor = self.get_autor_by_id(autor_id)
        datos = payload.model_dump(exclude_unset=True)
        if "nombre" in datos and datos["nombre"] is None:
            raise DatosAutorInvalidosException("El nombre del autor no puede ser nulo")
        return self.repo.update_autor(autor, datos)

    def delete_autor(self, autor_id: int) -> None:
        autor = self.get_autor_by_id(autor_id)
        if autor.libros:
            raise AutorConLibrosException()
        self.repo.delete_autor(autor)
