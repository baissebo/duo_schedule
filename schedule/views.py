from datetime import datetime

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from schedule.forms import EmployeeWishForm, ScheduleForm, ShiftForm
from schedule.models import Schedule, Shift, EmployeeWish
from schedule.utils import assign_employees


class ScheduleListView(LoginRequiredMixin, ListView):
    model = Schedule
    paginate_by = 1


class ScheduleDetailView(LoginRequiredMixin, DetailView):
    model = Schedule


class ScheduleCreateView(CreateView):
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

        schedule_date = datetime(year, month, 1)

        schedule = form.save(commit=False)
        schedule.date = schedule_date
        schedule.save()

        return redirect(reverse_lazy("schedule:schedule-list"))


class ShiftListView(LoginRequiredMixin, ListView):
    model = Shift
    paginate_by = 31


class ShiftDetailView(LoginRequiredMixin, DetailView):
    model = Shift


class ShiftCreateView(LoginRequiredMixin, CreateView):
    model = Shift
    template_name = "schedule/shift_form.html"
    form_class = ShiftForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        schedule_id = self.kwargs.get("schedule_id")
        context["schedule"] = Schedule.objects.get(id=schedule_id)
        return context

    def form_valid(self, form):
        schedule = Schedule.objects.get(id=self.kwargs["schedule_id"])
        form.instance.schedule = schedule
        shift = form.save()

        wishes = EmployeeWish.objects.filter(date=shift.date).order_by("created_at")

        assign_employees(shift, wishes)

        return super().form_valid(form)

    def get_success_url(self):
        schedule_id = self.kwargs.get("schedule_id")
        return reverse_lazy("schedule:schedule-detail", kwargs={"pk": schedule_id})


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
