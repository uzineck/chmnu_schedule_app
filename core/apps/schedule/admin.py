from django.contrib import admin

from core.apps.schedule.models.groups import Group
from core.apps.schedule.models.lessons import Lesson
from core.apps.schedule.models.teachers import Teacher
from core.apps.schedule.models.rooms import Room
from core.apps.schedule.models.subjects import Subject
from core.apps.schedule.models.sophomors import Sophomore
from core.apps.schedule.models.timeslots import Timeslot


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('number', 'has_subgroups', 'sophomore', 'created_at', 'updated_at',)


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('subject', 'teacher', 'type', 'room', 'timeslot', 'subgroup', 'created_at', 'updated_at',)


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'middle_name', 'rank', 'created_at', 'updated_at',)


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'created_at', 'updated_at',)


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('number', 'description', 'created_at', 'updated_at',)
    list_filter = ('number',)


@admin.register(Timeslot)
class TimeslotAdmin(admin.ModelAdmin):
    list_display = ('day', 'ord_number', 'is_even')


@admin.register(Sophomore)
class SophomoreAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'middle_name', 'token', 'created_at', 'updated_at',)
