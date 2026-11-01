from datetime import date

from sqlmodel import Field, SQLModel

from api.payload.libro_dto import LibroResumenResponse


class PrestamoCreateRequest(SQLModel):
    socio_id: int = Field(gt=0)
    libro_id: int = Field(gt=0)


class PrestamoResponse(SQLModel):
    id: int
    socio_id: int
    libro_id: int
    fecha_prestamo: date
    fecha_vencimiento: date
    fecha_devolucion: date | None = None
    multa: float
    libro: LibroResumenResponse | None = None
