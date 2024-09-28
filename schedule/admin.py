from django.contrib import admin

from schedule.models import EmployeeWish, Schedule, Shift, Vacation


@admin.register(EmployeeWish)
class EmployeeWish(admin.ModelAdmin):
    list_display = ("id", "employee", "date", "shift_preference", "created_at")


@admin.register(Schedule)
class Schedule(admin.ModelAdmin):
    list_display = ("date", "is_calculated")


@admin.register(Shift)
class Shift(admin.ModelAdmin):
    list_display = ("id", "schedule", "date")


@admin.register(Vacation)
class Vacation(admin.ModelAdmin):
    list_display = ("schedule", "employee", "start_date", "end_date")
