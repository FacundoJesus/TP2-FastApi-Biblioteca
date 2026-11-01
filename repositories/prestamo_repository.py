from collections.abc import Sequence
from datetime import date

from sqlmodel import select

from dependencies import SessionDep
from models import LibroDB, PrestamoDB


class PrestamoRepository:
    def __init__(self, session: SessionDep) -> None:
        self.session = session

    def get_prestamos(self, offset: int = 0, limit: int = 50) -> Sequence[PrestamoDB]:
        statement = select(PrestamoDB).offset(offset).limit(limit)
        return self.session.exec(statement).all()

    def get_prestamo_by_id(self, prestamo_id: int) -> PrestamoDB | None:
        return self.session.get(PrestamoDB, prestamo_id)

    def create_prestamo(self, prestamo: PrestamoDB, libro: LibroDB) -> PrestamoDB:
        libro.stock -= 1
        self.session.add(libro)
        self.session.add(prestamo)
        self.session.commit()
        self.session.refresh(prestamo)
        self.session.refresh(libro)
        return prestamo

    def registrar_devolucion(
        self,
        prestamo: PrestamoDB,
        libro: LibroDB,
        fecha_devolucion: date,
        multa: float,
    ) -> PrestamoDB:
        prestamo.fecha_devolucion = fecha_devolucion
        prestamo.multa = multa
        libro.stock += 1
        self.session.add(libro)
        self.session.add(prestamo)
        self.session.commit()
        self.session.refresh(prestamo)
        self.session.refresh(libro)
        return prestamo
