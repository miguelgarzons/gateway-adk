from app.domain.ports.repository import HelloRepository

class HelloService:
    def __init__(self, repo: HelloRepository):
        self.repo = repo

    def get_message(self) -> str:
        return self.repo.get_message()
