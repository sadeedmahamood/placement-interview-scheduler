# from datetime import datetime, timedelta, time
# from django.db import transaction
# from django.core.exceptions import ValidationError
# import logging

# from scheduler.models import Interview, Room, Panel

# logger = logging.getLogger(__name__)


# class Replanner:
#     """Handles rescheduling of interviews when conflicts arise."""

#     # Configuration constants
#     DAY_START = time(9, 0)      # 9:00 AM
#     DAY_END = time(17, 0)       # 5:00 PM
#     SLOT_MINUTES = 15           # 15-minute increments
#     MAX_DAY = 5                 # Maximum days to schedule (Monday-Friday)

#     # ---------------------------------------------------------
#     # SCHEDULE HELPERS
#     # ---------------------------------------------------------

#     def get_old_schedule(self, interview):
#         """Return the current interview schedule."""
#         return {
#             "day": interview.day,
#             "start_time": interview.start_time,
#             "end_time": interview.end_time,
#             "panel": interview.panel.panel_id if interview.panel else None,
#             "room": interview.room.room_id if interview.room else None,
#         }

#     def get_new_schedule(self, interview):
#         """Return the updated interview schedule."""
#         return {
#             "day": interview.day,
#             "start_time": interview.start_time,
#             "end_time": interview.end_time,
#             "panel": interview.panel.panel_id if interview.panel else None,
#             "room": interview.room.room_id if interview.room else None,
#         }

#     def validate_interview(self, interview):
#         """Validate interview has all required fields."""
#         if not interview:
#             raise ValueError("Interview cannot be None")
#         if not interview.student:
#             raise ValueError("Interview must have a student")
#         if not interview.company:
#             raise ValueError("Interview must have a company")
#         if not interview.company.interview_duration:
#             raise ValueError("Company must have interview duration")

#     # ---------------------------------------------------------
#     # TIME HELPERS
#     # ---------------------------------------------------------

#     def time_to_minutes(self, value):
#         """Convert time object to minutes since midnight."""
#         return value.hour * 60 + value.minute

#     def minutes_to_time(self, minutes):
#         """Convert minutes since midnight to time object."""
#         minutes = max(0, min(minutes, 24 * 60 - 1))  # Clamp to valid range
#         return time(minutes // 60, minutes % 60)

#     def generate_slots(self, duration):
#         """
#         Generate every possible start time between 09:00 and 17:00
#         using 15-minute increments.
#         """
#         start = self.time_to_minutes(self.DAY_START)
#         end = self.time_to_minutes(self.DAY_END)

#         current = start
#         while current + duration <= end:
#             yield (
#                 self.minutes_to_time(current),
#                 self.minutes_to_time(current + duration),
#             )
#             current += self.SLOT_MINUTES

#     def is_within_business_hours(self, start_time, end_time):
#         """Check if time range is within business hours."""
#         day_start = self.time_to_minutes(self.DAY_START)
#         day_end = self.time_to_minutes(self.DAY_END)
#         start_min = self.time_to_minutes(start_time)
#         end_min = self.time_to_minutes(end_time)
#         return day_start <= start_min and end_min <= day_end

#     # ---------------------------------------------------------
#     # RESOURCE CHECKS (FIXED)
#     # ---------------------------------------------------------

#     def room_is_free(self, room, interview):
#         """Check whether a room is available for the interview."""
#         if not room or not room.is_available:
#             return False

#         if interview.start_time is None or interview.end_time is None:
#             return False

#         # ✅ Exclude non-scheduled statuses
#         return not Interview.objects.filter(
#             room=room,
#             day=interview.day,
#             start_time__lt=interview.end_time,
#             end_time__gt=interview.start_time,
#             status="SCHEDULED",
#         ).exclude(
#             id=interview.id
#         ).exclude(
#             status__in=["UNSCHEDULED", "WITHDRAWN", "CANCELLED"]
#         ).exists()

#     def panel_is_free(self, panel, interview):
#         """Check whether a panel is available."""
#         if not panel:
#             return False

#         # ✅ FIXED: Check if panel is available
#         if hasattr(panel, 'is_available') and not panel.is_available:
#             return False

#         if interview.start_time is None or interview.end_time is None:
#             return False

#         return not Interview.objects.filter(
#             panel=panel,
#             day=interview.day,
#             start_time__lt=interview.end_time,
#             end_time__gt=interview.start_time,
#             status="SCHEDULED",
#         ).exclude(
#             id=interview.id
#         ).exclude(
#             status__in=["UNSCHEDULED", "WITHDRAWN", "CANCELLED"]
#         ).exists()

#     def student_is_free(self, interview):
#         """Check whether a student is available."""
#         if not interview.student:
#             return False

#         if interview.start_time is None or interview.end_time is None:
#             return False

#         return not Interview.objects.filter(
#             student=interview.student,
#             day=interview.day,
#             start_time__lt=interview.end_time,
#             end_time__gt=interview.start_time,
#             status="SCHEDULED",
#         ).exclude(
#             id=interview.id
#         ).exclude(
#             status__in=["UNSCHEDULED", "WITHDRAWN", "CANCELLED"]
#         ).exists()

#     # ---------------------------------------------------------
#     # CHECK A COMPLETE SLOT
#     # ---------------------------------------------------------

#     def slot_is_valid(
#         self,
#         interview,
#         day,
#         start_time,
#         end_time,
#         panel,
#         room,
#     ):
#         """Check if a slot is valid for the interview."""
#         if not panel or not room:
#             return False

#         if not room.is_available:
#             return False

#         # ✅ FIXED: Check panel availability
#         if hasattr(panel, 'is_available') and not panel.is_available:
#             return False

#         # ✅ FIXED: Validate business hours
#         if not self.is_within_business_hours(start_time, end_time):
#             return False

#         # Store original values for restoration
#         old_day = interview.day
#         old_start = interview.start_time
#         old_end = interview.end_time
#         old_panel = interview.panel
#         old_room = interview.room

#         try:
#             # Temporarily set candidate values
#             interview.day = day
#             interview.start_time = start_time
#             interview.end_time = end_time
#             interview.panel = panel
#             interview.room = room

#             # Check all constraints
#             if not self.panel_is_free(panel, interview):
#                 return False

#             if not self.room_is_free(room, interview):
#                 return False

#             if not self.student_is_free(interview):
#                 return False

#             return True

#         finally:
#             # Always restore original values
#             interview.day = old_day
#             interview.start_time = old_start
#             interview.end_time = old_end
#             interview.panel = old_panel
#             interview.room = old_room

#     # ---------------------------------------------------------
#     # FIND COMPLETE SLOT
#     # ---------------------------------------------------------

#     def find_available_slot(
#         self,
#         interview,
#         unavailable_room=None,
#         unavailable_panel=None,
#         start_day=None,
#     ):
#         """
#         Find a valid day/time/panel/room for an interview.
        
#         Search order: Day -> time -> panel -> room
#         """
#         self.validate_interview(interview)

#         duration = interview.company.interview_duration
#         if not duration:
#             return None

#         first_day = start_day if start_day else 1

#         # ✅ OPTIMIZED: Cache panels and rooms
#         panels = list(Panel.objects.filter(
#             company=interview.company
#         ).order_by("panel_id"))

#         # ✅ FIXED: Filter panels by availability
#         if hasattr(Panel, 'is_available'):
#             panels = [p for p in panels if p.is_available]

#         rooms = list(Room.objects.filter(
#             is_available=True
#         ).order_by("room_id"))

#         # Remove unavailable resources
#         if unavailable_room:
#             rooms = [r for r in rooms if r.id != unavailable_room.id]

#         if unavailable_panel:
#             panels = [p for p in panels if p.id != unavailable_panel.id]

#         for day in range(first_day, self.MAX_DAY + 1):
#             for start_time, end_time in self.generate_slots(duration):
#                 for panel in panels:
#                     if not self.panel_is_available_for_slot(
#                         panel, interview, day, start_time, end_time
#                     ):
#                         continue

#                     for room in rooms:
#                         if not self.room_is_available_for_slot(
#                             room, interview, day, start_time, end_time
#                         ):
#                             continue

#                         if not self.student_is_available_for_slot(
#                             interview, day, start_time, end_time
#                         ):
#                             continue

#                         return {
#                             "day": day,
#                             "start_time": start_time,
#                             "end_time": end_time,
#                             "panel": panel,
#                             "room": room,
#                         }

#         return None

#     # ---------------------------------------------------------
#     # SLOT-SPECIFIC CHECKS (FIXED)
#     # ---------------------------------------------------------

#     def panel_is_available_for_slot(
#         self,
#         panel,
#         interview,
#         day,
#         start_time,
#         end_time,
#     ):
#         """Check if panel is available for a specific slot."""
#         if not panel:
#             return False

#         # ✅ FIXED: Check panel availability
#         if hasattr(panel, 'is_available') and not panel.is_available:
#             return False

#         return not Interview.objects.filter(
#             panel=panel,
#             day=day,
#             start_time__lt=end_time,
#             end_time__gt=start_time,
#             status="SCHEDULED",
#         ).exclude(
#             id=interview.id
#         ).exclude(
#             status__in=["UNSCHEDULED", "WITHDRAWN", "CANCELLED"]
#         ).exists()

#     def room_is_available_for_slot(
#         self,
#         room,
#         interview,
#         day,
#         start_time,
#         end_time,
#     ):
#         """Check if room is available for a specific slot."""
#         if not room or not room.is_available:
#             return False

#         return not Interview.objects.filter(
#             room=room,
#             day=day,
#             start_time__lt=end_time,
#             end_time__gt=start_time,
#             status="SCHEDULED",
#         ).exclude(
#             id=interview.id
#         ).exclude(
#             status__in=["UNSCHEDULED", "WITHDRAWN", "CANCELLED"]
#         ).exists()

#     def student_is_available_for_slot(
#         self,
#         interview,
#         day,
#         start_time,
#         end_time,
#     ):
#         """Check if student is available for a specific slot."""
#         # ✅ FIXED: Check if student exists
#         if not interview.student:
#             return False

#         return not Interview.objects.filter(
#             student=interview.student,
#             day=day,
#             start_time__lt=end_time,
#             end_time__gt=start_time,
#             status="SCHEDULED",
#         ).exclude(
#             id=interview.id
#         ).exclude(
#             status__in=["UNSCHEDULED", "WITHDRAWN", "CANCELLED"]
#         ).exists()

#     # ---------------------------------------------------------
#     # APPLY SLOT
#     # ---------------------------------------------------------

#     @transaction.atomic
#     def apply_slot(self, interview, slot):
#         """Apply a slot to an interview with validation."""
#         if not slot:
#             raise ValueError("Cannot apply empty slot")

#         interview.day = slot["day"]
#         interview.start_time = slot["start_time"]
#         interview.end_time = slot["end_time"]
#         interview.panel = slot["panel"]
#         interview.room = slot["room"]
#         interview.status = "SCHEDULED"

#         # Validate before saving
#         interview.full_clean()
#         interview.save()

#     @transaction.atomic
#     def unschedule_interview(self, interview):
#         """Set interview to unscheduled state."""
#         interview.room = None
#         interview.panel = None
#         interview.day = None
#         interview.start_time = None
#         interview.end_time = None
#         interview.status = "UNSCHEDULED"
#         interview.save()

#     # ---------------------------------------------------------
#     # ROOM UNAVAILABLE (FIXED)
#     # ---------------------------------------------------------

#     @transaction.atomic
#     def replan_room(self, room):
#         """Replan interviews affected by a room becoming unavailable."""
#         if not room:
#             raise ValueError("Room cannot be None")

#         # Check if room is already unavailable
#         if not room.is_available:
#             logger.warning(f"Room {room.room_id} is already unavailable")
#             return []

#         affected_interviews = list(
#             Interview.objects.filter(
#                 room=room,
#                 status="SCHEDULED",
#             ).order_by(
#                 "day",
#                 "start_time",
#                 "id",
#             ).select_related("student", "company", "panel")  # ✅ OPTIMIZED
#         )

#         if not affected_interviews:
#             logger.info(f"No scheduled interviews in room {room.room_id}")
#             room.is_available = False
#             room.save(update_fields=["is_available"])
#             return []

#         changes = []

#         # Mark room as unavailable BEFORE processing
#         room.is_available = False
#         room.save(update_fields=["is_available"])

#         for interview in affected_interviews:
#             try:
#                 old_schedule = self.get_old_schedule(interview)

#                 slot = self.find_available_slot(
#                     interview,
#                     unavailable_room=room,
#                 )

#                 if slot:
#                     self.apply_slot(interview, slot)
#                     changes.append({
#                         "student": interview.student.student_id,
#                         "company": interview.company.company_id,
#                         "status": "ROOM REPLANNED",
#                         "old": old_schedule,
#                         "new": self.get_new_schedule(interview),
#                         "inform": ["STUDENT", "COMPANY"],
#                     })
#                 else:
#                     self.unschedule_interview(interview)
#                     changes.append({
#                         "student": interview.student.student_id,
#                         "company": interview.company.company_id,
#                         "status": "UNSCHEDULED",
#                         "old": old_schedule,
#                         "new": {"status": "UNSCHEDULED"},
#                         "inform": ["STUDENT", "COMPANY"],
#                     })

#             except Exception as e:
#                 logger.error(f"Error replanning interview {interview.id}: {str(e)}")
#                 raise

#         return changes

#     # ---------------------------------------------------------
#     # PANEL DROPOUT (FIXED)
#     # ---------------------------------------------------------

#     @transaction.atomic
#     def replan_panel(self, panel):
#         """Replan interviews affected by a panel becoming unavailable."""
#         if not panel:
#             raise ValueError("Panel cannot be None")

#         # ✅ FIXED: Check if panel has availability field
#         if hasattr(panel, 'is_available') and not panel.is_available:
#             logger.warning(f"Panel {panel.panel_id} is already unavailable")
#             return []

#         affected_interviews = list(
#             Interview.objects.filter(
#                 panel=panel,
#                 status="SCHEDULED",
#             ).order_by(
#                 "day",
#                 "start_time",
#                 "id",
#             ).select_related("student", "company", "room")  # ✅ OPTIMIZED
#         )

#         if not affected_interviews:
#             logger.info(f"No scheduled interviews with panel {panel.panel_id}")
#             # ✅ FIXED: Mark panel as unavailable if field exists
#             if hasattr(panel, 'is_available'):
#                 panel.is_available = False
#                 panel.save(update_fields=["is_available"])
#             return []

#         changes = []

#         # ✅ FIXED: Mark panel as unavailable if field exists
#         if hasattr(panel, 'is_available'):
#             panel.is_available = False
#             panel.save(update_fields=["is_available"])

#         for interview in affected_interviews:
#             try:
#                 old_schedule = self.get_old_schedule(interview)

#                 slot = self.find_available_slot(
#                     interview,
#                     unavailable_panel=panel,
#                 )

#                 if slot:
#                     self.apply_slot(interview, slot)
#                     changes.append({
#                         "student": interview.student.student_id,
#                         "company": interview.company.company_id,
#                         "status": "PANEL REPLANNED",
#                         "old": old_schedule,
#                         "new": self.get_new_schedule(interview),
#                         "inform": ["STUDENT", "COMPANY"],
#                     })
#                 else:
#                     self.unschedule_interview(interview)
#                     changes.append({
#                         "student": interview.student.student_id,
#                         "company": interview.company.company_id,
#                         "status": "UNSCHEDULED",
#                         "old": old_schedule,
#                         "new": {"status": "UNSCHEDULED"},
#                         "inform": ["STUDENT", "COMPANY"],
#                     })

#             except Exception as e:
#                 logger.error(f"Error replanning interview {interview.id}: {str(e)}")
#                 raise

#         return changes

#     # ---------------------------------------------------------
#     # COMPANY DELAY (FIXED)
#     # ---------------------------------------------------------

#     @transaction.atomic
#     def replan(self, company, delay_hours):
#         """Replan interviews affected by a company delay."""
#         if not company:
#             raise ValueError("Company cannot be None")

#         if delay_hours < 0:
#             raise ValueError("Delay hours cannot be negative")

#         affected_interviews = list(
#             Interview.objects.filter(
#                 company=company,
#                 status="SCHEDULED",
#             ).order_by(
#                 "day",
#                 "start_time",
#                 "id",
#             ).select_related("student", "panel", "room")  # ✅ OPTIMIZED
#         )

#         if not affected_interviews:
#             logger.info(f"No scheduled interviews for company {company.company_id}")
#             return []

#         changes = []
#         delay_minutes = delay_hours * 60

#         # ✅ FIXED: Use class constants instead of hardcoded values
#         day_start_minutes = self.time_to_minutes(self.DAY_START)
#         day_end_minutes = self.time_to_minutes(self.DAY_END)

#         for interview in affected_interviews:
#             try:
#                 old_schedule = self.get_old_schedule(interview)

#                 # Calculate original times in minutes
#                 original_start = self.time_to_minutes(interview.start_time)
#                 original_end = self.time_to_minutes(interview.end_time)
#                 duration = original_end - original_start

#                 delayed_start = original_start + delay_minutes
#                 delayed_end = delayed_start + duration

#                 scheduled = False

#                 # ---------------------------------------------------------
#                 # 1. Try exact delayed time on same day
#                 # ---------------------------------------------------------
#                 # ✅ FIXED: Use class constant
#                 if delayed_end <= day_end_minutes:
#                     candidate_start = self.minutes_to_time(delayed_start)
#                     candidate_end = self.minutes_to_time(delayed_end)

#                     if self.slot_is_valid(
#                         interview,
#                         interview.day,
#                         candidate_start,
#                         candidate_end,
#                         interview.panel,
#                         interview.room,
#                     ):
#                         interview.start_time = candidate_start
#                         interview.end_time = candidate_end
#                         interview.save()

#                         changes.append({
#                             "student": interview.student.student_id,
#                             "company": interview.company.company_id,
#                             "status": "COMPANY DELAYED",
#                             "old": old_schedule,
#                             "new": self.get_new_schedule(interview),
#                             "inform": ["STUDENT", "COMPANY"],
#                         })
#                         continue

#                 # ---------------------------------------------------------
#                 # 2. Search forward on same day in 15-min increments
#                 # ---------------------------------------------------------
#                 # ✅ FIXED: Use class constants
#                 search_start = max(delayed_start, day_start_minutes)

#                 while search_start + duration <= day_end_minutes:
#                     candidate_start = self.minutes_to_time(search_start)
#                     candidate_end = self.minutes_to_time(search_start + duration)

#                     if self.slot_is_valid(
#                         interview,
#                         interview.day,
#                         candidate_start,
#                         candidate_end,
#                         interview.panel,
#                         interview.room,
#                     ):
#                         interview.start_time = candidate_start
#                         interview.end_time = candidate_end
#                         interview.save()

#                         changes.append({
#                             "student": interview.student.student_id,
#                             "company": interview.company.company_id,
#                             "status": "COMPANY DELAYED",
#                             "old": old_schedule,
#                             "new": self.get_new_schedule(interview),
#                             "inform": ["STUDENT", "COMPANY"],
#                         })
#                         scheduled = True
#                         break

#                     search_start += self.SLOT_MINUTES  # ✅ Use class constant

#                 if scheduled:
#                     continue

#                 # ---------------------------------------------------------
#                 # 3. Find slot on later days
#                 # ---------------------------------------------------------
#                 slot = self.find_available_slot(
#                     interview,
#                     start_day=interview.day + 1,
#                 )

#                 if slot:
#                     self.apply_slot(interview, slot)
#                     changes.append({
#                         "student": interview.student.student_id,
#                         "company": interview.company.company_id,
#                         "status": "COMPANY DELAYED",
#                         "old": old_schedule,
#                         "new": self.get_new_schedule(interview),
#                         "inform": ["STUDENT", "COMPANY"],
#                     })
#                     continue

#                 # ---------------------------------------------------------
#                 # 4. No slot found - unschedule
#                 # ---------------------------------------------------------
#                 self.unschedule_interview(interview)
#                 changes.append({
#                     "student": interview.student.student_id,
#                     "company": interview.company.company_id,
#                     "status": "UNSCHEDULED",
#                     "old": old_schedule,
#                     "new": {"status": "UNSCHEDULED"},
#                     "inform": ["STUDENT", "COMPANY"],
#                 })

#             except Exception as e:
#                 logger.error(f"Error replanning interview {interview.id}: {str(e)}")
#                 raise

#         return changes

#     # ---------------------------------------------------------
#     # STUDENT WITHDRAWAL (FIXED)
#     # ---------------------------------------------------------

#     @transaction.atomic
#     def withdraw_student(self, student):
#         """Withdraw all scheduled interviews for a student."""
#         if not student:
#             raise ValueError("Student cannot be None")

#         affected_interviews = list(
#             Interview.objects.filter(
#                 student=student,
#                 status="SCHEDULED",
#             ).order_by(
#                 "day",
#                 "start_time",
#                 "id",
#             ).select_related("company")  # ✅ OPTIMIZED
#         )

#         if not affected_interviews:
#             logger.info(f"No scheduled interviews for student {student.student_id}")
#             return []

#         changes = []

#         for interview in affected_interviews:
#             try:
#                 old_schedule = self.get_old_schedule(interview)

#                 interview.status = "WITHDRAWN"
#                 interview.save()

#                 changes.append({
#                     "student": student.student_id,
#                     "company": interview.company.company_id,
#                     "status": "WITHDRAWN",
#                     "old": old_schedule,
#                     "new": {"status": "WITHDRAWN"},
#                     "inform": ["COMPANY"],
#                 })

#             except Exception as e:
#                 logger.error(f"Error withdrawing interview {interview.id}: {str(e)}")
#                 raise

#         return changes

#     # ---------------------------------------------------------
#     # ADDITIONAL USEFUL METHODS
#     # ---------------------------------------------------------

#     def get_all_conflicts(self):
#         """Find all scheduling conflicts across the system."""
#         conflicts = []
#         interviews = Interview.objects.filter(status="SCHEDULED")

#         for interview in interviews:
#             conflicting = Interview.objects.filter(
#                 day=interview.day,
#                 start_time__lt=interview.end_time,
#                 end_time__gt=interview.start_time,
#             ).exclude(id=interview.id).filter(
#                 status="SCHEDULED"
#             )

#             for conflict in conflicting:
#                 if (conflict.room == interview.room or
#                     conflict.panel == interview.panel or
#                     conflict.student == interview.student):
#                     conflicts.append({
#                         "interview1": interview.id,
#                         "interview2": conflict.id,
#                         "resource": "room" if conflict.room == interview.room else
#                                    "panel" if conflict.panel == interview.panel else
#                                    "student",
#                         "day": interview.day,
#                         "time": f"{interview.start_time}-{interview.end_time}",
#                     })

#         return conflicts

#     def cleanup_orphaned_interviews(self):
#         """Clean up interviews with missing references."""
#         count = 0
#         orphaned = Interview.objects.filter(status="SCHEDULED")

#         orphaned = orphaned.filter(
#             room__isnull=True,
#             panel__isnull=True,
#         )

#         for interview in orphaned:
#             interview.status = "UNSCHOLULED"
#             interview.save()
#             count += 1

#         return count




from datetime import time

from django.db import transaction

from scheduler.models import Interview, Room, Panel


class Replanner:

    DAY_START = time(9, 0)
    DAY_END = time(17, 0)
    SLOT_MINUTES = 15
    MAX_DAY = 5

    # ---------------------------------------------------------
    # HELPERS
    # ---------------------------------------------------------

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

    # ---------------------------------------------------------
    # CONFLICT CHECKS
    # ---------------------------------------------------------

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

    # ---------------------------------------------------------
    # FIND SLOT
    # ---------------------------------------------------------

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

    # ---------------------------------------------------------
    # APPLY / UNSCHEDULE
    # ---------------------------------------------------------

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

    # ---------------------------------------------------------
    # COMPANY DELAY
    # ---------------------------------------------------------

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

    # ---------------------------------------------------------
    # PANEL DROPOUT
    # ---------------------------------------------------------

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

    # ---------------------------------------------------------
    # ROOM UNAVAILABLE
    # ---------------------------------------------------------

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

    # ---------------------------------------------------------
    # STUDENT WITHDRAWAL
    # ---------------------------------------------------------

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

    # ---------------------------------------------------------
    # CONFLICT CHECK
    # ---------------------------------------------------------

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

    # ---------------------------------------------------------
    # CLEANUP
    # ---------------------------------------------------------

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