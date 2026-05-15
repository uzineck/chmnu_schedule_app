from abc import (
    ABC,
    abstractmethod,
)

from core.apps.schedule.entities.semester_settings import SemesterSettings as SemesterSettingsEntity
from core.apps.schedule.models import SemesterSettings as SemesterSettingsModel


class BaseSemesterSettingsService(ABC):
    @abstractmethod
    def get_current_settings(self) -> SemesterSettingsEntity:
        ...


class ORMSemesterSettingsService(BaseSemesterSettingsService):
    def get_current_settings(self) -> SemesterSettingsEntity:
        obj = SemesterSettingsModel.get_singleton()
        return SemesterSettingsEntity(
            start_date=obj.start_date,
            is_above_line=obj.is_above_line,
        )
