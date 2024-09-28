from django.core.exceptions import ValidationError
from django.core.management import BaseCommand

from users.models import User


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("--email", type=str)
        parser.add_argument("--password", type=str)

    def handle(self, *args, **options):
        email = options["email"]
        password = options["password"]

        if not email:
            self.stderr.write(self.style.ERROR("Email не указан!"))
            return

        if not password:
            self.stderr.write(self.style.ERROR("Пароль не указан!"))
            return

        if User.objects.filter(email=email).exists():
            self.stderr.write(self.style.ERROR(f"Email '{email}' уже занят!"))
            return

        user = User.objects.create_user(email=email, password=password)
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True

        try:
            user.save()
            self.stdout.write(self.style.SUCCESS(f"Суперпользователь '{email}' создан успешно!"))
        except ValidationError as e:
            self.stderr.write(self.style.ERROR(f"Ошибка {e} при создании суперпользователя"))
            return

