from django import forms
from django.forms import DateInput

from schedule.models import Schedule, Shift, EmployeeWish


class EmployeeWishForm(forms.ModelForm):
    class Meta:
        model = EmployeeWish
        fields = ["date", "shift_preference", "comment"]
        widgets = {
            "date": DateInput(attrs={"type": "date"})
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get("date")
        shift_preference = cleaned_data.get("shift_preference")

        if date and shift_preference and self.user:
            if EmployeeWish.objects.filter(employee=self.user, date=date, shift_preference=shift_preference).exists():
                raise forms.ValidationError("Так не пойдет! У тебя уже есть пожелание на эту дату и с этим типом смены")

        return cleaned_data
