from django.contrib import admin

from core.apps.schedule.models.group import Group
from core.apps.schedule.models.lesson import Lesson
from core.apps.schedule.models.room import Room
from core.apps.schedule.models.subject import Subject
from core.apps.schedule.models.teacher import Teacher
from core.apps.schedule.models.timeslot import Timeslot


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('number', 'has_subgroups', 'headman', 'created_at', 'updated_at')
    search_fields = ('number', 'headman__email')
    list_filter = ('has_subgroups', 'created_at', 'updated_at')


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('id', 'subject', 'teacher', 'room', 'timeslot', 'type', 'subgroup')
    list_filter = ('timeslot__day', 'timeslot__ord_number', 'timeslot__is_even', 'type')


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('id', 'last_name', 'first_name', 'middle_name', 'rank', 'created_at', 'updated_at')
    search_fields = ('last_name', 'first_name', 'middle_name')
    list_filter = ('rank', 'created_at', 'updated_at')


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'slug', 'created_at', 'updated_at')
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ('title',)
    list_filter = ('created_at', 'updated_at')


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('id', 'number', 'description', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('number', 'description')


@admin.register(Timeslot)
class TimeslotAdmin(admin.ModelAdmin):
    list_display = ('id', 'day', 'ord_number', 'is_even')
    list_filter = ('day', 'ord_number', 'is_even')
