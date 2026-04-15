from app.domain.services import HelloService

class HelloUseCase:
    def __init__(self, service: HelloService):
        self.service = service

    def execute(self) -> str:
        return self.service.get_message()
