import random
from django.db.models import Q
from datetime import datetime, time, timedelta
from faker import Faker
from django.core.management.base import BaseCommand
from scheduler.models import Student, Company, Room, Panel, Application, Shortlist, Interview

class Command(BaseCommand):
    help = 'generate placement datas'

    def handle(self, *args, **kwargs):

        fake = Faker("en_IN")

        Student.objects.all().delete()
        Company.objects.all().delete()
        Room.objects.all().delete()
        Panel.objects.all().delete()
        Application.objects.all().delete()
        Shortlist.objects.all().delete()
        Interview.objects.all().delete()

        # scheduled_interview = []

        branches = ["CSE", "IT", "BCA", "ECE", "BBA"]
        interview_duration = [30, 45, 60]
        priority_tier = ["Tier 1", "Tier 2", "Tier 3"]

        # STUDEND
        for i in range(1, 801):

            random_name = fake.name()
            email_name = random_name.lower().replace(" ", ".")
            random_cgpa = round(random.uniform(6.0, 10.0), 2)
            random_branch = random.choice(branches)
            random_number = str(random.randint(9000000000, 9999999999))

            stud = Student.objects.create(
                student_id = f"S{i:03d}",
                name = random_name,
                email = f"{email_name}{i:03d}@gmail.com",
                phone = random_number,
                cgpa = random_cgpa,
                branch = random_branch,
            )
            print( stud.name,
                   stud.email,
                   stud.phone,
                )

        # COMPANY
        for i in range(1, 36):

            random_company_name = fake.company()
            random_cutoff = random.randint(6,8)
            duration = random.choice(interview_duration)
            random_panel_count = random.randint(1,5)
            random_priority = random.choice(priority_tier)
            random_branch_count = random.randint(1,3)
            random_branches = random.sample(branches, random_branch_count)
            eligible_branches = ", ".join(random_branches)


            company = Company.objects.create(
                company_id = f"C{i:03d}",
                name = random_company_name,
                cgpa_cutoff = random_cutoff,
                eligible_branches = eligible_branches,
                interview_duration = duration,
                panel_count = random_panel_count,
                priority_tier = random_priority,
            )
            print(         
            company.company_id,
            company.name,
            company.cgpa_cutoff,
            company.eligible_branches,
            company.interview_duration,
            company.panel_count,
            company.priority_tier
        )


        # ROOM
        for i in range(1, 21):
            room = Room.objects.create(
                room_id = f"R{i:03d}",
                name = f"Room {i}",
                is_available = True,
            )
            print(room.room_id,
                  room.name,
                  room.is_available
                )


        # PANEL
        companies= Company.objects.all()
        for c in companies:
            for j in range(1, c.panel_count + 1):
                panel = Panel.objects.create(
                    panel_id = f"{c.company_id}-P{j:03d}",
                    name = f"Panel {j}",
                    company = c,
                )
                print(
                    panel.panel_id,
                    panel.name,
                    panel.company
                )


        # APPLICATION
        stud = Student.objects.all()
        company = list(Company.objects.all())
        for s in stud:
            application_count = random.randint(1,3)
            selected_company = random.sample(company, application_count)

            for c in selected_company:
                application = Application.objects.create(
                    company = c,
                    student = s,
                )
                print(
                    application.company,
                    application.student,
                    application.status,
                )

        # SHORTLIST
        application = Application.objects.all()

        for a in application:
            eligible_branches = a.company.eligible_branches.split(", ")

            if (a.student.cgpa >= a.company.cgpa_cutoff 
                and
                a.student.branch in eligible_branches
                ):

                shortlist = Shortlist.objects.create(
                    company = a.company,
                    student = a.student,

                )
                print(
                    "SHORTLISTED:",
                    shortlist.student.student_id,
                    shortlist.company.company_id
                )



        # SCHEDULING
        shortlists = Shortlist.objects.select_related("student", "company")

        rooms = list(Room.objects.all())

        scheduled_interviews = []

        for s in shortlists:

            student = s.student
            company = s.company

            panels = list(Panel.objects.filter(company = company))

            scheduled = False

            for day in range(1, 6):
                current_time = time(9, 0)

                while current_time < time(17, 0):

                    start_time = current_time

                    end_datetime = (
                        datetime.combine(
                            datetime.today(),
                            start_time
                        )
                        + timedelta(minutes=company.interview_duration)
                    )

                    end_time = end_datetime.time()

                    if end_time > time(17, 0):
                        break

                    for panel in panels:

                        for room in rooms:

                            if not self.has_conflict(
                                scheduled_interviews,
                                student,
                                panel,
                                room,
                                day,
                                start_time,
                                end_time,
                            ):

                                interview = Interview.objects.create(
                                    student = student,
                                    company = company,
                                    panel  = panel,
                                    room = room,
                                    day = day,
                                    start_time = start_time,
                                    end_time = end_time,
                                    status = "SCHEDULED"

                                )

                                scheduled_interviews.append(
                                    {
                                        "student" : student,
                                        "panel" : panel,
                                        "room" : room,
                                        "day" : day,
                                        "start_time" : start_time,
                                        "end_time" : end_time
                                    }
                                )

                                print(
                                    "SCHEDULED",
                                    interview.student.student_id,
                                    interview.company.company_id,
                                    interview.panel.panel_id,
                                    interview.room.room_id,
                                    interview.day,
                                    interview.start_time,
                                    interview.end_time
                                )

                                scheduled = True
                                break

                        if scheduled:
                            break

                    if scheduled:
                        break

                    current_time = (
                        datetime.combine(
                            datetime.today(),
                            current_time
                        )
                        + timedelta(minutes=15)
                    ).time()

                if scheduled:
                    break

            if not scheduled:
                interview = Interview.objects.create(
                    student = student,
                    company = company,
                    panel = None,
                    room = None,
                    day = None,
                    start_time = None,
                    end_time = None,
                    status = "UNSCHEDULED"
                )
                print(
                    "UNSCHEDULED",
                    student.student_id,
                    company.company_id,
                )


        self.stdout.write(
            self.style.SUCCESS(
                "Placement data generation completed!"

            )
        )
                

                        

    def has_conflict(
            self,
            scheduled_interviews,
            student,
            panel,
            room,
            day,
            start_time,
            end_time,
        ):

            for interview in scheduled_interviews:

                if interview["day"] != day:
                    continue

                if (
                    start_time < interview["end_time"]
                    and
                    end_time > interview["start_time"]
                ):

                    if (
                        interview["student"] == student
                        or
                        interview["panel"] == panel
                        or
                        interview["room"] == room
                    ):
                        return True

            return False
            



        

