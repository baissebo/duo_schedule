from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from schedule.forms import EmployeeWishForm
from schedule.models import Schedule, Shift, EmployeeWish


class ScheduleListView(LoginRequiredMixin, ListView):
    model = Schedule
    paginate_by = 12


class ScheduleDetailView(LoginRequiredMixin, DetailView):
    model = Schedule


class ShiftListView(LoginRequiredMixin, ListView):
    model = Shift
    paginate_by = 12


class ShiftDetailView(LoginRequiredMixin, DetailView):
    model = Shift


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
