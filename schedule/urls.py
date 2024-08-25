from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from schedule.apps import ScheduleConfig
from schedule.views import ScheduleListView

app_name = ScheduleConfig.name

urlpatterns = [
    path("schedule-list/", ScheduleListView.as_view(), name="schedule-list"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
