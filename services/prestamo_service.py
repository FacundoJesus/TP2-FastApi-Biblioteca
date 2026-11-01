from abc import ABC, abstractmethod
from collections.abc import Sequence
from datetime import date, timedelta

from api.payload.prestamo_dto import PrestamoCreateRequest
from dependencies import LibroRepositoryDep, PrestamoRepositoryDep, SocioRepositoryDep
from exceptions import (
    LibroNoEncontradoException,
    LibroSinStockException,
    PrestamoNoEncontradoException,
    PrestamoYaDevueltoException,
    SocioInactivoException,
    SocioLimitePrestamosException,
    SocioNoEncontradoException,
)
from models import PrestamoDB

PLAZO_PRESTAMO_DIAS = 14
MAX_PRESTAMOS_ACTIVOS = 3
MONTO_MULTA_POR_DIA = 100.0


class PrestamoServiceInterface(ABC):
    @abstractmethod
    def get_prestamos(self, offset: int = 0, limit: int = 50) -> Sequence[PrestamoDB]:
        ...

    @abstractmethod
    def get_prestamo_by_id(self, prestamo_id: int) -> PrestamoDB:
        ...

    @abstractmethod
    def create_prestamo(self, payload: PrestamoCreateRequest) -> PrestamoDB:
        ...

    @abstractmethod
    def registrar_devolucion(self, prestamo_id: int) -> PrestamoDB:
        ...


class PrestamoService(PrestamoServiceInterface):
    def __init__(
        self,
        repo: PrestamoRepositoryDep,
        socio_repo: SocioRepositoryDep,
        libro_repo: LibroRepositoryDep,
    ) -> None:
        self.repo = repo
        self.socio_repo = socio_repo
        self.libro_repo = libro_repo

    def get_prestamos(self, offset: int = 0, limit: int = 50) -> Sequence[PrestamoDB]:
        return self.repo.get_prestamos(offset=offset, limit=limit)

    def get_prestamo_by_id(self, prestamo_id: int) -> PrestamoDB:
        prestamo = self.repo.get_prestamo_by_id(prestamo_id)
        if not prestamo:
            raise PrestamoNoEncontradoException(prestamo_id)
        return prestamo

    def create_prestamo(self, payload: PrestamoCreateRequest) -> PrestamoDB:
        # 1. Validar que el socio exista y esté activo
        socio = self.socio_repo.get_socio_by_id(payload.socio_id)
        if not socio:
            raise SocioNoEncontradoException(payload.socio_id)
        if not socio.activo:
            raise SocioInactivoException(payload.socio_id)

        # 2. Validar que el socio no supere el máximo de préstamos activos (3)
        prestamos_activos = self.socio_repo.get_prestamos_by_socio(
            payload.socio_id,
            activos=True,
        )
        if len(prestamos_activos) >= MAX_PRESTAMOS_ACTIVOS:
            raise SocioLimitePrestamosException(payload.socio_id, MAX_PRESTAMOS_ACTIVOS)

        # 3. Validar que el libro exista y tenga stock disponible
        libro = self.libro_repo.get_libro_by_id(payload.libro_id)
        if not libro:
            raise LibroNoEncontradoException(payload.libro_id)
        if libro.stock <= 0:
            raise LibroSinStockException(payload.libro_id)

        # 4. Calcular fechas (plazo de 14 días) y registrar el préstamo descontando stock
        fecha_prestamo = date.today()
        fecha_vencimiento = fecha_prestamo + timedelta(days=PLAZO_PRESTAMO_DIAS)

        nuevo_prestamo = PrestamoDB(
            socio_id=payload.socio_id,
            libro_id=payload.libro_id,
            fecha_prestamo=fecha_prestamo,
            fecha_vencimiento=fecha_vencimiento,
            fecha_devolucion=None,
            multa=0.0,
        )
        return self.repo.create_prestamo(nuevo_prestamo, libro)

    def registrar_devolucion(self, prestamo_id: int) -> PrestamoDB:
        # 1. Validar que el préstamo exista y no haya sido devuelto previamente
        prestamo = self.get_prestamo_by_id(prestamo_id)
        if prestamo.fecha_devolucion is not None:
            raise PrestamoYaDevueltoException(prestamo_id)

        # 2. Obtener el libro asociado para reponer stock
        libro = self.libro_repo.get_libro_by_id(prestamo.libro_id)
        if not libro:
            raise LibroNoEncontradoException(prestamo.libro_id)

        # 3. Calcular fecha de devolución y eventual multa ($100 x día de atraso)
        fecha_devolucion = date.today()
        dias_atraso = (fecha_devolucion - prestamo.fecha_vencimiento).days
        multa = float(dias_atraso * MONTO_MULTA_POR_DIA) if dias_atraso > 0 else 0.0

        return self.repo.registrar_devolucion(
            prestamo=prestamo,
            libro=libro,
            fecha_devolucion=fecha_devolucion,
            multa=multa,
        )
