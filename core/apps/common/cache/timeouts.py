from django.db import models


class Timeout(models.IntegerChoices):
    MINUTE = 60
    HALF_MINUTE = MINUTE // 2
    FIVE_MINUTES = MINUTE * 5
    TEN_MINUTES = MINUTE * 10
    HALF_HOUR = MINUTE * 30
    HOUR = MINUTE * 60
    HALF_DAY = HOUR * 12
    DAY = HOUR * 24
    HALF_WEEK = DAY * 3
    WEEK = DAY * 7
    HALF_MONTH = DAY * 15
    MONTH = DAY * 30
