import re
from datetime import datetime

from django import forms
from django.core.exceptions import ValidationError
from django.forms import DateInput

from schedule.models import Schedule, Shift, EmployeeWish, Vacation


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

        current_instance = self.instance

        if date and shift_preference and self.user:
            if EmployeeWish.objects.exclude(pk=current_instance.pk).filter(
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
                "Введи корректный год (всего лишь нужно 4 цифры подряд)"
            )

        return year

    def clean(self):
        cleaned_data = super().clean()
        year = cleaned_data.get("year")
        month = cleaned_data.get("month")

        if year is not None and month is not None:
            date_to_check = datetime(year=int(year), month=int(month), day=1)

            if Schedule.objects.filter(date=date_to_check).exists():
                raise ValidationError("Такой график уже существует!")

        return cleaned_data


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
            if schedule.date.year != date.year or schedule.date.month != date.month:
                raise ValidationError("Выбранный график не соответствует дате смены!")

            if Shift.objects.filter(schedule=schedule, date=date).exclude(id=shift_id).exists():
                raise ValidationError("Смена на эту дату для данного графика уже существует!")

        return cleaned_data


class VacationForm(forms.ModelForm):
    class Meta:
        model = Vacation
        fields = ["schedule", "employee", "start_date", "end_date"]

    def clean(self):
        cleaned_data = super().clean()
        schedule = cleaned_data.get("schedule")
        employee = cleaned_data.get("employee")
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")

        if schedule and employee and start_date and end_date:
            if schedule.date.year != start_date.year or schedule.date.month != start_date.month:
                raise ValidationError("Выбранный график не соответствует дате начала отпуска!")

            if Vacation.objects.filter(schedule=schedule, employee=employee, start_date__lte=end_date,
                                       end_date__gte=start_date).exists():
                raise ValidationError("Сотрудник уже имеет отпуск в этот период!")

            if start_date > end_date:
                raise ValidationError("Дата начала отпуска не может быть позже даты окончания!")

        return cleaned_data
