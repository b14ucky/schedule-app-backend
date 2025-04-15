from rest_framework import serializers
from .models import EmployeeSchedule, Shift


class ShiftSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shift
        fields = (
            "date",
            "time_start",
            "time_end",
            "day_type",
            "additional_info",
        )


class EmployeeScheduleSerializer(serializers.ModelSerializer):
    shifts = ShiftSerializer(many=True)

    class Meta:
        model = EmployeeSchedule
        fields = ("month", "year", "shifts")

    def create(self, validated_data):
        shifts_data = validated_data.pop("shifts")
        user = self.context["user"]

        schedule = EmployeeSchedule.objects.get_or_create(user=user, **validated_data)[0]

        for shift in shifts_data:
            Shift.objects.get_or_create(schedule=schedule, **shift)

        return schedule
