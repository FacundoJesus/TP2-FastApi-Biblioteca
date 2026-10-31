class DominioException(Exception):
    """Excepción base para errores de reglas de negocio."""


# Excepcion con status = 404:
class RecursoNoEncontradoException(DominioException):
    """Recurso inexistente"""


# Excepcion con status = 409:
class ConflictoNegocioException(DominioException):
    """Se lanza ante conflictos de integridad o estado (HTTP 409)."""


# Excepcion con status = 403:
class OperacionProhibidaException(DominioException):
    """Se lanza cuando la entidad no tiene permitido realizar la acción (HTTP 403)."""


# Excepcion con status = 400:
class ReglaNegocioException(DominioException):
    """Se lanza cuando una operación viola una validación de dominio (HTTP 400)."""
