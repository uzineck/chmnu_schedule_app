from dataclasses import dataclass


@dataclass(eq=False)
class ServiceException(Exception):
    @property
    def message(self):
        return 'Application exception occurred'


@dataclass(eq=False)
class JWTKeyParsingException(ServiceException):

    @property
    def message(self):
        return 'Invalid JWT Key Error'


@dataclass(eq=False)
class InvalidTokenTypeException(ServiceException):

    @property
    def message(self):
        return 'Invalid token type'

