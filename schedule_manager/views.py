from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import ShiftSerializer
from .models import Shift, EmployeeSchedule


class EmployeeScheduleView(APIView):
    serializer = ShiftSerializer

    def get(self, request):

        month = request.query_params.get("month")
        if not month:
            return Response(
                {"Bad Request": "month parameter not found in request"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        year = request.query_params.get("year")
        if not year:
            return Response(
                {"Bad Request": "year parameter not found in request"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        token = request.auth
        user_id = token["user_id"]

        schedule = EmployeeSchedule.objects.get(user=user_id, month=month, year=year)

        if not schedule:
            return Response(
                {"Not Found": "Schedule for given parameters was not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        shifts = Shift.objects.filter(schedule=schedule)
        data = [ShiftSerializer(shift).data for shift in shifts]

        return Response(data, status=status.HTTP_200_OK)
