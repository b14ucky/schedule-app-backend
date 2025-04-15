from django.urls import path
from .views import EmployeeScheduleView

urlpatterns = [
    path("schedule/", EmployeeScheduleView.as_view(), name="employee_schedule"),
]
