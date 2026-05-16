from django.db import models

import uuid

from core.apps.common.models import TimedBaseModel
from core.apps.notifications.entities.push_subscription import (
    GroupPushSubscription as GroupPushSubscriptionEntity,
    TeacherPushSubscription as TeacherPushSubscriptionEntity,
)
from core.apps.schedule.models.group import Group
from core.apps.schedule.models.teacher import Teacher


class GroupPushSubscription(TimedBaseModel):
    external_id = models.UUIDField(
        verbose_name='Per-device external identifier',
        default=uuid.uuid4,
        editable=False,
        unique=True,
    )
    player_id = models.CharField(
        verbose_name='OneSignal player ID',
        max_length=100,
    )
    group = models.ForeignKey(
        Group,
        verbose_name='Subscribed group',
        on_delete=models.CASCADE,
        related_name='push_subscriptions',
    )
    is_active = models.BooleanField(
        verbose_name='Is subscription active',
        default=True,
    )
    last_seen_at = models.DateTimeField(
        verbose_name='Last time the device was seen',
        null=True,
        blank=True,
    )

    def to_entity(self) -> GroupPushSubscriptionEntity:
        return GroupPushSubscriptionEntity(
            id=self.id,
            external_id=str(self.external_id),
            player_id=self.player_id,
            group=self.group.to_entity(),
            is_active=self.is_active,
            last_seen_at=self.last_seen_at,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    def __str__(self) -> str:
        return f'{self.group} ← {self.external_id}'

    class Meta:
        verbose_name = 'Group Push Subscription'
        verbose_name_plural = 'Group Push Subscriptions'
        constraints = [
            models.UniqueConstraint(
                fields=['player_id', 'group'],
                name='unique_group_push_player',
            ),
        ]


class TeacherPushSubscription(TimedBaseModel):
    external_id = models.UUIDField(
        verbose_name='Per-device external identifier',
        default=uuid.uuid4,
        editable=False,
        unique=True,
    )
    player_id = models.CharField(
        verbose_name='OneSignal player ID',
        max_length=100,
    )
    teacher = models.ForeignKey(
        Teacher,
        verbose_name='Subscribed teacher',
        on_delete=models.CASCADE,
        related_name='push_subscriptions',
    )
    is_active = models.BooleanField(
        verbose_name='Is subscription active',
        default=True,
    )
    last_seen_at = models.DateTimeField(
        verbose_name='Last time the device was seen',
        null=True,
        blank=True,
    )

    def to_entity(self) -> TeacherPushSubscriptionEntity:
        return TeacherPushSubscriptionEntity(
            id=self.id,
            external_id=str(self.external_id),
            player_id=self.player_id,
            teacher=self.teacher.to_entity(),
            is_active=self.is_active,
            last_seen_at=self.last_seen_at,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    def __str__(self) -> str:
        return f'{self.teacher} ← {self.external_id}'

    class Meta:
        verbose_name = 'Teacher Push Subscription'
        verbose_name_plural = 'Teacher Push Subscriptions'
        constraints = [
            models.UniqueConstraint(
                fields=['player_id', 'teacher'],
                name='unique_teacher_push_player',
            ),
        ]
