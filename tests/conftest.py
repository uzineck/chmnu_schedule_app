import pytest
from faker import Faker

from core.project.containers.containers import get_container


@pytest.fixture(scope="function")
def container():
    container = get_container()
    return container


# faker = Faker()
# faker_ua = Faker('uk_UA')


@pytest.fixture(scope="session")
def faker():
    return Faker()


@pytest.fixture(scope="session")
def faker_ua():
    return Faker("uk_UA")
