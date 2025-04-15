from django.contrib import admin, messages
from .models import EmployeeSchedule, Shift
from django import forms
from django.urls import path, reverse
from django.shortcuts import render
from io import BytesIO
from .schedule_parser import ScheduleParser
from django.contrib.auth import get_user_model
from .serializers import EmployeeScheduleSerializer
from dataclasses import asdict
from django.http import HttpResponseRedirect


User = get_user_model()


class ScheduleUploadForm(forms.Form):
    schedule_file = forms.FileField()


class EmployeeScheduleAdmin(admin.ModelAdmin):
    list_display = ("user", "month", "year")

    def get_urls(self):
        urls = super().get_urls()
        new_urls = [path("upload-schedule/", self.upload_schedule)]

        return new_urls + urls

    def upload_schedule(self, request):

        if request.method == "POST":
            schedule_parser = ScheduleParser()
            schedule_file = request.FILES["schedule_file"]

            if not schedule_file.name.endswith(".xlsx"):
                messages.warning(request, "Wrong file type was uploaded.")
                return HttpResponseRedirect(request.path_info)

            schedule_parser.parse(BytesIO(schedule_file.read()))
            employees_success = []
            employees_fail = []

            for employee in schedule_parser.full_schedule:
                user = User.objects.get(
                    first_name=employee.first_name, last_name=employee.last_name
                )

                employee_string = f"{employee.first_name} {employee.last_name}"
                if not user:
                    employees_fail.append(employee_string)
                    continue

                serializer = EmployeeScheduleSerializer(
                    data=asdict(employee.schedule), context={"user": user}
                )
                if serializer.is_valid(raise_exception=True):
                    serializer.save()
                    employees_success.append(employee_string)

            if employees_success:
                messages.info(
                    request,
                    f"Added schedules for employees: {', '.join(employees_success)}.",
                )

            if employees_fail:
                messages.warning(
                    request,
                    f"Employees not found in database: {', '.join(employees_fail)}.",
                )

            return HttpResponseRedirect(
                reverse("admin:schedule_manager_employeeschedule_changelist")
            )

        form = ScheduleUploadForm()
        data = {"form": form}

        return render(request, "admin/schedule_upload.html", data)


class ShiftAdmin(admin.ModelAdmin):
    list_display = (
        "date",
        "time_start",
        "time_end",
        "day_type",
        "schedule",
    )


admin.site.register(EmployeeSchedule, EmployeeScheduleAdmin)
admin.site.register(Shift, ShiftAdmin)
