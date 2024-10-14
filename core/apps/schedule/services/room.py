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
    RoomDeleteException,
    RoomNotFoundException,
    RoomUpdateException,
)
from core.apps.schedule.models import Room as RoomModel


class BaseRoomService(ABC):
    @abstractmethod
    def create(self, number: str) -> RoomEntity:
        ...

    @abstractmethod
    def get_all_rooms(self) -> Iterable[RoomEntity]:
        ...

    @abstractmethod
    def get_room_list(self, filters: SearchFiltersEntity, pagination: PaginationIn) -> Iterable[RoomEntity]:
        ...

    @abstractmethod
    def get_room_count(self, filters: SearchFiltersEntity) -> int:
        ...

    @abstractmethod
    def get_by_uuid(self, room_uuid: str) -> RoomEntity:
        ...

    @abstractmethod
    def get_by_id(self, room_id: int) -> RoomEntity:
        ...

    @abstractmethod
    def check_room_number_exists(self, room_number: str) -> bool:
        ...

    @abstractmethod
    def update_number(self, room_id: int, number: str) -> None:
        ...

    @abstractmethod
    def update_description(self, room_id: int, description: str) -> None:
        ...

    @abstractmethod
    def delete_room(self, room_id: int) -> None:
        ...


class ORMRoomService(BaseRoomService):
    def _build_room_query(self, filters: SearchFiltersEntity) -> Q:
        query = Q()

        if filters.search is not None:
            query &= Q(number__icontains=filters.search) | Q(
                description__icontains=filters.search,
            )

        return query

    def create(self, number: str) -> RoomEntity:
        try:
            room = RoomModel.objects.create(number=number)
        except IntegrityError:
            raise RoomAlreadyExistException(number=number)
        return room.to_entity()

    def get_all_rooms(self) -> Iterable[RoomEntity]:
        rooms = RoomModel.objects.all()

        for room in rooms:
            yield room.to_entity()

    def get_room_list(self, filters: SearchFiltersEntity, pagination: PaginationIn) -> list[RoomEntity]:
        query = self._build_room_query(filters)
        qs = RoomModel.objects.filter(query)[pagination.offset:pagination.offset + pagination.limit]
        return [room.to_entity() for room in qs]

    def get_room_count(self, filters: SearchFiltersEntity) -> int:
        query = self._build_room_query(filters)

        return RoomModel.objects.filter(query).count()

    def get_by_uuid(self, room_uuid: str) -> RoomEntity:
        try:
            room = RoomModel.objects.get(room_uuid=room_uuid)
        except RoomModel.DoesNotExist:
            raise RoomNotFoundException(uuid=room_uuid)

        return room.to_entity()

    def get_by_id(self, room_id: int) -> RoomEntity:
        try:
            room = RoomModel.objects.get(id=room_id)
        except RoomModel.DoesNotExist:
            raise RoomNotFoundException(id=room_id)

        return room.to_entity()

    def check_room_number_exists(self, room_number: str) -> bool:
        return RoomModel.objects.filter(number=room_number).exists()

    def update_number(
        self,
        room_id: int,
        number: str,
    ) -> None:
        is_updated = RoomModel.objects.filter(id=room_id).update(number=number)

        if not is_updated:
            raise RoomUpdateException(id=room_id)

    def update_description(self, room_id: int, description: str) -> None:
        is_updated = RoomModel.objects.filter(id=room_id).update(description=description)

        if not is_updated:
            raise RoomUpdateException(id=room_id)

    def delete_room(self, room_id: int) -> None:
        is_deleted = RoomModel.objects.filter(id=room_id).delete()

        if not is_deleted:
            raise RoomDeleteException(id=room_id)
