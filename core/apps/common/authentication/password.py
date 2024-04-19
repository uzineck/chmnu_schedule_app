from dataclasses import dataclass
from typing import ClassVar

import bcrypt

from abc import ABC, abstractmethod


@dataclass
class BasePasswordService(ABC):
    HASH_ENCODING: ClassVar[str]

    @abstractmethod
    def hash_password(self, plain_password: str) -> str:
        ...

    @abstractmethod
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        ...


class BcryptPasswordService(BasePasswordService):
    HASH_ENCODING: ClassVar[str] = "UTF-8"

    def hash_password(self, plain_password: str) -> str:
        hashed_password = bcrypt.hashpw(
            password=plain_password.encode(self.HASH_ENCODING),
            salt=bcrypt.gensalt()
        )
        return hashed_password.decode(self.HASH_ENCODING)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(
            password=plain_password.encode(self.HASH_ENCODING),
            hashed_password=hashed_password.encode(self.HASH_ENCODING)
        )
