from dependencies import SessionDep


class LibroRepository:
    def __init__(self, session: SessionDep) -> None:
        self.session = session
