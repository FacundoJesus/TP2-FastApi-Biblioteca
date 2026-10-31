from exceptions.base_exceptions import (
    ConflictoNegocioException,
    OperacionProhibidaException,
    RecursoNoEncontradoException,
    ReglaNegocioException,
)


# Excepcion con status = 404:
class SocioNoEncontradoException(RecursoNoEncontradoException):
    def __init__(self, socio_id: int) -> None:
        super().__init__(f"No se encontró el socio con id {socio_id}")


# Excepcion 403:
# Un socio inactivo no puede pedir préstamos
class SocioInactivoException(OperacionProhibidaException):
    def __init__(self, socio_id: int | None = None) -> None:
        detalle = (
            f"El socio con id {socio_id} está inactivo y no puede pedir préstamos"
            if socio_id is not None
            else "Un socio inactivo no puede pedir préstamos"
        )
        super().__init__(detalle)


# Excepcion con status = 409:
# Un socio no puede tener más de 3 préstamos activos
class SocioLimitePrestamosException(ConflictoNegocioException):
    def __init__(self, socio_id: int | None = None, max_prestamos: int = 3) -> None:
        detalle = (
            f"El socio con id {socio_id} ya alcanzó el límite de {max_prestamos} préstamos activos"
            if socio_id is not None
            else f"Un socio no puede tener más de {max_prestamos} préstamos activos"
        )
        super().__init__(detalle)


# Excepcion con status = 409:
# email duplicado
class EmailDuplicadoException(ConflictoNegocioException):
    def __init__(self, email: str | None = None) -> None:
        detalle = (
            f"Ya existe un socio registrado con el email '{email}'"
            if email is not None
            else "Ya existe un socio registrado con ese email"
        )
        super().__init__(detalle)


# Excepcion con status = 409:
class SocioConPrestamosException(ConflictoNegocioException):
    def __init__(self) -> None:
        super().__init__("No se puede eliminar un socio que tiene préstamos registrados")


# Excepcion con status = 400:
class DatosSocioInvalidosException(ReglaNegocioException):
    pass
