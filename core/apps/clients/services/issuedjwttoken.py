from django.db import IntegrityError

from abc import (
    ABC,
    abstractmethod,
)

from core.apps.clients.entities.client import Client as ClientEntity
from core.apps.clients.exceptions.issuedjwttoken import (
    ClientTokensRevokedException,
    TokenJTIAlreadyExistsException,
)
from core.apps.clients.models import IssuedJwtToken as IssuedJwtTokenModel


class BaseIssuedJwtTokenService(ABC):
    @abstractmethod
    def create(
            self,
            subject: ClientEntity,
            jti: str,
            device_id: str,
            expiration_time: int,
    ) -> None:
        ...

    @abstractmethod
    def check_revoked(self, jti: str) -> bool:
        ...

    @abstractmethod
    def revoke_client_tokens(self, subject: ClientEntity) -> None:
        ...

    @abstractmethod
    def revoke_client_device_tokens(self, subject: ClientEntity, device_id: str) -> None:
        ...


class ORMIssuedJwtTokenService(BaseIssuedJwtTokenService):
    def create(self, subject: ClientEntity, jti: str, device_id: str, expiration_time: int) -> None:
        try:
            IssuedJwtTokenModel.objects.create(
                subject_id=subject.id,
                jti=jti,
                device_id=device_id,
                expiration_time=expiration_time,
            )
        except IntegrityError:
            raise TokenJTIAlreadyExistsException(jti=jti)

    def check_revoked(self, jti: str) -> bool:
        return IssuedJwtTokenModel.objects.filter(jti=jti, revoked=True).exists()

    def revoke_client_tokens(self, subject: ClientEntity) -> None:
        IssuedJwtTokenModel.objects.filter(subject_id=subject.id).update(revoked=True)
        raise ClientTokensRevokedException(client_email=subject.email)

    def revoke_client_device_tokens(self, subject: ClientEntity, device_id: str) -> None:
        IssuedJwtTokenModel.objects.filter(subject_id=subject.id, device_id=device_id).update(revoked=True)
