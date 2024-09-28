from django.contrib.auth.models import AbstractUser
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

from email_user_manager import EmailUserManager
from nullable import NULLABLE


class User(AbstractUser):
    username = None

    email = models.EmailField(unique=True)
    phone = PhoneNumberField(
        verbose_name="Номер телефона", **NULLABLE, help_text="Введите номер телефона"
    )
    job_title = models.CharField(
        max_length=50,
        verbose_name="Должность",
        **NULLABLE,
        help_text="Введите вашу должность",
    )
    avatar = models.ImageField(
        upload_to="users_avatars/",
        verbose_name="Аватар",
        **NULLABLE,
        help_text="Загрузите изображение",
    )
    token = models.CharField(max_length=100, verbose_name="Token", **NULLABLE)

    objects = EmailUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return f"{self.get_full_name()}, {self.email}"
