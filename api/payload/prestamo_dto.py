from datetime import date

from sqlmodel import SQLModel

from api.payload.libro_dto import LibroResumenResponse


class PrestamoResponse(SQLModel):
    id: int
    socio_id: int
    libro_id: int
    fecha_prestamo: date
    fecha_vencimiento: date
    fecha_devolucion: date | None = None
    multa: float
    libro: LibroResumenResponse | None = None
