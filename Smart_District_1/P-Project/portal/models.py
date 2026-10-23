"""OOP models (Days 8-9): ABC, inheritance, overriding, properties, dunder methods."""
from abc import ABC, abstractmethod
from datetime import date

from .exceptions import InvalidRecordError


class Person(ABC):
    def __init__(self, name: str):
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    @abstractmethod
    def describe(self) -> str:
        """Every subclass must say how it describes itself."""


class Student(Person):
    """Undergraduate student (base tier)."""
    level = "UG"
    pass_marks = 40.0
    total_created = 0                     # class attribute

    def __init__(self, student_id, name, department, marks, fee_due: date, fee_paid: date = None):
        super().__init__(name)
        self.student_id = student_id
        self.department = department
        self.marks = marks                # goes through the setter
        self.fee_due = fee_due
        self.fee_paid = fee_paid
        Student.total_created += 1

    @property
    def marks(self) -> float:
        return self._marks

    @marks.setter
    def marks(self, value):
        if not 0 <= value <= 100:
            raise InvalidRecordError(f"marks must be 0-100, got {value}")
        self._marks = float(value)

    @property
    def failed(self) -> bool:
        return self._marks < self.pass_marks

    def late_days(self, as_of: date) -> int:
        end = self.fee_paid or as_of
        return max(0, (end - self.fee_due).days)

    def fine(self, as_of: date, per_day: float) -> float:
        return self.late_days(as_of) * per_day

    @classmethod
    def count(cls) -> int:
        return Student.total_created

    @staticmethod
    def grade(marks: float) -> str:
        return "A" if marks >= 80 else "B" if marks >= 65 else "C" if marks >= 50 else "D" if marks >= 40 else "F"

    def describe(self) -> str:
        return f"{self.level} student in {self.department}"

    def __str__(self):
        status = "FAIL" if self.failed else "PASS"
        return f"{self.student_id:<6}{self.name:<18}{self.level:<4}{self.department:<5}{self._marks:>6.1f}  {status}"

    def __repr__(self):
        return f"{type(self).__name__}({self.student_id!r}, {self.name!r}, marks={self._marks})"

    def __eq__(self, other):
        return isinstance(other, Student) and self.student_id == other.student_id

    def __hash__(self):
        return hash(self.student_id)

    def __lt__(self, other):
        return self._marks < other._marks

    def __gt__(self, other):
        return self._marks > other._marks


class GraduateStudent(Student):
    level = "GR"
    pass_marks = 50.0

    def fine(self, as_of, per_day):               # method overriding
        return super().fine(as_of, per_day) * 1.5


class HonorsStudent(GraduateStudent):             # multilevel: Student -> Graduate -> Honors
    level = "HN"
    pass_marks = 60.0
    MAX_FINE = 2000.0

    def fine(self, as_of, per_day):
        return min(super().fine(as_of, per_day), self.MAX_FINE)


LEVELS = {cls.level: cls for cls in (Student, GraduateStudent, HonorsStudent)}
