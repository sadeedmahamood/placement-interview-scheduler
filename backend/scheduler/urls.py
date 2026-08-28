
from django.urls import path
from .views import StudentListApiView, CompanyListApiView, ApplicationListApiView, ShortlistListApiView, InterviewListApiView, ReplanApiView, PanelListApiView, RoomListApiView

urlpatterns = [
    path("students/", StudentListApiView.as_view(), name="student-list"),
    path("companys/", CompanyListApiView.as_view(), name="company-list"),
    path("applications/", ApplicationListApiView.as_view(), name="application-list"),
    path("shortlists/", ShortlistListApiView.as_view(), name="shortlist-list"),
    path("interviews/", InterviewListApiView.as_view(), name="interview-list"),
    path("rooms/", RoomListApiView.as_view(), name="room-list"),
    path("panels/", PanelListApiView.as_view(), name="panel-list"),
    path("replan/", ReplanApiView.as_view(), name="replan"),


]
