# Portal ka main logic. Sab pichle dinon ke concepts yahan ek saath use hue hain.
import asyncio
import hmac
import logging
import math
import os
from collections import Counter
from datetime import date
from functools import reduce

from .decorators import log_call, require_role, timer
from .exceptions import StudentNotFoundError
from .loader import LoadResult, load_all
from .models import Student
from .reports import write_reports
from .sorting import binary_search, insertion_sort

log = logging.getLogger("portal.service")


class AcademicPortal:
    def __init__(self, settings, role="viewer"):
        self.settings = settings
        self.role = role
        self.result = LoadResult()

    # ---------- login ----------
    def login(self, token):
        # compare_digest se timing attack nahi hota
        is_admin = bool(self.settings.admin_token) and hmac.compare_digest(token, self.settings.admin_token)
        self.role = "admin" if is_admin else "viewer"
        log.info("login hua, role = %s", self.role)
        return self.role

    # ---------- data ----------
    def csv_paths(self):
        found = {name for name in os.listdir(self.settings.data_dir) if name.endswith(".csv")}
        names = sorted(found | set(self.settings.expected_files))     # set union
        return [os.path.join(self.settings.data_dir, n) for n in names]

    @property
    def students(self):
        return self.result.students

    @timer
    @log_call
    @require_role("admin")
    def load_data(self):
        self.result = asyncio.run(load_all(self.csv_paths()))
        return self.result

    # ---------- queries (viewer bhi kar sakta hai) ----------
    def ranking(self):
        # marks zyada pehle, barabar hon to naam A-Z. Sort khud ka likha hua (insertion sort)
        return insertion_sort(self.students, key=lambda s: (-s.marks, s.name))

    def failed_students(self):
        return list(filter(lambda s: s.failed, self.students))

    def find_by_name(self, name):
        by_name = sorted(self.students, key=lambda s: s.name.lower())
        index = binary_search(by_name, name.strip().lower(), key=lambda s: s.name.lower())
        if index == -1:
            raise StudentNotFoundError(f"'{name}' naam ka student nahi mila")
        return by_name[index]

    def department_summary(self):
        departments = {s.department for s in self.students}            # set comprehension
        summary = {}
        for dept in sorted(departments):
            marks = [s.marks for s in self.students if s.department == dept]
            average = sum(marks) / len(marks)
            variance = sum(math.pow(m - average, 2) for m in marks) / len(marks)
            summary[dept] = {
                "count": len(marks),
                "avg": average,
                "std": math.sqrt(variance),                           # standard deviation
                "failed": len([s for s in self.students if s.department == dept and s.failed]),
            }
        return summary

    def grade_counts(self):
        grades = [Student.grade(s.marks) for s in self.students]
        return dict(sorted(Counter(grades).items()))

    def pass_percentage(self):
        if len(self.students) == 0:
            return 0
        passed = len(self.students) - len(self.failed_students())
        return math.floor(passed * 100 / len(self.students))

    # ---------- sirf admin ----------
    @log_call
    @require_role("admin")
    def fines(self, as_of=None):
        as_of = as_of or date.today()
        pairs = [(s, s.fine(as_of, self.settings.fine_per_day)) for s in self.students]
        with_fine = [(s, f) for s, f in pairs if f > 0]
        return sorted(with_fine, key=lambda pair: pair[1], reverse=True)

    def total_fines(self, fines):
        return reduce(lambda total, pair: total + pair[1], fines, 0)

    @timer
    @log_call
    @require_role("admin")
    def generate_reports(self, as_of=None):
        return write_reports(
            self.settings.report_dir,
            self.ranking(),
            self.failed_students(),
            self.fines(as_of),
            self.result.problems,
            self.department_summary(),
        )
