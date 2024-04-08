from django.contrib import admin

from core.apps.schedule.models.groups import Group
from core.apps.schedule.models.lessons import Lesson
from core.apps.schedule.models.teachers import Teacher
from core.apps.schedule.models.rooms import Room
from core.apps.schedule.models.subjects import Subject
from core.apps.schedule.models.timeslots import Timeslot


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('number', 'has_subgroups', 'sophomore', 'created_at', 'updated_at',)
    search_fields = ('number',)

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('subject', 'teacher', 'type', 'room', 'timeslot', 'subgroup', 'created_at', 'updated_at',)


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'middle_name', 'rank', 'created_at', 'updated_at',)
    search_fields = ('last_name', 'first_name', 'middle_name',)


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'created_at', 'updated_at',)
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ('title',)


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('number', 'description', 'created_at', 'updated_at',)
    list_filter = ('number',)
    search_fields = ('number',)


@admin.register(Timeslot)
class TimeslotAdmin(admin.ModelAdmin):
    list_display = ('day', 'ord_number', 'is_even')



