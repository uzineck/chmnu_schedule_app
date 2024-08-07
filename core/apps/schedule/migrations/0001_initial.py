# Generated by Django 5.0.4 on 2024-07-25 13:41

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('clients', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Lesson',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created date')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated date')),
                ('type', models.CharField(choices=[('lecture', 'Lecture'), ('practice', 'Practice')], max_length=10, verbose_name='Type of the lesson')),
                ('subgroup', models.CharField(choices=[('A', 'A'), ('B', 'B')], max_length=1, null=True)),
            ],
            options={
                'verbose_name': 'Lesson',
                'verbose_name_plural': 'Lessons',
            },
        ),
        migrations.CreateModel(
            name='Room',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created date')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated date')),
                ('number', models.CharField(max_length=20, unique=True, verbose_name='Number of the room')),
                ('description', models.CharField(blank=True, max_length=300, null=True, verbose_name='Description of the room')),
            ],
            options={
                'verbose_name': 'Room',
                'verbose_name_plural': 'Rooms',
            },
        ),
        migrations.CreateModel(
            name='Subject',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created date')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated date')),
                ('title', models.CharField(max_length=150, unique=True, verbose_name="Subject's title")),
                ('slug', models.SlugField(max_length=150, verbose_name="Subject's slug")),
            ],
            options={
                'verbose_name': 'Subject',
                'verbose_name_plural': 'Subjects',
            },
        ),
        migrations.CreateModel(
            name='Timeslot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created date')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated date')),
                ('day', models.CharField(choices=[('MN', 'Monday'), ('TS', 'Tuesday'), ('WD', 'Wednesday'), ('TH', 'Thursday'), ('FR', 'Friday'), ('ST', 'Saturday'), ('SN', 'Sunday')], max_length=2, verbose_name='The day of the week for the lesson')),
                ('ord_number', models.PositiveSmallIntegerField(choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5'), (6, '6')], verbose_name='Ordinary number of the lesson')),
                ('is_even', models.BooleanField(default=True, verbose_name='Is this lesson taken during even weeks')),
            ],
            options={
                'verbose_name': 'Timeslot',
                'verbose_name_plural': 'Timeslots',
            },
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created date')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated date')),
                ('number', models.CharField(max_length=10, primary_key=True, serialize=False, unique=True, verbose_name='Group Number')),
                ('has_subgroups', models.BooleanField(default=True, verbose_name='Does group has subgroups')),
                ('headman', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='group_headman', to='clients.client', verbose_name='Headman of the group')),
                ('lessons', models.ManyToManyField(blank=True, related_name='group_lessons', to='schedule.lesson', verbose_name='Group lessons')),
            ],
            options={
                'verbose_name': 'Group',
                'verbose_name_plural': 'Groups',
            },
        ),
        migrations.AddField(
            model_name='lesson',
            name='room',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='lesson_room', to='schedule.room', verbose_name='Room where the lesson is held'),
        ),
        migrations.AddField(
            model_name='lesson',
            name='subject',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='lesson_subject', to='schedule.subject', verbose_name='Subject of the lesson'),
        ),
        migrations.CreateModel(
            name='Teacher',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created date')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated date')),
                ('first_name', models.CharField(max_length=100, verbose_name="Teacher's First Name")),
                ('last_name', models.CharField(max_length=100, verbose_name="Teacher's Last name")),
                ('middle_name', models.CharField(max_length=100, verbose_name="Teacher's Middle Name")),
                ('rank', models.CharField(choices=[('professor', 'Professor'), ('associate_professor', 'Associate Professor'), ('senior_lecturer', 'Senior Lecturer'), ('lecturer', 'Lecturer'), ('graduate_student', 'Graduate Student')], verbose_name="Teacher's rank")),
                ('is_active', models.BooleanField(default=True, verbose_name='Is teacher still teaching')),
                ('subjects', models.ManyToManyField(blank=True, related_name='teacher_subjects', to='schedule.subject')),
            ],
            options={
                'verbose_name': 'Teacher',
                'verbose_name_plural': 'Teachers',
            },
        ),
        migrations.AddField(
            model_name='lesson',
            name='teacher',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='lesson_teacher', to='schedule.teacher', verbose_name='Teacher that holds the lesson'),
        ),
        migrations.AddField(
            model_name='lesson',
            name='timeslot',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='lesson_timeslot', to='schedule.timeslot', verbose_name='Timeslot when the lesson is held'),
        ),
    ]
