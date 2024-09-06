from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from schedule.apps import ScheduleConfig
from schedule.views import (ScheduleListView, ScheduleDetailView, ScheduleCreateView, EmployeeWishCreateView,
                            EmployeeWishListView, EmployeeWishDetailView, EmployeeWishUpdateView,
                            EmployeeWishDeleteView, ShiftCreateView)

app_name = ScheduleConfig.name

urlpatterns = [
    path("schedule-list/", ScheduleListView.as_view(), name="schedule-list"),
    path("schedule-create/", ScheduleCreateView.as_view(), name="schedule-create"),

    path("shift-create/", ShiftCreateView.as_view(), name="shift-create"),

    path("wish-list/", EmployeeWishListView.as_view(), name="wish-list"),
    path("wish/<int:pk>/", EmployeeWishDetailView.as_view(), name="wish-detail"),
    path("wish-create/", EmployeeWishCreateView.as_view(), name="wish-create"),
    path("wish/<int:pk>/update", EmployeeWishUpdateView.as_view(), name="wish-update"),
    path("wish/<int:pk>/delete", EmployeeWishDeleteView.as_view(), name="wish-delete"),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
