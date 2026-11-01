from pydantic import EmailStr
from sqlmodel import Field, SQLModel


class SocioResponse(SQLModel):
    id: int
    nombre: str
    email: str
    activo: bool


class SocioCreateRequest(SQLModel):
    nombre: str = Field(min_length=3, max_length=100)
    email: EmailStr
    activo: bool = Field(default=True)


class SocioUpdateRequest(SQLModel):
    nombre: str = Field(min_length=3, max_length=100)
    email: EmailStr
    activo: bool = Field(default=True)


class SocioPatchRequest(SQLModel):
    nombre: str | None = Field(default=None, min_length=3, max_length=100)
    email: EmailStr | None = Field(default=None)
    activo: bool | None = Field(default=None)
