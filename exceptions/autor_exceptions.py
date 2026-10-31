from exceptions.base_exceptions import (
    ConflictoNegocioException,
    RecursoNoEncontradoException,
    ReglaNegocioException,
)


class AutorNoEncontradoException(RecursoNoEncontradoException):
    def __init__(self, autor_id: int) -> None:
        super().__init__(f"No se encontró el autor con id {autor_id}")


class AutorConLibrosException(ConflictoNegocioException):
    def __init__(self) -> None:
        super().__init__("No se puede eliminar un autor que tiene libros asociados")


class DatosAutorInvalidosException(ReglaNegocioException):
    pass
