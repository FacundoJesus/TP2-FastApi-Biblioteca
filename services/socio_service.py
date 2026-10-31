from dependencies import SocioRepositoryDep


class SocioService:
    def __init__(self, repo: SocioRepositoryDep) -> None:
        self.repo = repo
