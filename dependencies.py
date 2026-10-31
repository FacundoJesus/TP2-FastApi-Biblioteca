from typing import Annotated
from fastapi import Depends

# Autores
from services.autor_service import AutorService
AutorServiceDep = Annotated[AutorService, Depends(AutorService)]

from repositories.autor_repository import AutorRepository
AutorRepositoryDep = Annotated[AutorRepository, Depends(AutorRepository)]

# Libros
from services.libro_service import LibroService
LibroServiceDep = Annotated[LibroService, Depends(LibroService)]

from repositories.libro_repository import LibroRepository
LibroRepositoryDep = Annotated[LibroRepository, Depends(LibroRepository)]


# Socios
from services.socio_service import SocioService
SocioServiceDep = Annotated[SocioService, Depends(SocioService)]

from repositories.socio_repository import SocioRepository
SocioRepositoryDep = Annotated[SocioRepository, Depends(SocioRepository)]