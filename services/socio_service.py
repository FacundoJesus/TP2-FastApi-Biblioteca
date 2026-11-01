from abc import ABC, abstractmethod
from collections.abc import Sequence

from api.payload.socio_dto import (
    SocioCreateRequest,
    SocioPatchRequest,
    SocioUpdateRequest,
)
from dependencies import SocioRepositoryDep
from exceptions import (
    DatosSocioInvalidosException,
    EmailDuplicadoException,
    SocioConPrestamosException,
    SocioNoEncontradoException,
)
from models import PrestamoDB, SocioDB


class SocioServiceInterface(ABC):
    @abstractmethod
    def get_socios(
        self,
        offset: int = 0,
        limit: int = 50,
        activos: bool | None = None,
    ) -> Sequence[SocioDB]:
        ...

    @abstractmethod
    def get_socio_by_id(self, socio_id: int) -> SocioDB:
        ...

    @abstractmethod
    def create_socio(self, payload: SocioCreateRequest) -> SocioDB:
        ...

    @abstractmethod
    def replace_socio(self, socio_id: int, payload: SocioUpdateRequest) -> SocioDB:
        ...

    @abstractmethod
    def update_socio(self, socio_id: int, payload: SocioPatchRequest) -> SocioDB:
        ...

    @abstractmethod
    def delete_socio(self, socio_id: int) -> None:
        ...

    @abstractmethod
    def get_prestamos_socio(
        self,
        socio_id: int,
        activos: bool | None = None,
    ) -> Sequence[PrestamoDB]:
        ...


class SocioService(SocioServiceInterface):
    def __init__(self, repo: SocioRepositoryDep) -> None:
        self.repo = repo

    def _validar_email_unico(self, email: str, socio_id_actual: int | None = None) -> None:
        existente = self.repo.get_socio_by_email(email)
        if existente is not None and existente.id != socio_id_actual:
            raise EmailDuplicadoException(email)

    def get_socios(
        self,
        offset: int = 0,
        limit: int = 50,
        activos: bool | None = None,
    ) -> Sequence[SocioDB]:
        return self.repo.get_socios(offset=offset, limit=limit, activos=activos)

    def get_socio_by_id(self, socio_id: int) -> SocioDB:
        socio = self.repo.get_socio_by_id(socio_id)
        if not socio:
            raise SocioNoEncontradoException(socio_id)
        return socio

    def create_socio(self, payload: SocioCreateRequest) -> SocioDB:
        self._validar_email_unico(str(payload.email))
        nuevo_socio = SocioDB.model_validate(payload)
        return self.repo.create_socio(nuevo_socio)

    def replace_socio(self, socio_id: int, payload: SocioUpdateRequest) -> SocioDB:
        socio = self.get_socio_by_id(socio_id)
        self._validar_email_unico(str(payload.email), socio_id_actual=socio_id)
        datos = payload.model_dump()
        return self.repo.update_socio(socio, datos)

    def update_socio(self, socio_id: int, payload: SocioPatchRequest) -> SocioDB:
        socio = self.get_socio_by_id(socio_id)
        datos = payload.model_dump(exclude_unset=True)

        campos_no_nulos = {
            "nombre": "El nombre del socio no puede ser nulo",
            "email": "El email del socio no puede ser nulo",
            "activo": "El estado activo del socio no puede ser nulo",
        }
        for campo, mensaje in campos_no_nulos.items():
            if campo in datos and datos[campo] is None:
                raise DatosSocioInvalidosException(mensaje)

        if "email" in datos:
            self._validar_email_unico(str(datos["email"]), socio_id_actual=socio_id)

        return self.repo.update_socio(socio, datos)

    def delete_socio(self, socio_id: int) -> None:
        socio = self.get_socio_by_id(socio_id)
        if socio.prestamos:
            raise SocioConPrestamosException()
        self.repo.delete_socio(socio)

    def get_prestamos_socio(
        self,
        socio_id: int,
        activos: bool | None = None,
    ) -> Sequence[PrestamoDB]:
        self.get_socio_by_id(socio_id)
        return self.repo.get_prestamos_by_socio(socio_id, activos=activos)
