from schedule.models import ShiftAssignment, EmployeeWish, Vacation
from users.models import User
from django.db import models


class ShiftAssigner:
    def __init__(self, shift):
        self.shift = shift
        self.needed = {
            "morning": shift.morning_needed,
            "day": shift.day_needed,
            "night": shift.night_needed
        }
        self.assigned = {
            "morning": [],
            "day": [],
            "night": []
        }

    def is_on_vacation(self):
        return Vacation.objects.filter(
            start_date__lte=self.shift.date,
            end_date__gte=self.shift.date).exists()

    def get_employee_wishes(self):
        vacation_employee_ids = list(Vacation.objects.filter(
            start_date__lte=self.shift.date,
            end_date__gte=self.shift.date
        ).values_list("employee_id", flat=True))

        wishes = EmployeeWish.objects.filter(
            date=self.shift.date
        ).exclude(
            employee_id__in=vacation_employee_ids
        ).order_by("-created_at")

        employee_wishes = {}

        for wish in wishes:
            if wish.employee.id not in employee_wishes:
                employee_wishes[wish.employee.id] = []
            employee_wishes[wish.employee.id].append(wish)

        not_days_off = []
        free_employees = []

        for employee_id, wishes in employee_wishes.items():
            preferences = [wish.shift_preference for wish in wishes]
            if "free" in preferences:
                free_employees.append(employee_id)
            else:
                wishes_sorted = sorted(wishes, key=lambda x: x.created_at)
                not_days_off.extend([{"employee_id": employee_id, "preference": wish.shift_preference} for wish in wishes_sorted])

        return {
            "free_employees": free_employees,
            "not_days_off": not_days_off
        }

    def get_without_wishes(self):
        vacation_employee_ids = list(Vacation.objects.filter(
            start_date__lte=self.shift.date,
            end_date__gte=self.shift.date
        ).values_list("employee_id", flat=True))

        return User.objects.exclude(
            id__in=EmployeeWish.objects.filter(date=self.shift.date).values_list("employee_id", flat=True)
        ).exclude(
            id__in=vacation_employee_ids
        ).distinct()

    def assign_employees(self):
        wishes_data = self.get_employee_wishes()

        without_wishes = self.get_without_wishes()

        assigned_employees = set()

        for wish in wishes_data["not_days_off"]:
            preference = wish["preference"]
            employee_id = wish["employee_id"]
            employee = User.objects.get(id=employee_id)

            if employee not in assigned_employees and self.needed[preference] > 0:
                self.assigned[preference].append(employee)
                self.needed[preference] -= 1
                assigned_employees.add(employee)

            if all(n == 0 for n in self.needed.values()):
                break

        if any(n > 0 for n in self.needed.values()):
            for employee in without_wishes:
                if employee not in assigned_employees:
                    for shift_time in ["morning", "day", "night"]:
                        if self.needed[shift_time] > 0:
                            self.assigned[shift_time].append(employee)
                            self.needed[shift_time] -= 1
                            assigned_employees.add(employee)
                            break

                if all(n == 0 for n in self.needed.values()):
                    break

        if any(n > 0 for n in self.needed.values()):
            for employee_id in wishes_data["free_employees"]:
                employee = User.objects.get(id=employee_id)
                if employee not in assigned_employees:
                    for shift_time in ["morning", "day", "night"]:
                        if self.needed[shift_time] > 0:
                            self.assigned[shift_time].append(employee)
                            self.needed[shift_time] -= 1
                            assigned_employees.add(employee)
                            break

                if all(n == 0 for n in self.needed.values()):
                    break

    def create_assignments(self):
        for shift_time, employees in self.assigned.items():
            for employee in employees:
                if not ShiftAssignment.objects.filter(shift=self.shift, employee=employee).exists():
                    ShiftAssignment.objects.create(shift=self.shift, employee=employee, shift_type=shift_time)

    def run_assignment(self):
        self.assign_employees()
        self.create_assignments()

