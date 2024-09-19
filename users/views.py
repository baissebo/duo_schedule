import secrets

from django.contrib import messages
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordResetView
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy, reverse
from django.utils.html import strip_tags
from django.views.generic import (
    CreateView,
    ListView,
    UpdateView,
    DetailView,
    DeleteView,
)

from config.settings import EMAIL_HOST_USER
from users.forms import UserRegisterForm, UserUpdateForm
from users.models import User


class UserListView(LoginRequiredMixin, ListView):
    model = User

    def get_queryset(self):
        return User.objects.all()


class UserProfileView(LoginRequiredMixin, DetailView):
    model = User
    template_name = "users/user_profile.html"

    def get_object(self):
        return self.request.user


class UserCreateView(CreateView):
    model = User
    form_class = UserRegisterForm
    success_url = reverse_lazy("users:login")

    def form_valid(self, form):
        user = form.save()
        user.is_active = False
        token = secrets.token_hex(16)
        user.token = token
        user.save()
        host = self.request.get_host()
        url = f"http://{host}/users/email-confirm/{token}/"

        subject = "Подтверждение почты"
        html_message = render_to_string(
            "email_confirm.html",
            {
                "user": user,
                "url": url,
            },
        )
        plain_message = strip_tags(html_message)

        send_mail(
            subject=subject,
            message=plain_message,
            from_email=EMAIL_HOST_USER,
            recipient_list=[user.email],
            html_message=html_message,
        )
        return super().form_valid(form)


def email_verification(request, token):
    user = get_object_or_404(User, token=token)
    user.is_active = True
    user.token = ""
    user.save()
    return redirect(reverse("users:login"))


class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = "users/user_form.html"
    success_url = reverse_lazy("users:profile")

    def get_object(self):
        return self.request.user


class UserDeleteView(LoginRequiredMixin, DeleteView):
    model = User
    success_url = reverse_lazy("users:logout")
    slug_field = "email"
    slug_url_kwarg = "email"


class NewPasswordView(PasswordResetView):
    form_class = PasswordResetForm
    template_name = "users/new_password.html"
    success_url = reverse_lazy("users:login")

    def form_valid(self, form):
        email = form.cleaned_data["email"]
        try:
            user = User.objects.get(email=email)
            password = secrets.token_urlsafe(10)

            message = render_to_string("password_reset_email.html", {
                "user": user,
                "new_password": password,
            })

            send_mail(
                subject="Новый пароль для вашего аккаунта",
                message=message,
                from_email=EMAIL_HOST_USER,
                recipient_list=[user.email],
                html_message=message,
                fail_silently=False,
            )

            user.set_password(password)
            user.save()
            messages.success(self.request, "Новый пароль отправлен на электронную почту")
            return redirect(self.success_url)
        except User.DoesNotExist:
            messages.error(self.request, "Пользователь с таким email не найден")
            return super().form_invalid(form)
