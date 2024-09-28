from django.utils import timezone
from django.test import TestCase

from schedule.models import Schedule, Vacation, Shift, EmployeeWish
from schedule.utils import is_on_vacation, assign_employees
from users.models import User


class EmployeeVacationTest(TestCase):
    def setUp(self):
        self.employee = User.objects.create(email="job123@mail.com", password="password")
        self.schedule = Schedule.objects.create(date=timezone.now().date())

    def test_employee_on_vacation(self):
        vacation = Vacation.objects.create(
            employee=self.employee,
            schedule=self.schedule,
            start_date=timezone.now().date(),
            end_date=timezone.now().date()
        )
        target_date = timezone.now().date()

        self.assertTrue(is_on_vacation(self.employee, target_date))

    def test_employee_not_on_vacation(self):
        target_date = timezone.now().date()

        self.assertFalse(is_on_vacation(self.employee, target_date))


class ShiftAssignmentTests(TestCase):
    def setUp(self):
        self.employee1 = User.objects.create(email="job1@mail.com", password="password1")
        self.employee2 = User.objects.create(email="job2@mail.com", password="password2")
        self.employee3 = User.objects.create(email="job3@mail.com", password="password3")
        self.employee4 = User.objects.create(email="job4@mail.com", password="password4")
        self.employee5 = User.objects.create(email="job5@mail.com", password="password5")
        self.employee6 = User.objects.create(email="job6@mail.com", password="password6")

        self.schedule = Schedule.objects.create(date=timezone.now().date())
        self.shift = Shift.objects.create(
            schedule=self.schedule,
            date=timezone.now().date(),
            morning_needed=2,
            day_needed=1,
            night_needed=1
        )

    def test_assign_employees_with_vacation(self):
        Vacation.objects.create(
            employee=self.employee2,
            schedule=self.schedule,
            start_date=timezone.now().date(),
            end_date=timezone.now().date()
        )

        EmployeeWish.objects.create(employee=self.employee4, date=self.shift.date, shift_preference="free")
        EmployeeWish.objects.create(employee=self.employee5, date=self.shift.date,
                                    shift_preference="free")
        EmployeeWish.objects.create(employee=self.employee1, date=self.shift.date, shift_preference="morning")
        EmployeeWish.objects.create(employee=self.employee2, date=self.shift.date, shift_preference="day")
        EmployeeWish.objects.create(employee=self.employee3, date=self.shift.date, shift_preference="night")

        assign_employees(self.shift)

        self.assertIn(self.employee1, self.shift.assigned_employees.all())
        self.assertNotIn(self.employee2, self.shift.assigned_employees.all())
        self.assertIn(self.employee3, self.shift.assigned_employees.all())
        self.assertIn(self.employee5, self.shift.assigned_employees.all())


class ScheduleListViewTests(TestCase):
    def setUp(self):
        self.employee1 = User.objects.create_user(email="job1@mail.com", password="password1")
        self.schedule = Schedule.objects.create(date=timezone.now().date())
        self.shift = Shift.objects.create(
            schedule=self.schedule,
            date=timezone.now().date())

