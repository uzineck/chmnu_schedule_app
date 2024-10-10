from tests.conftest import faker


def generate_email() -> str:
    return f'{faker.user_name()}@gmail.com'


def generate_password() -> str:
    return faker.password(length=10)
