from datetime import time

from django.db import transaction

from scheduler.models import Interview, Room, Panel


class Replanner:

    DAY_START = time(9, 0)
    DAY_END = time(17, 0)
    SLOT_MINUTES = 15
    MAX_DAY = 5

    
    # HELPERS
    

    def get_schedule(self, interview):
        return {
            "day": interview.day,
            "start_time": interview.start_time,
            "end_time": interview.end_time,
            "panel": interview.panel.panel_id if interview.panel else None,
            "room": interview.room.room_id if interview.room else None,
        }

    def time_to_minutes(self, value):
        return value.hour * 60 + value.minute

    def minutes_to_time(self, minutes):
        return time(minutes // 60, minutes % 60)

    def generate_slots(self, duration):
        start = self.time_to_minutes(self.DAY_START)
        end = self.time_to_minutes(self.DAY_END)

        current = start

        while current + duration <= end:
            yield (
                self.minutes_to_time(current),
                self.minutes_to_time(current + duration),
            )
            current += self.SLOT_MINUTES

    
    # CONFLICT CHECKS
    

    def panel_is_free(self, panel, interview, day, start_time, end_time):
        if not panel or not panel.is_available:
            return False

        return not Interview.objects.filter(
            panel=panel,
            day=day,
            start_time__lt=end_time,
            end_time__gt=start_time,
            status="SCHEDULED",
        ).exclude(id=interview.id).exists()

    def room_is_free(self, room, interview, day, start_time, end_time):
        if not room or not room.is_available:
            return False

        return not Interview.objects.filter(
            room=room,
            day=day,
            start_time__lt=end_time,
            end_time__gt=start_time,
            status="SCHEDULED",
        ).exclude(id=interview.id).exists()

    def student_is_free(self, interview, day, start_time, end_time):
        return not Interview.objects.filter(
            student=interview.student,
            day=day,
            start_time__lt=end_time,
            end_time__gt=start_time,
            status="SCHEDULED",
        ).exclude(id=interview.id).exists()

    def slot_is_available(
        self,
        interview,
        day,
        start_time,
        end_time,
        panel,
        room,
    ):
        if start_time < self.DAY_START:
            return False

        if end_time > self.DAY_END:
            return False

        if not self.panel_is_free(
            panel,
            interview,
            day,
            start_time,
            end_time,
        ):
            return False

        if not self.room_is_free(
            room,
            interview,
            day,
            start_time,
            end_time,
        ):
            return False

        if not self.student_is_free(
            interview,
            day,
            start_time,
            end_time,
        ):
            return False

        return True

    
    # FIND SLOT
    

    def find_available_slot(
        self,
        interview,
        unavailable_room=None,
        unavailable_panel=None,
        start_day=1,
    ):
        company = interview.company
        duration = company.interview_duration

        panels = list(
            Panel.objects.filter(
                company=company,
                is_available=True,
            ).order_by("panel_id")
        )

        rooms = list(
            Room.objects.filter(
                is_available=True
            ).order_by("room_id")
        )

        if unavailable_panel:
            panels = [
                panel
                for panel in panels
                if panel.id != unavailable_panel.id
            ]

        if unavailable_room:
            rooms = [
                room
                for room in rooms
                if room.id != unavailable_room.id
            ]

        for day in range(start_day, self.MAX_DAY + 1):

            for start_time, end_time in self.generate_slots(duration):

                for panel in panels:

                    for room in rooms:

                        if self.slot_is_available(
                            interview,
                            day,
                            start_time,
                            end_time,
                            panel,
                            room,
                        ):
                            return {
                                "day": day,
                                "start_time": start_time,
                                "end_time": end_time,
                                "panel": panel,
                                "room": room,
                            }

        return None

    
    # APPLY / UNSCHEDULE
    

    def apply_slot(self, interview, slot):
        interview.day = slot["day"]
        interview.start_time = slot["start_time"]
        interview.end_time = slot["end_time"]
        interview.panel = slot["panel"]
        interview.room = slot["room"]
        interview.status = "SCHEDULED"

        interview.save()

    def unschedule(self, interview):
        interview.day = None
        interview.start_time = None
        interview.end_time = None
        interview.panel = None
        interview.room = None
        interview.status = "UNSCHEDULED"

        interview.save()

    
    # COMPANY DELAY
    

    @transaction.atomic
    def replan(self, company, delay_hours):

        if not company:
            raise ValueError("Company is required")

        if delay_hours < 0:
            raise ValueError("Delay hours cannot be negative")

        interviews = list(
            Interview.objects.filter(
                company=company,
                status="SCHEDULED",
            ).order_by(
                "day",
                "start_time",
                "id",
            ).select_related(
                "student",
                "company",
                "panel",
                "room",
            )
        )

        changes = []

        delay_minutes = delay_hours * 60

        for interview in interviews:

            old_schedule = self.get_schedule(interview)

            duration = (
                self.time_to_minutes(interview.end_time)
                - self.time_to_minutes(interview.start_time)
            )

            new_start = (
                self.time_to_minutes(interview.start_time)
                + delay_minutes
            )

            new_end = new_start + duration

            scheduled = False

            # Try delayed time and later slots on same day
            while new_start + duration <= self.time_to_minutes(
                self.DAY_END
            ):

                start_time = self.minutes_to_time(new_start)
                end_time = self.minutes_to_time(new_end)

                if self.slot_is_available(
                    interview,
                    interview.day,
                    start_time,
                    end_time,
                    interview.panel,
                    interview.room,
                ):
                    interview.start_time = start_time
                    interview.end_time = end_time
                    interview.status = "SCHEDULED"
                    interview.save()

                    changes.append({
                        "student": interview.student.student_id,
                        "company": interview.company.company_id,
                        "status": "COMPANY DELAYED",
                        "old": old_schedule,
                        "new": self.get_schedule(interview),
                        "inform": ["STUDENT", "COMPANY"],
                    })

                    scheduled = True
                    break

                new_start += self.SLOT_MINUTES
                new_end += self.SLOT_MINUTES

            if scheduled:
                continue

            # Try later days
            slot = self.find_available_slot(
                interview,
                start_day=interview.day + 1,
            )

            if slot:
                self.apply_slot(interview, slot)

                changes.append({
                    "student": interview.student.student_id,
                    "company": interview.company.company_id,
                    "status": "COMPANY DELAYED",
                    "old": old_schedule,
                    "new": self.get_schedule(interview),
                    "inform": ["STUDENT", "COMPANY"],
                })

            else:
                self.unschedule(interview)

                changes.append({
                    "student": interview.student.student_id,
                    "company": interview.company.company_id,
                    "status": "UNSCHEDULED",
                    "old": old_schedule,
                    "new": {
                        "day": None,
                        "start_time": None,
                        "end_time": None,
                        "panel": None,
                        "room": None,
                    },
                    "inform": ["STUDENT", "COMPANY"],
                })

        return changes

    
    # PANEL DROPOUT
    

    @transaction.atomic
    def replan_panel(self, panel):

        if not panel:
            raise ValueError("Panel is required")

        if not panel.is_available:
            return []

        interviews = list(
            Interview.objects.filter(
                panel=panel,
                status="SCHEDULED",
            ).order_by(
                "day",
                "start_time",
                "id",
            ).select_related(
                "student",
                "company",
                "panel",
                "room",
            )
        )

        panel.is_available = False
        panel.save(update_fields=["is_available"])

        changes = []

        for interview in interviews:

            old_schedule = self.get_schedule(interview)

            slot = self.find_available_slot(
                interview,
                unavailable_panel=panel,
            )

            if slot:
                self.apply_slot(interview, slot)

                changes.append({
                    "student": interview.student.student_id,
                    "company": interview.company.company_id,
                    "status": "PANEL REPLANNED",
                    "old": old_schedule,
                    "new": self.get_schedule(interview),
                    "inform": ["STUDENT", "COMPANY"],
                })

            else:
                self.unschedule(interview)

                changes.append({
                    "student": interview.student.student_id,
                    "company": interview.company.company_id,
                    "status": "UNSCHEDULED",
                    "old": old_schedule,
                    "new": {
                        "day": None,
                        "start_time": None,
                        "end_time": None,
                        "panel": None,
                        "room": None,
                    },
                    "inform": ["STUDENT", "COMPANY"],
                })

        return changes

    
    # ROOM UNAVAILABLE
    

    @transaction.atomic
    def replan_room(self, room):

        if not room:
            raise ValueError("Room is required")

        if not room.is_available:
            return []

        interviews = list(
            Interview.objects.filter(
                room=room,
                status="SCHEDULED",
            ).order_by(
                "day",
                "start_time",
                "id",
            ).select_related(
                "student",
                "company",
                "panel",
                "room",
            )
        )

        room.is_available = False
        room.save(update_fields=["is_available"])

        changes = []

        for interview in interviews:

            old_schedule = self.get_schedule(interview)

            slot = self.find_available_slot(
                interview,
                unavailable_room=room,
            )

            if slot:
                self.apply_slot(interview, slot)

                changes.append({
                    "student": interview.student.student_id,
                    "company": interview.company.company_id,
                    "status": "ROOM REPLANNED",
                    "old": old_schedule,
                    "new": self.get_schedule(interview),
                    "inform": ["STUDENT", "COMPANY"],
                })

            else:
                self.unschedule(interview)

                changes.append({
                    "student": interview.student.student_id,
                    "company": interview.company.company_id,
                    "status": "UNSCHEDULED",
                    "old": old_schedule,
                    "new": {
                        "day": None,
                        "start_time": None,
                        "end_time": None,
                        "panel": None,
                        "room": None,
                    },
                    "inform": ["STUDENT", "COMPANY"],
                })

        return changes

    # STUDENT WITHDRAWAL

    @transaction.atomic
    def withdraw_student(self, student):

        if not student:
            raise ValueError("Student is required")

        interviews = list(
            Interview.objects.filter(
                student=student,
                status="SCHEDULED",
            ).order_by(
                "day",
                "start_time",
                "id",
            ).select_related(
                "student",
                "company",
                "panel",
                "room",
            )
        )

        changes = []

        for interview in interviews:

            old_schedule = self.get_schedule(interview)

            interview.day = None
            interview.start_time = None
            interview.end_time = None
            interview.panel = None
            interview.room = None
            interview.status = "WITHDRAWN"

            interview.save()

            changes.append({
                "student": student.student_id,
                "company": interview.company.company_id,
                "status": "WITHDRAWN",
                "old": old_schedule,
                "new": {
                    "day": None,
                    "start_time": None,
                    "end_time": None,
                    "panel": None,
                    "room": None,
                },
                "inform": ["COMPANY"],
            })

        return changes

    # CONFLICT CHECK

    def get_all_conflicts(self):

        conflicts = []

        interviews = Interview.objects.filter(
            status="SCHEDULED"
        ).select_related(
            "student",
            "panel",
            "room",
        )

        for interview in interviews:

            others = Interview.objects.filter(
                status="SCHEDULED",
                day=interview.day,
                start_time__lt=interview.end_time,
                end_time__gt=interview.start_time,
            ).exclude(
                id=interview.id
            )

            for other in others:

                if other.room_id == interview.room_id:
                    resource = "room"

                elif other.panel_id == interview.panel_id:
                    resource = "panel"

                elif other.student_id == interview.student_id:
                    resource = "student"

                else:
                    continue

                conflicts.append({
                    "interview1": interview.id,
                    "interview2": other.id,
                    "resource": resource,
                    "day": interview.day,
                    "time": (
                        f"{interview.start_time}-"
                        f"{interview.end_time}"
                    ),
                })

        return conflicts

    # CLEANUP


    def cleanup_orphaned_interviews(self):

        interviews = Interview.objects.filter(
            status="SCHEDULED",
            room__isnull=True,
            panel__isnull=True,
        )

        count = interviews.update(
            status="UNSCHEDULED",
            day=None,
            start_time=None,
            end_time=None,
        )

        return count