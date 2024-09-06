from django.db import models

from nullable import NULLABLE
from users.models import User

SHIFT_TYPES = (
    ("morning", "Утро"),
    ("day", "День"),
    ("night", "Ночь"),
    ("free", "Выходной"),
)


class EmployeeWish(models.Model):
    employee = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="Сотрудник"
    )
    date = models.DateField(verbose_name="Дата")
    shift_preference = models.CharField(
        max_length=20, choices=SHIFT_TYPES, verbose_name="Предпочтительный тип смены"
    )
    comment = models.TextField(max_length=155, **NULLABLE, verbose_name="Комментарий")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        unique_together = ("employee", "date", "shift_preference")
        verbose_name = "Пожелание сотрудника"
        verbose_name_plural = "Пожелания сотрудников"


class Schedule(models.Model):
    date = models.DateField(verbose_name="Дата")

    class Meta:
        verbose_name = "График работы"
        verbose_name_plural = "Графики работ"
        ordering = ["-date"]


class Shift(models.Model):
    schedule = models.ForeignKey(
        Schedule, on_delete=models.CASCADE, verbose_name="График работы"
    )
    date = models.DateField(verbose_name="Дата смены")
    morning_needed = models.PositiveIntegerField(
        default=0, verbose_name="Количество сотрудников в утро"
    )
    day_needed = models.PositiveIntegerField(
        default=0, verbose_name="Количество сотрудников в день"
    )
    night_needed = models.PositiveIntegerField(
        default=0, verbose_name="Количество сотрудников в ночь"
    )
    assigned_employees = models.ManyToManyField(
        User, verbose_name="Назначенные сотрудники", blank=True
    )

    def __str__(self):
        return f"Смена на {self.date} (Утро: {self.morning_needed}, День: {self.day_needed}, Ночь: {self.night_needed})"

    class Meta:
        verbose_name = "Смена"
        verbose_name_plural = "Смены"
        ordering = ["-date"]
