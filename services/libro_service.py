from dependencies import LibroRepositoryDep


class LibroService:
    def __init__(self, repo: LibroRepositoryDep) -> None:
        self.repo = repo
