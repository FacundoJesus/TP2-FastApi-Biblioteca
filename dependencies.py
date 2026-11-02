# isort: skip_file
from typing import Annotated

from fastapi import Depends
from sqlmodel import Session

from repositories.database import get_session

# 1. Sesión de base de datos
SessionDep = Annotated[Session, Depends(get_session)]

# 2. Repositorios (dependen de SessionDep)
from repositories.autor_repository import AutorRepository  # noqa: E402

AutorRepositoryDep = Annotated[AutorRepository, Depends(AutorRepository)]

from repositories.libro_repository import LibroRepository  # noqa: E402

LibroRepositoryDep = Annotated[LibroRepository, Depends(LibroRepository)]

from repositories.socio_repository import SocioRepository  # noqa: E402

SocioRepositoryDep = Annotated[SocioRepository, Depends(SocioRepository)]

from repositories.prestamo_repository import PrestamoRepository  # noqa: E402

PrestamoRepositoryDep = Annotated[PrestamoRepository, Depends(PrestamoRepository)]

# 3. Servicios (dependen de *RepositoryDep)
from services.autor_service import AutorService, AutorServiceInterface  # noqa: E402

AutorServiceDep = Annotated[AutorServiceInterface, Depends(AutorService)]

from services.libro_service import LibroService, LibroServiceInterface  # noqa: E402

LibroServiceDep = Annotated[LibroServiceInterface, Depends(LibroService)]

from services.socio_service import SocioService, SocioServiceInterface  # noqa: E402

SocioServiceDep = Annotated[SocioServiceInterface, Depends(SocioService)]

from services.prestamo_service import (  # noqa: E402
    PrestamoService,
    PrestamoServiceInterface,
)

PrestamoServiceDep = Annotated[PrestamoServiceInterface, Depends(PrestamoService)]

# 4. Autorización y Roles vía Headers HTTP
from collections.abc import Callable, Sequence  # noqa: E402
from fastapi import Header, HTTPException, status  # noqa: E402

ROL_BIBLIOTECARIO = "bibliotecario"
ROL_SOCIO = "socio"
ROLES_VALIDOS = (ROL_BIBLIOTECARIO, ROL_SOCIO)


def require_bibliotecario(
    x_rol: Annotated[
        str | None,
        Header(
            alias="X-Rol",
            description="Rol del usuario solicitante: 'bibliotecario'",
            examples=["bibliotecario"],
        ),
    ] = None,
) -> str:
    if not x_rol or x_rol.lower().strip() != ROL_BIBLIOTECARIO:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operación restringida: se requiere rol 'bibliotecario'",
        )
    return x_rol.lower().strip()


RequireBibliotecarioDep = Annotated[str, Depends(require_bibliotecario)]


def get_current_role(
    x_rol: Annotated[
        str,
        Header(
            alias="X-Rol",
            description="Rol del usuario solicitante: 'socio'",
        ),
    ] = ROL_SOCIO,
) -> str:
    rol_limpio = x_rol.lower().strip()
    if rol_limpio not in ROLES_VALIDOS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Rol inválido '{x_rol}'. Valores permitidos: {', '.join(ROLES_VALIDOS)}",
        )
    return rol_limpio


RoleDep = Annotated[str, Depends(get_current_role)]
RoleSocioDep = RoleDep


def get_current_socio_id(
    x_socio_id: Annotated[
        int | None,
        Header(
            alias="X-Socio-Id",
            description="ID del socio solicitante (requerido para consultas privadas de socio)",
        ),
    ] = None,
) -> int | None:
    return x_socio_id


SocioIdDep = Annotated[int | None, Depends(get_current_socio_id)]


def require_role(roles_permitidos: Sequence[str]) -> Callable[..., str]:
    if list(roles_permitidos) == [ROL_BIBLIOTECARIO]:
        return require_bibliotecario

    def check_role(rol: RoleDep) -> str:
        if rol not in roles_permitidos:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operación restringida: se requiere uno de los siguientes roles: {', '.join(roles_permitidos)}",
            )
        return rol

    return check_role

