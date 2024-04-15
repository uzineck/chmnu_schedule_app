import random
from abc import (
    ABC,
    abstractmethod,
)

from django.core.cache import cache

from core.apps.clients.entities.sophomore import Sophomore as SophomoreEntity
from core.apps.clients.exceptions.codes import (
    CodeNotFoundException,
    CodesNotEqualException,
)


class BaseCodeService(ABC):
    @abstractmethod
    def generate_code(self, sophomore: SophomoreEntity) -> str:
        ...

    @abstractmethod
    def validate_code(self, code: str, sophomore: SophomoreEntity) -> None:
        ...


class DjangoCacheCodeService(BaseCodeService):
    def generate_code(self, sophomore: SophomoreEntity) -> str:
        code = str(random.randint(100000, 999999))
        cache.set(sophomore.email, code)
        return code

    def validate_code(self, code: str, sophomore: SophomoreEntity) -> None:
        cached_code = cache.get(sophomore.email)

        if cached_code is None:
            raise CodeNotFoundException(code=code)

        if cached_code != code:
            raise CodesNotEqualException(
                code=code,
                cached_code=cached_code,
                customer_phone=customer.phone,
            )

        cache.delete(sophomore.email)
