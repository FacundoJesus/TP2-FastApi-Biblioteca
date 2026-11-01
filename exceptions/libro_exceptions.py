from exceptions.base_exceptions import (
    ConflictoNegocioException,
    RecursoNoEncontradoException,
    ReglaNegocioException,
)


# Excepcion con status = 404:
class LibroNoEncontradoException(RecursoNoEncontradoException):
    def __init__(self, libro_id: int) -> None:
        super().__init__(f"No se encontró el libro con id {libro_id}")


# Excepcion con status = 409:
# No se presta un libro sin stock; al prestar se descuenta 1
class LibroSinStockException(ConflictoNegocioException):
    def __init__(self, libro_id: int | None = None) -> None:
        detalle = (
            f"El libro con id {libro_id} no tiene stock disponible para préstamo"
            if libro_id is not None
            else "No se puede prestar un libro sin stock disponible"
        )
        super().__init__(detalle)


# Excepcion con status = 409:
# ISBN duplicado
class IsbnDuplicadoException(ConflictoNegocioException):
    def __init__(self, isbn: str | None = None) -> None:
        detalle = (
            f"Ya existe un libro registrado con el ISBN '{isbn}'"
            if isbn is not None
            else "Ya existe un libro registrado con ese ISBN"
        )
        super().__init__(detalle)


# Excepcion con status = 409:
class AutorYaAsociadoException(ConflictoNegocioException):
    def __init__(self, libro_id: int, autor_id: int) -> None:
        super().__init__(
            f"El autor con id {autor_id} ya está asociado al libro con id {libro_id}"
        )


# Excepcion con status = 409:
class LibroConPrestamosException(ConflictoNegocioException):
    def __init__(self) -> None:
        super().__init__("No se puede eliminar un libro que tiene préstamos registrados")


# Excepcion con status = 400:
class DatosLibroInvalidosException(ReglaNegocioException):
    pass
