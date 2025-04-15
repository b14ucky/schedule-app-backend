from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class ShiftDayType(models.TextChoices):
    WORK = "WORK", "Praca"
    SICK_LEAVE = "SICK_LEAVE", "L4"
    VACATION = "VACATION", "Urlop"
    NON_WORKING_DAY = "NON_WORKING_DAY", "Dzień wolny (grafik)"
    AVAILABILITY_OFF = "AVAILABILITY_OFF", "Wolne (niedyspozycyjność)"
    REQUESTED_OFF = "REQUESTED_OFF", "Wolne na prośbę"


class EmployeeSchedule(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    month = models.IntegerField()
    year = models.IntegerField()

    def __str__(self):
        return f"{self.user} - {self.month}/{self.year}"


class Shift(models.Model):
    schedule = models.ForeignKey(EmployeeSchedule, on_delete=models.CASCADE)
    date = models.DateField()
    time_start = models.TimeField(null=True, blank=True)
    time_end = models.TimeField(null=True, blank=True)
    day_type = models.CharField(
        max_length=20, choices=ShiftDayType.choices, default=ShiftDayType.NON_WORKING_DAY
    )
    additional_info = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return f"{self.schedule.user} | {self.date} | {self.day_type}"
