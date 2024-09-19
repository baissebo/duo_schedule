from django import forms
from django.contrib.auth.forms import UserCreationForm

from users.models import User


class UserRegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("email", "first_name", "last_name", "password1", "password2", "phone", "job_title", "avatar")

    def clean_first_name(self):
        first_name = self.cleaned_data["first_name"]
        if len(first_name) < 2:
            raise forms.ValidationError("Имя должно содержать не менее 2-х символов")
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data["last_name"]
        if not last_name:
            raise forms.ValidationError("Поле 'Фамилия' не должно быть пустым")
        return last_name

    def clean_email(self):
        email = self.cleaned_data["email"]
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Этот email уже занят! Попробуй использовать другой.")
        return email


class UserUpdateForm(UserRegisterForm):
    email = None
    password1 = None
    password2 = None

    class Meta(UserRegisterForm.Meta):
        fields = ("first_name", "last_name", "phone", "job_title", "avatar")
