import re

from django import forms
from django.core.exceptions import ValidationError
from django.forms import DateInput

from schedule.models import Schedule, Shift, EmployeeWish


class EmployeeWishForm(forms.ModelForm):
    class Meta:
        model = EmployeeWish
        fields = ["date", "shift_preference", "comment"]
        widgets = {"date": DateInput(attrs={"type": "date"})}

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get("date")
        shift_preference = cleaned_data.get("shift_preference")

        if date and shift_preference and self.user:
            if EmployeeWish.objects.filter(
                    employee=self.user, date=date, shift_preference=shift_preference
            ).exists():
                raise forms.ValidationError(
                    "Так не пойдет! У тебя уже есть пожелание на эту дату и с этим типом смены"
                )

        return cleaned_data


class ScheduleForm(forms.ModelForm):
    year = forms.CharField(
        label="Год",
        max_length=4,
        widget=forms.TextInput(attrs={"placeholder": "Введите год", "type": "number"}),
    )
    month = forms.ChoiceField(
        label="Месяц",
        choices=[
            (1, "Январь"),
            (2, "Февраль"),
            (3, "Март"),
            (4, "Апрель"),
            (5, "Май"),
            (6, "Июнь"),
            (7, "Июль"),
            (8, "Август"),
            (9, "Сентябрь"),
            (10, "Октябрь"),
            (11, "Ноябрь"),
            (12, "Декабрь"),
        ],
    )

    class Meta:
        model = Schedule
        fields = ["year", "month"]

    def clean_year(self):
        year = self.cleaned_data.get("year")

        if not re.match(r"^\d{4}$", year):
            raise ValidationError(
                "Введи корректный код (всего лишь нужно 4 цифры подряд)"
            )

        return year


class ShiftForm(forms.ModelForm):
    class Meta:
        model = Shift
        fields = ["schedule", "date", "morning_needed", "day_needed", "night_needed"]

    def clean(self):
        cleaned_data = super().clean()
        schedule = cleaned_data.get("schedule")
        date = cleaned_data.get("date")

        shift_id = self.instance.id if self.instance.pk else None

        if schedule and date:
            if Shift.objects.filter(schedule=schedule, date=date).exclude(id=shift_id).exists():
                raise ValidationError("Смена на эту дату для данного графика уже существует!")

        return cleaned_data
