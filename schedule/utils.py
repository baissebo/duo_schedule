from datetime import timedelta

from schedule.models import Shift


def shift_restrictions(employee, target_date):
    shifts = Shift.objects.filter(assigned_employee=employee, date__gte=target_date - timedelta(days=3))

    if shifts.count() >= 4:
        return False

    if shifts.filter(date=target_date - timedelta(days=1), shift_preference="night").exists():
        if shifts.filter(date=target_date, shift_preference="morning").exists():
            return False

    return True


def assign_employees(shift, wishes):
    morning_needed = shift.morning_needed
    day_needed = shift.day_needed
    night_needed = shift.night_needed

    assigned = {
        "morning": [],
        "day": [],
        "night": []
    }

    for wish in wishes:
        if shift_restrictions(wish.employee, shift.date):
            if wish.shift_preference == "morning" and morning_needed > 0:
                assigned["morning"].append(wish.employee)
                morning_needed -= 1
            elif wish.shift_preference == "day" and day_needed > 0:
                assigned["day"].append(wish.employee)
                day_needed -= 1
            elif wish.shift_preference == "night" and night_needed > 0:
                assigned["night"].append(wish.employee)
                night_needed -= 1

        if morning_needed == 0 and day_needed == 0 and night_needed == 0:
            break

    for shift_time in ["morning", "day", "night"]:
        shift.assigned_employees.add(*assigned[shift_time])
