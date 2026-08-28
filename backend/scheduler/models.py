from django.db import models

# Create your models here.

class Student(models.Model):
    student_id = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    cgpa = models.DecimalField(max_digits=4, decimal_places=2)
    branch = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.student_id} - {self.name}"

class Company(models.Model):
    company_id = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    cgpa_cutoff = models.DecimalField(max_digits=4, decimal_places=2)
    eligible_branches = models.CharField(max_length=200, blank=True, null=True)
    interview_duration = models.PositiveIntegerField(help_text="Duration in minutes")
    panel_count = models.PositiveIntegerField()
    priority_tier = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.company_id} - {self.name}"

class Room(models.Model):
    room_id = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Panel(models.Model):
    panel_id = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    is_available = models.BooleanField(default=True)
    def __str__(self):
        return self.name

class Application(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)

    status = models.CharField(max_length=100, default="APPLIED")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields= ["student", "company"],
                name = "unique_student_company_applied"
            )
        ]
    def __str__(self):
        return f"{self.student.student_id} - {self.company.company_id}"


class Shortlist(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields= ['student', 'company'],
                name = 'unique_student_company_shortlist'
            )
        ]

    def __str__(self):
        return f"{self.student.student_id} - {self.company.company_id}"

class Interview(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)      
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    panel = models.ForeignKey(Panel, on_delete=models.SET_NULL, null=True, blank=True)
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, blank=True)

    day = models.PositiveIntegerField(null=True, blank=True)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)

    status = models.CharField(max_length=20, default="UNSCHEDULED")

    def __str__(self):
        return f"{self.student.student_id} - {self.company.company_id}"
        