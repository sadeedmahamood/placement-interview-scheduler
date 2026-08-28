from rest_framework import serializers
from .models import Student, Company, Application, Shortlist, Interview, Room, Panel


class StudentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Student
        fields = [
            "student_id",
            "name",
            "email",
            "phone",
            "cgpa",
            "branch",
        ]

class CompanySerializer(serializers.ModelSerializer):

    class Meta:
        model = Company
        fields = [
            "company_id",
            "name",
            "cgpa_cutoff",
            "eligible_branches",
            "interview_duration",
            "panel_count",
            "priority_tier",
        ]

class ApplicationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Application
        fields = [
            "id",
            "student",
            "company",
            "status",
        ]

class ShortlistSerializer(serializers.ModelSerializer):

    class Meta:
        model = Shortlist
        fields = [
            "id",
            "student",
            "company",
        ]

class InterviewSerializer(serializers.ModelSerializer):

    student = serializers.SlugRelatedField(many = False, read_only = True, slug_field = "student_id")

    company = serializers.SlugRelatedField(many = False, read_only = True, slug_field = "company_id")

    panel = serializers.SlugRelatedField(many = False, read_only = True, slug_field = "panel_id")

    room = serializers.SlugRelatedField(many = False, read_only = True, slug_field = "room_id")

    

    class Meta:
        model = Interview
        fields = [
            "id",
            "student",
            "company",
            "panel",
            "room",
            "day",
            "start_time",
            "end_time",
            "status",
        ]

class RoomSerializer(serializers.ModelSerializer):

    class Meta:
        model = Room
        fields = [
            "room_id",
            "name",
            "is_available",
        ]


class PanelSerializer(serializers.ModelSerializer):

    class Meta:
        model = Panel
        fields = [
            "panel_id",
            "name",
            "company",
        ]