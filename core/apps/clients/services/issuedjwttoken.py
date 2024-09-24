from abc import (
    ABC,
    abstractmethod,
)
from typing import Any

from core.apps.clients.entities.client import Client as ClientEntity
from core.apps.clients.exceptions.issuedjwttoken import ClientTokensRevokedException
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
    def bulk_create(
            self,
            subject: ClientEntity,
            raw_tokens: list[dict[str, Any]],
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
        IssuedJwtTokenModel.objects.create(
            subject_id=subject.id,
            jti=jti,
            device_id=device_id,
            expiration_time=expiration_time,
        )

    def bulk_create(self, subject: ClientEntity, raw_tokens: list[dict[str, Any]]) -> None:
        IssuedJwtTokenModel.objects.bulk_create(
            [
                IssuedJwtTokenModel(
                    subject_id=subject.id,
                    jti=token_payload.get('jti'),
                    device_id=token_payload.get('device_id'),
                    expiration_time=token_payload.get('exp'),
                )
                for token_payload in raw_tokens
            ],
        )

    def check_revoked(self, jti: str) -> bool:
        return IssuedJwtTokenModel.objects.filter(jti=jti, revoked=True).exists()

    def revoke_client_tokens(self, subject: ClientEntity) -> None:
        IssuedJwtTokenModel.objects.filter(subject_id=subject.id).update(revoked=True)
        raise ClientTokensRevokedException(client_email=subject.email)

    def revoke_client_device_tokens(self, subject: ClientEntity, device_id: str) -> None:
        IssuedJwtTokenModel.objects.filter(subject_id=subject.id, device_id=device_id).update(revoked=True)
