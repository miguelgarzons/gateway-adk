from abc import ABC, abstractmethod
from typing import Any


class AgentClientError(Exception):
    pass


class HelpdeskAgentClient(ABC):
    @abstractmethod
    def create_session(self, app_name: str, user_id: str, session_id: str) -> None:
        pass

    @abstractmethod
    def run(
        self, app_name: str, user_id: str, session_id: str, message: str
    ) -> dict[str, Any]:
        pass
