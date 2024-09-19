from django.db import models


class TimedBaseModel(models.Model):
    created_at = models.DateTimeField(
        verbose_name='Created date',
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        verbose_name='Updated date',
        auto_now=True,
    )

    class Meta:
        abstract = True


class Day(models.TextChoices):

    MONDAY = "MN", "Monday"
    TUESDAY = "TS", "Tuesday"
    WEDNESDAY = "WD", "Wednesday"
    THURSDAY = "TH", "Thursday"
    FRIDAY = "FR", "Friday"
    SATURDAY = "ST", "Saturday"
    SUNDAY = "SN", "Sunday"


class TeachersDegree(models.TextChoices):
    PROFESSOR = "professor", "Professor"
    ASSOCIATE_PROFESSOR = "associate_professor", "Associate Professor"
    SENIOR_LECTURER = "senior_lecturer", "Senior Lecturer"
    LECTURER = "lecturer", "Lecturer"
    GRADUATE_STUDENT = "graduate_student", "Graduate Student"


class LessonType(models.TextChoices):
    LECTURE = "lecture", "Lecture"
    PRACTICE = "practice", "Practice"


class Subgroup(models.TextChoices):
    A = "A", "A"
    B = "B", "B"


class OrdinaryNumber(models.IntegerChoices):
    FIRST = 1, "1"
    SECOND = 2, "2"
    THIRD = 3, "3"
    FOURTH = 4, "4"
    FIFTH = 5, "5"
    SIXTH = 6, "6"


class ClientRole(models.TextChoices):
    ADMIN = "admin", "Admin"
    MANAGER = "manager", "Manager"
    HEADMAN = "headman", "Headman"
    DEFAULT = "default", "Default"


class TokenType(models.TextChoices):
    ACCESS = "access", "ACCESS"
    REFRESH = "refresh", "REFRESH"

