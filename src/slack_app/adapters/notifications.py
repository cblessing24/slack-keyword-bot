from abc import ABC, abstractmethod


class AbstractNotifications(ABC):
    @abstractmethod
    def send(self, destination: str, message: str) -> None:
        pass


class SlackNotifications(AbstractNotifications):
    def send(self, destination: str, message: str) -> None:
        print(f"Sending message to {destination}: {message}")
