import sys, unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from portal.decorators import require_role
from portal.exceptions import AccessDeniedError, InvalidRecordError
from portal.loader import load_file, parse_row
from portal.models import GraduateStudent, HonorsStudent, Student
from portal.utils import binary_search

DATA = Path(__file__).resolve().parent.parent / "data"


class Dummy:
    role = "viewer"

    @require_role("admin")
    def secret(self):
        """doc"""
        return 1


class Tests(unittest.TestCase):
    def test_binary_search(self):
        self.assertEqual(binary_search([1, 3, 5, 7], 5), 2)
        self.assertEqual(binary_search([1, 3, 5, 7], 4), -1)

    def test_fine_overriding(self):
        due, today = date(2026, 9, 1), date(2026, 9, 11)
        ug = Student("a", "A", "CS", 50, due)
        gr = GraduateStudent("b", "B", "CS", 50, due)
        hn = HonorsStudent("c", "C", "CS", 50, date(2020, 1, 1))
        self.assertEqual(ug.fine(today, 50), 500)
        self.assertEqual(gr.fine(today, 50), 750)
        self.assertEqual(hn.fine(today, 50), 2000)   # capped

    def test_pass_marks_by_level(self):
        self.assertTrue(GraduateStudent("x", "X", "CS", 45, date.today()).failed)
        self.assertFalse(Student("y", "Y", "CS", 45, date.today()).failed)

    def test_invalid_rows(self):
        bad = {"student_id": "S1", "name": "a", "level": "UG", "department": "cs",
               "marks": "abc", "fee_due": "2026-09-01", "fee_paid": ""}
        with self.assertRaises(InvalidRecordError):
            parse_row(bad, 2)

    def test_files_never_crash(self):
        self.assertEqual(len(load_file(DATA / "nope.csv").files_failed), 1)
        self.assertEqual(len(load_file(DATA / "students_corrupt.csv").files_failed), 1)
        res = load_file(DATA / "students_se.csv")
        self.assertTrue(res.files_ok and res.errors)

    def test_role_decorator_keeps_metadata(self):
        self.assertEqual(Dummy.secret.__name__, "secret")
        with self.assertRaises(AccessDeniedError):
            Dummy().secret()


if __name__ == "__main__":
    unittest.main()
