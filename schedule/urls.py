from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from schedule.apps import ScheduleConfig
from schedule.views import (
    ScheduleListView,
    ScheduleDetailView,
    ScheduleCreateView,
    EmployeeWishCreateView,
    EmployeeWishListView,
    EmployeeWishDetailView,
    EmployeeWishUpdateView,
    EmployeeWishDeleteView,
    ShiftCreateView,
    ShiftListView,
    ShiftDetailView,
    ShiftUpdateView,
    ShiftDeleteView,
    vacation_create,
)

app_name = ScheduleConfig.name

urlpatterns = [
    path("vacation-create/", vacation_create, name="vacation-create"),

    path("schedule-list/", ScheduleListView.as_view(), name="schedule-list"),
    path("schedule/<int:pk>/", ScheduleDetailView.as_view(), name="schedule-detail"),
    path("schedule-create/", ScheduleCreateView.as_view(), name="schedule-create"),

    path("shift-list/", ShiftListView.as_view(), name="shift-list"),
    path("shift/<int:pk>/", ShiftDetailView.as_view(), name="shift-detail"),
    path("shift-create/", ShiftCreateView.as_view(), name="shift-create"),
    path("shift/<int:pk>/update", ShiftUpdateView.as_view(), name="shift-update"),
    path("shift/<int:pk>/delete", ShiftDeleteView.as_view(), name="shift-delete"),

    path("wish-list/", EmployeeWishListView.as_view(), name="wish-list"),
    path("wish/<int:pk>/", EmployeeWishDetailView.as_view(), name="wish-detail"),
    path("wish-create/", EmployeeWishCreateView.as_view(), name="wish-create"),
    path("wish/<int:pk>/update", EmployeeWishUpdateView.as_view(), name="wish-update"),
    path("wish/<int:pk>/delete", EmployeeWishDeleteView.as_view(), name="wish-delete"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
