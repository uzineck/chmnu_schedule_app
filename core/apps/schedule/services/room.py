from django.db import IntegrityError
from django.db.models import Q

from abc import (
    ABC,
    abstractmethod,
)
from typing import Iterable

from core.api.filters import PaginationIn
from core.apps.common.filters import SearchFilter as SearchFiltersEntity
from core.apps.schedule.entities.room import Room as RoomEntity
from core.apps.schedule.exceptions.room import (
    RoomAlreadyExistException,
    RoomNumberNotFoundException,
    RoomUuidNotFoundException,
)
from core.apps.schedule.models import Room as RoomModel


class BaseRoomService(ABC):
    @abstractmethod
    def get_or_create(self, number: str) -> RoomEntity:
        ...

    @abstractmethod
    def get_room_list(self, filters: SearchFiltersEntity, pagination: PaginationIn) -> Iterable[RoomEntity]:
        ...

    @abstractmethod
    def get_room_count(self, filters: SearchFiltersEntity) -> int:
        ...

    @abstractmethod
    def get_room_by_number(self, number: str) -> RoomEntity:
        ...

    @abstractmethod
    def get_room_by_uuid(self, room_uuid: str) -> RoomEntity:
        ...

    @abstractmethod
    def update_room_number(self, room_uuid: str, new_number: str) -> RoomEntity:
        ...

    @abstractmethod
    def update_room_description(self, room_uuid: str, description: str) -> RoomEntity:
        ...

    @abstractmethod
    def delete_room_by_number(self, number: str) -> None:
        ...

    @abstractmethod
    def delete_room_by_uuid(self, room_uuid: str) -> None:
        ...


class ORMRoomService(BaseRoomService):
    def _build_room_query(self, filters: SearchFiltersEntity) -> Q:
        query = Q()

        if filters.search is not None:
            query &= Q(number__icontains=filters.search) | Q(
                description__icontains=filters.search,
            )

        return query

    def get_or_create(self, number: str) -> RoomEntity:
        room, _ = RoomModel.objects.get_or_create(number=number)
        return room.to_entity()

    def get_room_list(self, filters: SearchFiltersEntity, pagination: PaginationIn) -> list[RoomEntity]:
        query = self._build_room_query(filters)
        qs = RoomModel.objects.filter(query)[pagination.offset:pagination.offset + pagination.limit]
        return [room.to_entity() for room in qs]

    def get_room_count(self, filters: SearchFiltersEntity) -> int:
        query = self._build_room_query(filters)

        return RoomModel.objects.filter(query).count()

    def get_room_by_number(self, number: str) -> RoomEntity:
        try:
            room = RoomModel.objects.get(number=number)
        except RoomModel.DoesNotExist:
            raise RoomNumberNotFoundException(number=number)

        return room.to_entity()

    def get_room_by_uuid(self, room_uuid: str) -> RoomEntity:
        try:
            room = RoomModel.objects.get(room_uuid=room_uuid)
        except RoomModel.DoesNotExist:
            raise RoomUuidNotFoundException(uuid=room_uuid)

        return room.to_entity()

    def update_room_number(
        self,
        room_uuid: str,
        new_number: str,
    ) -> RoomEntity:
        try:
            RoomModel.objects.filter(room_uuid=room_uuid).update(number=new_number)
        except IntegrityError:
            raise RoomAlreadyExistException(number=new_number)
        try:
            updated_room = RoomModel.objects.get(number=new_number)
        except RoomModel.DoesNotExist:
            raise RoomNumberNotFoundException(number=new_number)
        return updated_room.to_entity()

    def update_room_description(self, room_uuid: str, description: str) -> RoomEntity:
        RoomModel.objects.filter(room_uuid=room_uuid).update(description=description)
        try:
            updated_room = RoomModel.objects.get(room_uuid=room_uuid)
        except RoomModel.DoesNotExist:
            raise RoomUuidNotFoundException(uuid=room_uuid)

        return updated_room.to_entity()

    def delete_room_by_number(self, number: str) -> None:
        try:
            room = RoomModel.objects.get(number=number)
        except RoomModel.DoesNotExist:
            raise RoomNumberNotFoundException(number=number)

        room.delete()

    def delete_room_by_uuid(self, room_uuid: str) -> None:
        try:
            room = RoomModel.objects.get(room_uuid=room_uuid)
        except RoomModel.DoesNotExist:
            raise RoomUuidNotFoundException(uuid=room_uuid)

        room.delete()
