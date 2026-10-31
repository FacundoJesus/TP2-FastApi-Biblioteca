class DominioException(Exception):
    """Excepción base para errores de reglas de negocio."""


class RecursoNoEncontradoException(DominioException):
    """Se lanza cuando una entidad solicitada no existe (HTTP 404)."""


class ConflictoNegocioException(DominioException):
    """Se lanza ante conflictos de integridad o estado (HTTP 409)."""


class ReglaNegocioException(DominioException):
    """Se lanza cuando una operación viola una validación de dominio (HTTP 400)."""
