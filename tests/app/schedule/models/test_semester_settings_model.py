import datetime

import pytest

from core.apps.schedule.models import SemesterSettings


@pytest.mark.django_db
def test_singleton_create_uses_defaults():
    obj = SemesterSettings.get_singleton()

    assert obj.pk == 1
    assert obj.start_date == datetime.date(2024, 9, 2)
    assert obj.is_above_line is True


@pytest.mark.django_db
def test_singleton_returns_existing_row():
    first = SemesterSettings.get_singleton()
    first.start_date = datetime.date(2026, 2, 10)
    first.is_above_line = False
    first.save()

    second = SemesterSettings.get_singleton()

    assert second.pk == first.pk
    assert second.start_date == datetime.date(2026, 2, 10)
    assert second.is_above_line is False


@pytest.mark.django_db
def test_save_forces_pk_to_one():
    obj = SemesterSettings(pk=99, start_date=datetime.date(2026, 9, 1), is_above_line=True)
    obj.save()

    assert obj.pk == 1
    assert SemesterSettings.objects.count() == 1


@pytest.mark.django_db
def test_only_one_row_ever_exists():
    SemesterSettings.get_singleton()
    second = SemesterSettings(start_date=datetime.date(2026, 2, 1), is_above_line=False)
    second.save()

    assert SemesterSettings.objects.count() == 1


@pytest.mark.django_db
def test_str_contains_start_date():
    obj = SemesterSettings.get_singleton()

    assert str(obj.start_date) in str(obj)
