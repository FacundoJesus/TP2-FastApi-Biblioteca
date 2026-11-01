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

# 3. Servicios (dependen de *RepositoryDep)
from services.autor_service import AutorService, AutorServiceInterface  # noqa: E402

AutorServiceDep = Annotated[AutorServiceInterface, Depends(AutorService)]

from services.libro_service import LibroService, LibroServiceInterface  # noqa: E402

LibroServiceDep = Annotated[LibroServiceInterface, Depends(LibroService)]

from services.socio_service import SocioService, SocioServiceInterface  # noqa: E402

SocioServiceDep = Annotated[SocioServiceInterface, Depends(SocioService)]
