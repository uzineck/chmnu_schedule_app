from abc import (
    ABC,
    abstractmethod,
)
from dataclasses import dataclass

from core.apps.clients.entities.sophomore import Sophomore as SophomoreEntity


class BaseSenderService(ABC):
    @abstractmethod
    def send_code(self, sophomore: SophomoreEntity, code: str) -> None:
        ...


class DummySenderService(BaseSenderService):
    def send_code(self, sophomore: SophomoreEntity, code: str) -> None:
        print(f'Code to user: {sophomore}, sent: {code}')


class EmailSenderService(BaseSenderService):
    def send_code(self, sophomore: SophomoreEntity, code: str) -> None:
        print(f'sent code {code} to user email: {sophomore.email}')
