from datetime import datetime

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)

from schedule.forms import EmployeeWishForm, ScheduleForm, ShiftForm
from schedule.models import Schedule, Shift, EmployeeWish
from schedule.utils import assign_employees


class ScheduleListView(LoginRequiredMixin, ListView):
    model = Schedule
    paginate_by = 1


class ScheduleDetailView(LoginRequiredMixin, DetailView):
    model = Schedule


class ScheduleCreateView(LoginRequiredMixin, CreateView):
    model = Schedule
    template_name = "schedule/schedule_form.html"
    form_class = ScheduleForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def form_valid(self, form):
        year = form.cleaned_data["year"]
        month = form.cleaned_data["month"]

        year = int(year)
        month = int(month)

        schedule_date = datetime(year, month, 1).date()

        schedule = form.save(commit=False)
        schedule.date = schedule_date
        schedule.save()

        return redirect(reverse_lazy("schedule:schedule-list"))


class ShiftListView(LoginRequiredMixin, ListView):
    model = Shift
    paginate_by = 31
    template_name = "shifts/shift_list.html"

    def get_queryset(self):
        queryset = super().get_queryset()

        selected_month = self.request.GET.get("month")
        selected_year = self.request.GET.get("year")

        if selected_month and selected_year:
            queryset = queryset.filter(
                date__year=int(selected_year), date__month=selected_month
            )

        sort_by = self.request.GET.get("sort_by", "-date")
        return queryset.order_by(sort_by)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = ScheduleForm()
        return context


class ShiftDetailView(LoginRequiredMixin, DetailView):
    model = Shift
    template_name = "shifts/shift_detail.html"


class ShiftCreateView(LoginRequiredMixin, CreateView):
    model = Shift
    template_name = "shifts/shift_form.html"
    form_class = ShiftForm
    success_url = reverse_lazy("schedule:shift-list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        schedules = Schedule.objects.all()

        month_names = ScheduleForm.base_fields["month"].choices

        context["schedules"] = [
            {
                "id": schedule.id,
                "display": f"{schedule.date.year} - {dict(month_names)[schedule.date.month]}",
            }
            for schedule in schedules
        ]

        return context

    def form_valid(self, form):
        shift = form.save(commit=False)
        schedule_id = self.request.POST.get("schedule")
        shift.schedule = Schedule.objects.get(id=schedule_id)
        shift.save()

        return redirect(self.success_url)


class ShiftUpdateView(LoginRequiredMixin, UpdateView):
    model = Shift
    form_class = ShiftForm
    template_name = "shifts/shift_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        schedules = Schedule.objects.all()
        month_names = ScheduleForm.base_fields["month"].choices

        context["schedules"] = [
            {
                "id": schedule.id,
                "display": f"{schedule.date.year} - {dict(month_names)[schedule.date.month]}",
            }
            for schedule in schedules
        ]

        return context

    def form_valid(self, form):
        shift = form.save(commit=False)
        shift.schedule = form.cleaned_data.get("schedule")
        shift.save()

        return redirect("schedule:shift-detail", pk=shift.pk)


class ShiftDeleteView(LoginRequiredMixin, DeleteView):
    model = Shift
    template_name = "shifts/shift_confirm_delete.html"
    success_url = reverse_lazy("schedule:shift-list")


class EmployeeWishListView(LoginRequiredMixin, ListView):
    model = EmployeeWish
    paginate_by = 10
    template_name = "employee_wishes/wish_list.html"

    def get_queryset(self):
        queryset = super().get_queryset()

        sort_by = self.request.GET.get("sort_by", "-date")
        filters = self.request.GET.getlist("filter")

        if filters:
            queryset = queryset.filter(shift_preference__in=filters)

        return queryset.order_by(sort_by)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filters"] = self.request.GET.getlist("filter")

        return context


class EmployeeWishDetailView(LoginRequiredMixin, DetailView):
    model = EmployeeWish
    template_name = "employee_wishes/wish_detail.html"


class EmployeeWishCreateView(LoginRequiredMixin, CreateView):
    model = EmployeeWish
    form_class = EmployeeWishForm
    template_name = "employee_wishes/wish_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_success_url(self):
        return reverse_lazy("schedule:wish-detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        form.instance.employee = self.request.user
        return super().form_valid(form)


class EmployeeWishUpdateView(LoginRequiredMixin, UpdateView):
    model = EmployeeWish
    form_class = EmployeeWishForm
    template_name = "employee_wishes/wish_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_success_url(self):
        return reverse_lazy("schedule:wish-detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        form.instance.employee = self.request.user
        return super().form_valid(form)


class EmployeeWishDeleteView(LoginRequiredMixin, DeleteView):
    model = EmployeeWish
    template_name = "employee_wishes/wish_confirm_delete.html"
    success_url = reverse_lazy("schedule:wish-list")
