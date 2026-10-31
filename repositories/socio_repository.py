from dependencies import SessionDep


class SocioRepository:
    def __init__(self, session: SessionDep) -> None:
        self.session = session
