# OOP wali classes: Person -> Student -> GraduateStudent -> HonorsStudent
from abc import ABC, abstractmethod

from .exceptions import InvalidRecordError


class Person(ABC):
    def __init__(self, name):
        self._name = name                  # protected

    @property
    def name(self):
        return self._name

    @abstractmethod
    def describe(self):
        pass                               # har child ko ye khud likhna hai


class Student(Person):
    level = "UG"                           # class attributes
    pass_marks = 40
    total_created = 0

    def __init__(self, student_id, name, department, marks, fee_due, fee_paid=None):
        super().__init__(name)
        self.student_id = student_id
        self.department = department
        self.marks = marks                 # setter se check hoga
        self.fee_due = fee_due             # date
        self.fee_paid = fee_paid           # date ya None (abhi tak nahi di)
        Student.total_created += 1

    @property
    def marks(self):
        return self.__marks

    @marks.setter
    def marks(self, value):
        if not 0 <= value <= 100:
            raise InvalidRecordError(f"marks 0 se 100 ke beech hone chahiye, mile {value}")
        self.__marks = float(value)

    @property
    def failed(self):
        return self.marks < self.pass_marks

    def late_days(self, as_of):
        # agar fee de di to us din tak, warna aaj tak
        last_day = self.fee_paid or as_of
        return max(0, (last_day - self.fee_due).days)

    def fine(self, as_of, per_day):
        return self.late_days(as_of) * per_day

    @classmethod
    def count(cls):
        return Student.total_created

    @staticmethod
    def grade(marks):
        if marks >= 80:
            return "A"
        if marks >= 65:
            return "B"
        if marks >= 50:
            return "C"
        if marks >= 40:
            return "D"
        return "F"

    def describe(self):
        return f"{self.level} student of {self.department}"

    # ---- dunder methods ----
    def __str__(self):
        status = "FAIL" if self.failed else "PASS"
        return (f"{self.student_id:<6}{self.name:<18}{self.level:<4}"
                f"{self.department:<5}{self.marks:>6.1f}  {status}")

    def __repr__(self):
        return f"{type(self).__name__}({self.student_id!r}, {self.name!r}, marks={self.marks})"

    def __eq__(self, other):
        return isinstance(other, Student) and self.student_id == other.student_id

    def __hash__(self):
        return hash(self.student_id)

    def __lt__(self, other):
        return self.marks < other.marks

    def __gt__(self, other):
        return self.marks > other.marks


class GraduateStudent(Student):
    level = "GR"
    pass_marks = 50

    def fine(self, as_of, per_day):        # overriding: parent se 1.5 guna fine
        return super().fine(as_of, per_day) * 1.5


class HonorsStudent(GraduateStudent):      # multilevel: Student -> Graduate -> Honors
    level = "HN"
    pass_marks = 60
    MAX_FINE = 2000

    def fine(self, as_of, per_day):
        return min(super().fine(as_of, per_day), self.MAX_FINE)


LEVELS = {"UG": Student, "GR": GraduateStudent, "HN": HonorsStudent}


# ---------- apna iterator ----------
class StudentIterator:
    def __init__(self, students):
        self._students = students
        self._index = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self._index >= len(self._students):
            raise StopIteration
        student = self._students[self._index]
        self._index += 1
        return student


class StudentCollection:
    """Students ki list jise len(), [], in, for aur + se use kar sakte hain."""

    def __init__(self, students=None):
        self._students = list(students or [])

    def add(self, student):
        self._students.append(student)

    def __len__(self):
        return len(self._students)

    def __getitem__(self, index):
        return self._students[index]

    def __setitem__(self, index, student):
        self._students[index] = student

    def __iter__(self):
        return StudentIterator(self._students)

    def __contains__(self, student):
        return student in self._students

    def __add__(self, other):
        return StudentCollection(self._students + other._students)

    def __repr__(self):
        return f"StudentCollection({len(self)} students)"
