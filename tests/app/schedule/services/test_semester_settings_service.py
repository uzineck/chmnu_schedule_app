import datetime
import pytest

from core.apps.schedule.services.semester_settings import BaseSemesterSettingsService


@pytest.fixture
def semester_settings_service(container) -> BaseSemesterSettingsService:
    return container.resolve(BaseSemesterSettingsService)


@pytest.mark.django_db
def test_get_current_settings_returns_entity_with_defaults(
        semester_settings_service: BaseSemesterSettingsService,
):
    settings = semester_settings_service.get_current_settings()

    assert isinstance(settings.start_date, datetime.date)
    assert isinstance(settings.is_above_line, bool)
