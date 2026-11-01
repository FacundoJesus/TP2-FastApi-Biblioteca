from exceptions.base_exceptions import (
    ConflictoNegocioException,
    RecursoNoEncontradoException,
)


# Excepcion con status = 404:
class PrestamoNoEncontradoException(RecursoNoEncontradoException):
    def __init__(self, prestamo_id: int) -> None:
        super().__init__(f"No se encontró el préstamo con id {prestamo_id}")


# Excepcion con status = 409:
class PrestamoYaDevueltoException(ConflictoNegocioException):
    def __init__(self, prestamo_id: int | None = None) -> None:
        detalle = (
            f"El préstamo con id {prestamo_id} ya fue devuelto"
            if prestamo_id is not None
            else "El préstamo ya fue devuelto anteriormente"
        )
        super().__init__(detalle)
