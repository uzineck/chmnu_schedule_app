from django.contrib import admin

from core.apps.schedule.models import GroupLessons
from core.apps.schedule.models.group import Group
from core.apps.schedule.models.lesson import Lesson
from core.apps.schedule.models.room import Room
from core.apps.schedule.models.subject import Subject
from core.apps.schedule.models.teacher import Teacher
from core.apps.schedule.models.timeslot import Timeslot


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('group_uuid', 'number', 'has_subgroups', 'headman', 'created_at', 'updated_at')
    list_display_links = ('group_uuid',)
    search_fields = ('group_uuid', 'number', 'headman__email')
    list_filter = ('has_subgroups', 'created_at', 'updated_at')


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('lesson_uuid', 'subject', 'teacher', 'room', 'timeslot', 'type')
    list_display_links = ('lesson_uuid',)
    search_fields = ('lesson_uuid',)
    list_filter = ('timeslot__day', 'timeslot__ord_number', 'timeslot__is_even', 'type')


@admin.register(GroupLessons)
class GroupLessonsAdmin(admin.ModelAdmin):
    list_display = ('id', 'group', 'subgroup', 'lesson')
    search_fields = ('group__number', 'group__group_uuid', 'lesson__lesson_uuid')


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('teacher_uuid', 'last_name', 'first_name', 'middle_name', 'rank', 'created_at', 'updated_at')
    list_display_links = ('teacher_uuid',)
    search_fields = ('teacher_uuid', 'last_name', 'first_name', 'middle_name')
    list_filter = ('rank', 'created_at', 'updated_at')


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('subject_uuid', 'title', 'slug', 'created_at', 'updated_at')
    list_display_links = ('subject_uuid',)
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ('subject_uuid', 'title', 'slug')
    list_filter = ('created_at', 'updated_at')


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('room_uuid', 'number', 'created_at', 'updated_at')
    list_display_links = ('room_uuid',)
    list_filter = ('created_at', 'updated_at')
    search_fields = ('room_uuid', 'number', 'description')


@admin.register(Timeslot)
class TimeslotAdmin(admin.ModelAdmin):
    list_display = ('id', 'day', 'ord_number', 'is_even')
    list_filter = ('day', 'ord_number', 'is_even')
