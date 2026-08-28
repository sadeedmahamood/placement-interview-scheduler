from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework import status

from .models import (
    Student,
    Company,
    Application,
    Shortlist,
    Interview,
    Room,
    Panel,
)
from .serializers import (
    StudentSerializer,
    CompanySerializer,
    ApplicationSerializer,
    ShortlistSerializer,
    InterviewSerializer,
    RoomSerializer,
    PanelSerializer,
)
from .services.replanner import Replanner


# STUDENT
class StudentListApiView(APIView):
    def get(self, request):
        students = Student.objects.all()
        serializer = StudentSerializer(students, many=True)
        return Response(serializer.data)


# COMPANY
class CompanyListApiView(APIView):
    def get(self, request):
        companies = Company.objects.all()
        serializer = CompanySerializer(companies, many=True)
        return Response(serializer.data)


# APPLICATIONS
class ApplicationListApiView(APIView):
    def get(self, request):
        applications = Application.objects.all()
        serializer = ApplicationSerializer(applications, many=True)
        return Response(serializer.data)


# SHORTLIST
class ShortlistListApiView(APIView):
    def get(self, request):
        shortlists = Shortlist.objects.all()
        serializer = ShortlistSerializer(shortlists, many=True)
        return Response(serializer.data)


# PAGINATION
class InterviewPagination(PageNumberPagination):
    page_size = 25
    page_size_query_param = "page_size"
    max_page_size = 100


# INTERVIEW
class InterviewListApiView(APIView):
    def get(self, request):
        interviews = Interview.objects.all().order_by(
            "day",
            "start_time",
            "room__room_id",
        )

        student = request.query_params.get("student")
        company = request.query_params.get("company")
        day = request.query_params.get("day")
        interview_status = request.query_params.get("status")
        room = request.query_params.get("room")
        panel = request.query_params.get("panel")

        if student:
            interviews = interviews.filter(
                student__student_id=student
            )

        if company:
            interviews = interviews.filter(
                company__company_id=company
            )

        if day:
            interviews = interviews.filter(day=day)

        if interview_status:
            interviews = interviews.filter(
                status=interview_status
            )

        if room:
            interviews = interviews.filter(
                room__room_id=room
            )

        if panel:
            interviews = interviews.filter(
                panel__panel_id=panel
            )

        paginator = InterviewPagination()
        page = paginator.paginate_queryset(
            interviews,
            request,
        )

        serializer = InterviewSerializer(
            page,
            many=True,
        )

        return paginator.get_paginated_response(
            serializer.data
        )


# REPLAN
class ReplanApiView(APIView):
    def post(self, request):
        replan_type = request.data.get("type")
        replanner = Replanner()

        if replan_type == "company_delay":
            company_id = request.data.get("company")
            delay_hours = request.data.get("delay_hours")

            if not company_id or delay_hours is None:
                return Response(
                    {
                        "error": "company and delay_hours are required"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            try:
                company = Company.objects.get(
                    company_id=company_id
                )
            except Company.DoesNotExist:
                return Response(
                    {"error": "Company not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            try:
                delay_hours = int(delay_hours)
            except (TypeError, ValueError):
                return Response(
                    {"error": "delay_hours must be an integer"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            changes = replanner.replan(
                company,
                delay_hours,
            )

        elif replan_type == "panel_dropout":
            panel_id = request.data.get("panel")

            if not panel_id:
                return Response(
                    {"error": "panel is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            try:
                panel = Panel.objects.get(
                    panel_id=panel_id
                )
            except Panel.DoesNotExist:
                return Response(
                    {"error": "Panel not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            changes = replanner.replan_panel(panel)

        elif replan_type == "room_unavailable":
            room_id = request.data.get("room")

            if not room_id:
                return Response(
                    {"error": "room is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            try:
                room = Room.objects.get(
                    room_id=room_id
                )
            except Room.DoesNotExist:
                return Response(
                    {"error": "Room not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            changes = replanner.replan_room(room)

        elif replan_type == "student_withdrawal":
            student_id = request.data.get("student")

            if not student_id:
                return Response(
                    {"error": "student is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            try:
                student = Student.objects.get(
                    student_id=student_id
                )
            except Student.DoesNotExist:
                return Response(
                    {"error": "Student not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            changes = replanner.withdraw_student(student)

        else:
            return Response(
                {"error": "Invalid replan type"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "message": "Replanning completed",
                "changes": changes,
            },
            status=status.HTTP_200_OK,
        )


# ROOM
class RoomListApiView(APIView):
    def get(self, request):
        rooms = Room.objects.all()
        serializer = RoomSerializer(
            rooms,
            many=True,
        )
        return Response(serializer.data)


# PANEL
class PanelListApiView(APIView):
    def get(self, request):
        panels = Panel.objects.all()
        serializer = PanelSerializer(
            panels,
            many=True,
        )
        return Response(serializer.data)