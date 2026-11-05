import pytest
from sqlmodel import Session

from api.payload.socio_dto import (
    SocioCreateRequest,
    SocioPatchRequest,
    SocioUpdateRequest,
)
from exceptions import (
    DatosSocioInvalidosException,
    EmailDuplicadoException,
    SocioConPrestamosException,
    SocioNoEncontradoException,
)
from repositories.socio_repository import SocioRepository
from services.socio_service import SocioService


# Obtener listado de socios en el servicio
def test_socio_service_get_socios(session: Session, seed: None) -> None:
    service = SocioService(SocioRepository(session))
    socios = service.get_socios(offset=0, limit=10)
    assert len(socios) == 3


# Filtrar socios por estado activo en el servicio
def test_socio_service_get_socios_activos(session: Session, seed: None) -> None:
    service = SocioService(SocioRepository(session))
    activos = service.get_socios(activos=True)
    assert len(activos) == 2

    inactivos = service.get_socios(activos=False)
    assert len(inactivos) == 1
    assert inactivos[0].id == 3


# Obtener socio por ID existente
def test_socio_service_get_socio_by_id_ok(session: Session, seed: None) -> None:
    service = SocioService(SocioRepository(session))
    socio = service.get_socio_by_id(1)
    assert socio.id == 1
    assert socio.nombre == "Juan Pérez"


# Error al obtener socio por ID inexistente (SocioNoEncontradoException)
def test_socio_service_get_socio_by_id_not_found(session: Session, seed: None) -> None:
    service = SocioService(SocioRepository(session))
    with pytest.raises(SocioNoEncontradoException):
        service.get_socio_by_id(999)


# Crear socio con datos válidos en el servicio
def test_socio_service_create_socio_ok(session: Session) -> None:
    service = SocioService(SocioRepository(session))
    payload = SocioCreateRequest(
        nombre="Lucía Ramos",
        email="lucia.ramos@utn.edu.ar",
        activo=True,
    )
    creado = service.create_socio(payload)
    assert creado.id is not None
    assert creado.email == "lucia.ramos@utn.edu.ar"


# Error al crear socio con email duplicado (EmailDuplicadoException)
def test_socio_service_create_socio_email_duplicado(session: Session, seed: None) -> None:
    service = SocioService(SocioRepository(session))
    payload = SocioCreateRequest(
        nombre="Otro Juan",
        email="juan.perez@utn.edu.ar",  # ya existe en el seed
        activo=True,
    )
    with pytest.raises(EmailDuplicadoException):
        service.create_socio(payload)


# Reemplazo completo de un socio existente (PUT)
def test_socio_service_replace_socio_ok(session: Session, seed: None) -> None:
    service = SocioService(SocioRepository(session))
    payload = SocioUpdateRequest(
        nombre="Juan P. Pérez",
        email="juan.perez@utn.edu.ar",
        activo=False,
    )
    reemplazado = service.replace_socio(1, payload)
    assert reemplazado.nombre == "Juan P. Pérez"
    assert not reemplazado.activo


# Error al reemplazar socio con email de otro socio
def test_socio_service_replace_socio_email_duplicado(session: Session, seed: None) -> None:
    service = SocioService(SocioRepository(session))
    # Intentar asignar al socio 1 el email de la socia 2
    payload = SocioUpdateRequest(
        nombre="Conflicto Email",
        email="maria.lopez@utn.edu.ar",
        activo=True,
    )
    with pytest.raises(EmailDuplicadoException):
        service.replace_socio(1, payload)


# Actualización parcial de un socio (PATCH)
def test_socio_service_update_socio_patch_ok(session: Session, seed: None) -> None:
    service = SocioService(SocioRepository(session))
    payload = SocioPatchRequest(activo=False)
    actualizado = service.update_socio(1, payload)
    assert not actualizado.activo
    assert actualizado.nombre == "Juan Pérez"


# Error al actualizar socio con campos nulos prohibidos (DatosSocioInvalidosException)
def test_socio_service_update_socio_patch_invalid_null(session: Session, seed: None) -> None:
    service = SocioService(SocioRepository(session))
    with pytest.raises(DatosSocioInvalidosException):
        service.update_socio(1, SocioPatchRequest.model_construct(nombre=None))

    with pytest.raises(DatosSocioInvalidosException):
        service.update_socio(1, SocioPatchRequest.model_construct(email=None))

    with pytest.raises(DatosSocioInvalidosException):
        service.update_socio(1, SocioPatchRequest.model_construct(activo=None))


# Eliminar un socio sin préstamos con éxito
def test_socio_service_delete_socio_ok(session: Session, seed: None) -> None:
    service = SocioService(SocioRepository(session))
    # Socio 3 no tiene préstamos registrados
    service.delete_socio(3)
    with pytest.raises(SocioNoEncontradoException):
        service.get_socio_by_id(3)


# Error al eliminar socio con préstamos registrados (SocioConPrestamosException)
def test_socio_service_delete_socio_con_prestamos(session: Session, seed: None) -> None:
    service = SocioService(SocioRepository(session))
    # Socio 1 tiene préstamos asociados
    with pytest.raises(SocioConPrestamosException):
        service.delete_socio(1)


# Obtener préstamos de un socio en el servicio
def test_socio_service_get_prestamos_socio_ok(session: Session, seed: None) -> None:
    service = SocioService(SocioRepository(session))
    prestamos = service.get_prestamos_socio(1)
    assert len(prestamos) == 2

    activos = service.get_prestamos_socio(1, activos=True)
    assert len(activos) == 1
    assert activos[0].fecha_devolucion is None


# Error al obtener préstamos de un socio inexistente
def test_socio_service_get_prestamos_socio_not_found(session: Session, seed: None) -> None:
    service = SocioService(SocioRepository(session))
    with pytest.raises(SocioNoEncontradoException):
        service.get_prestamos_socio(999)
