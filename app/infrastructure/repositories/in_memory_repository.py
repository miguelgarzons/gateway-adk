from app.domain.ports.repository import HelloRepository

class InMemoryHelloRepository(HelloRepository):
    def get_message(self) -> str:
        return "Hola Mundo desde Hexagonal con DI"
