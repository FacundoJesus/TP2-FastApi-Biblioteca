from exceptions.base_exceptions import (
    OperacionProhibidaException,
    ReglaNegocioException,
)


class AccesoDenegadoRolException(OperacionProhibidaException):
    def __init__(self, mensaje: str = "Permiso insuficiente para realizar esta operación") -> None:
        super().__init__(mensaje)


class SocioIdRequeridoException(ReglaNegocioException):
    def __init__(self) -> None:
        super().__init__("Debe especificar la cabecera 'X-Socio-Id' cuando opera como socio")
