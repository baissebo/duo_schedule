import calendar
from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404, render
from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)

from schedule.forms import EmployeeWishForm, ScheduleForm, ShiftForm, VacationForm
from schedule.models import Schedule, Shift, EmployeeWish, Vacation, ShiftAssignment
from schedule.utils import assign_employees, is_on_vacation
from users.models import User


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

        num_days = calendar.monthrange(year, month)[1]

        if month in [5, 6, 7, 8, 9]:
            morning_needed = 3
            day_needed = 5
            night_needed = 3
        else:
            morning_needed = 2
            day_needed = 3
            night_needed = 2

        for day in range(1, num_days + 1):
            shift_date = datetime(year, month, day).date()
            shift = Shift(
                schedule=schedule,
                date=shift_date,
                morning_needed=morning_needed,
                day_needed=day_needed,
                night_needed=night_needed
            )
            shift.save()

        return redirect(reverse_lazy("schedule:schedule-list"))


class ShiftListView(LoginRequiredMixin, ListView):
    model = Shift
    paginate_by = 12
    template_name = "shifts/shift_list.html"

    def get_queryset(self):
        queryset = super().get_queryset().select_related("schedule")

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

        selected_month = self.request.GET.get("month")
        selected_year = self.request.GET.get("year")
        show_vacations = self.request.GET.get("show_vacations")

        context["selected_month"] = selected_month
        context["selected_year"] = selected_year

        if selected_month and selected_year and show_vacations:
            context["vacations"] = Vacation.objects.filter(
                start_date__month=selected_month,
                start_date__year=int(selected_year)
            )
        else:
            context["vacations"] = []

        return context


class ShiftDetailView(LoginRequiredMixin, DetailView):
    model = Shift
    template_name = "shifts/shift_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        shift = self.object
        assignments = ShiftAssignment.objects.filter(shift=shift)
        context["assignments"] = assignments
        return context


class ShiftCreateView(LoginRequiredMixin, CreateView):
    model = Shift
    template_name = "shifts/shift_form.html"
    form_class = ShiftForm
    success_url = reverse_lazy("schedule:shift-list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        schedules = Schedule.objects.all()

        context["schedules"] = schedules

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

        context["schedules"] = schedules

        context["object"] = self.object

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
    paginate_by = 12
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


@login_required
def vacation_create(request):
    if request.method == "POST":
        form = VacationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("schedule:shift-list")
    else:
        form = VacationForm()

    schedules = Schedule.objects.all()
    employees = User.objects.all()

    return render(request, "vacation_form.html", {
        "form": form,
        "schedules": schedules,
        "employees": employees,
    })
