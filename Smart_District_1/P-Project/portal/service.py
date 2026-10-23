"""Business logic of the portal (Days 1-10 combined)."""
import asyncio
import hmac
import logging
from collections import defaultdict
from datetime import date
from functools import reduce

from .decorators import log_call, require_role, timer
from .exceptions import StudentNotFoundError
from .loader import LoadResult, load_all
from .reports import write_reports
from .utils import binary_search

log = logging.getLogger("portal.service")


class AcademicPortal:
    def __init__(self, settings, role="viewer"):
        self.settings = settings
        self.role = role
        self.result = LoadResult()

    # ---- authentication --------------------------------------------------
    def login(self, token: str) -> str:
        ok = bool(self.settings.admin_token) and hmac.compare_digest(token, self.settings.admin_token)
        self.role = "admin" if ok else "viewer"
        log.info("login -> role=%s", self.role)
        return self.role

    # ---- data ------------------------------------------------------------
    def csv_paths(self):
        names = set(self.settings.expected_files) | {p.name for p in self.settings.data_dir.glob("*.csv")}
        return [self.settings.data_dir / n for n in sorted(names)]

    @property
    def students(self):
        return self.result.students

    @timer
    @log_call
    @require_role("admin")
    def load_data(self):
        """Load all CSV files concurrently with asyncio."""
        self.result = asyncio.run(load_all(self.csv_paths()))
        return self.result

    # ---- queries (viewer allowed) ----------------------------------------
    def ranking(self):
        """Marks high -> low; ties by name A -> Z."""
        return sorted(self.students, key=lambda s: (-s.marks, s.name))

    def failed_students(self):
        return list(filter(lambda s: s.failed, self.students))

    def find_by_name(self, name: str):
        by_name = sorted(self.students, key=lambda s: s.name.lower())
        index = binary_search(by_name, name.strip().lower(), key=lambda s: s.name.lower())
        if index == -1:
            raise StudentNotFoundError(f"no student named {name!r}")
        return by_name[index]

    def department_summary(self):
        groups = defaultdict(list)
        for s in self.students:
            groups[s.department].append(s)
        return {
            dept: {
                "count": len(members),
                "avg": sum(m.marks for m in members) / len(members),
                "failed": sum(1 for m in members if m.failed),
            }
            for dept, members in sorted(groups.items())
        }

    # ---- admin only ------------------------------------------------------
    @log_call
    @require_role("admin")
    def fines(self, as_of: date = None):
        as_of = as_of or date.today()
        pairs = [(s, s.fine(as_of, self.settings.fine_per_day)) for s in self.students]
        return sorted(((s, f) for s, f in pairs if f > 0), key=lambda p: -p[1])

    @timer
    @log_call
    @require_role("admin")
    def generate_reports(self, as_of: date = None):
        fines = self.fines(as_of)
        return write_reports(
            self.settings.report_dir, self.ranking(), self.failed_students(),
            fines, self.result.errors, self.department_summary(),
        )

    def total_fines(self, fines):
        return reduce(lambda acc, pair: acc + pair[1], fines, 0.0)
