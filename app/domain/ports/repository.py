from abc import ABC, abstractmethod

class HelloRepository(ABC):
    @abstractmethod
    def get_message(self) -> str:
        pass
