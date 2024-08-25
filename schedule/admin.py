from django.contrib import admin

from schedule.models import EmployeeWish, Schedule, Shift


@admin.register(EmployeeWish)
class EmployeeWish(admin.ModelAdmin):
    list_display = ("id", "employee", "date", "shift_preference")


@admin.register(Schedule)
class Schedule(admin.ModelAdmin):
    list_display = ("year", "month")


@admin.register(Shift)
class Shift(admin.ModelAdmin):
    list_display = ("id", "schedule", "date")
