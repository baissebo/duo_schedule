# Generated by Django 4.2.2 on 2024-08-22 10:54

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="EmployeeWish",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("date", models.DateField(verbose_name="Дата")),
                (
                    "shift_preference",
                    models.CharField(
                        choices=[
                            ("morning", "Утро"),
                            ("day", "День"),
                            ("night", "Ночь"),
                            ("free", "Выходной"),
                        ],
                        max_length=20,
                        verbose_name="Предпочтительный тип смены",
                    ),
                ),
                (
                    "employee",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Сотрудник",
                    ),
                ),
            ],
            options={
                "unique_together": {("employee", "date", "shift_preference")},
            },
        ),
    ]
