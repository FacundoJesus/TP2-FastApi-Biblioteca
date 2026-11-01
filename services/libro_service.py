from abc import ABC, abstractmethod
from collections.abc import Sequence

from api.payload.libro_dto import (
    LibroCreateRequest,
    LibroPatchRequest,
    LibroUpdateRequest,
)
from dependencies import AutorRepositoryDep, LibroRepositoryDep
from exceptions import (
    AutorNoEncontradoException,
    AutorYaAsociadoException,
    DatosLibroInvalidosException,
    IsbnDuplicadoException,
    LibroConPrestamosException,
    LibroNoEncontradoException,
)
from models import LibroDB


class LibroServiceInterface(ABC):
    @abstractmethod
    def get_libros(
        self,
        offset: int = 0,
        limit: int = 50,
        disponibles: bool | None = None,
    ) -> Sequence[LibroDB]:
        ...

    @abstractmethod
    def get_libro_by_id(self, libro_id: int) -> LibroDB:
        ...

    @abstractmethod
    def create_libro(self, payload: LibroCreateRequest) -> LibroDB:
        ...

    @abstractmethod
    def replace_libro(self, libro_id: int, payload: LibroUpdateRequest) -> LibroDB:
        ...

    @abstractmethod
    def update_libro(self, libro_id: int, payload: LibroPatchRequest) -> LibroDB:
        ...

    @abstractmethod
    def asociar_autor(self, libro_id: int, autor_id: int) -> LibroDB:
        ...

    @abstractmethod
    def delete_libro(self, libro_id: int) -> None:
        ...


class LibroService(LibroServiceInterface):
    def __init__(
        self,
        repo: LibroRepositoryDep,
        autor_repo: AutorRepositoryDep,
    ) -> None:
        self.repo = repo
        self.autor_repo = autor_repo

    def _validar_isbn_unico(self, isbn: str, libro_id_actual: int | None = None) -> None:
        existente = self.repo.get_libro_by_isbn(isbn)
        if existente is not None and existente.id != libro_id_actual:
            raise IsbnDuplicadoException(isbn)

    def get_libros(
        self,
        offset: int = 0,
        limit: int = 50,
        disponibles: bool | None = None,
    ) -> Sequence[LibroDB]:
        return self.repo.get_libros(
            offset=offset,
            limit=limit,
            disponibles=disponibles,
        )

    def get_libro_by_id(self, libro_id: int) -> LibroDB:
        libro = self.repo.get_libro_by_id(libro_id)
        if not libro:
            raise LibroNoEncontradoException(libro_id)
        return libro

    def create_libro(self, payload: LibroCreateRequest) -> LibroDB:
        self._validar_isbn_unico(payload.isbn)
        nuevo_libro = LibroDB.model_validate(payload)
        return self.repo.create_libro(nuevo_libro)

    def replace_libro(self, libro_id: int, payload: LibroUpdateRequest) -> LibroDB:
        libro = self.get_libro_by_id(libro_id)
        self._validar_isbn_unico(payload.isbn, libro_id_actual=libro_id)
        datos = payload.model_dump()
        return self.repo.update_libro(libro, datos)

    def update_libro(self, libro_id: int, payload: LibroPatchRequest) -> LibroDB:
        libro = self.get_libro_by_id(libro_id)
        datos = payload.model_dump(exclude_unset=True)

        campos_no_nulos = {
            "titulo": "El título del libro no puede ser nulo",
            "isbn": "El ISBN del libro no puede ser nulo",
            "stock": "El stock del libro no puede ser nulo",
        }
        for campo, mensaje in campos_no_nulos.items():
            if campo in datos and datos[campo] is None:
                raise DatosLibroInvalidosException(mensaje)

        if "isbn" in datos:
            self._validar_isbn_unico(str(datos["isbn"]), libro_id_actual=libro_id)

        return self.repo.update_libro(libro, datos)

    def asociar_autor(self, libro_id: int, autor_id: int) -> LibroDB:
        libro = self.get_libro_by_id(libro_id)
        autor = self.autor_repo.get_autor_by_id(autor_id)
        if not autor:
            raise AutorNoEncontradoException(autor_id)
        if any(a.id == autor_id for a in libro.autores):
            raise AutorYaAsociadoException(libro_id, autor_id)
        return self.repo.add_autor_to_libro(libro, autor)

    def delete_libro(self, libro_id: int) -> None:
        libro = self.get_libro_by_id(libro_id)
        if libro.prestamos:
            raise LibroConPrestamosException()
        self.repo.delete_libro(libro)
