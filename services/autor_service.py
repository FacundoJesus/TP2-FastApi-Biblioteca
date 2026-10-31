from collections.abc import Sequence
from abc import ABC, abstractmethod
from dependencies import AutorRepositoryDep
from models import AutorDB

class AutorServiceInterface(ABC):
    @abstractmethod
    def get_autores(self, offset: int, limit: int) -> Sequence[AutorDB]:
        ...


class AutorService(AutorServiceInterface):
    def __init__(self, repo: AutorRepositoryDep) -> None:
        self.repo = repo

    def get_autores(self, offset: int = 0, limit: int = 50) -> Sequence[AutorDB]:
        return self.repo.get_autores(offset, limit)
