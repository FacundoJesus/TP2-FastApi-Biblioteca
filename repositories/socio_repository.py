from collections.abc import Sequence

from sqlmodel import col, select

from dependencies import SessionDep
from models import PrestamoDB, SocioDB


class SocioRepository:
    def __init__(self, session: SessionDep) -> None:
        self.session = session

    def get_socios(self, offset: int = 0, limit: int = 50) -> Sequence[SocioDB]:
        statement = select(SocioDB).offset(offset).limit(limit)
        return self.session.exec(statement).all()

    def get_socio_by_id(self, socio_id: int) -> SocioDB | None:
        return self.session.get(SocioDB, socio_id)

    def get_socio_by_email(self, email: str) -> SocioDB | None:
        statement = select(SocioDB).where(col(SocioDB.email) == email)
        return self.session.exec(statement).first()

    def create_socio(self, socio: SocioDB) -> SocioDB:
        self.session.add(socio)
        self.session.commit()
        self.session.refresh(socio)
        return socio

    def update_socio(self, socio: SocioDB, datos: dict[str, object]) -> SocioDB:
        socio.sqlmodel_update(datos)
        self.session.add(socio)
        self.session.commit()
        self.session.refresh(socio)
        return socio

    def delete_socio(self, socio: SocioDB) -> None:
        self.session.delete(socio)
        self.session.commit()

    def get_prestamos_by_socio(
        self,
        socio_id: int,
        activos: bool | None = None,
    ) -> Sequence[PrestamoDB]:
        statement = select(PrestamoDB).where(col(PrestamoDB.socio_id) == socio_id)
        if activos is True:
            statement = statement.where(col(PrestamoDB.fecha_devolucion).is_(None))
        elif activos is False:
            statement = statement.where(col(PrestamoDB.fecha_devolucion).is_not(None))
        return self.session.exec(statement).all()
