import os
import sys
import unittest
from datetime import date

# project folder ko path mein daala taake `portal` import ho sake
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from portal.decorators import require_role
from portal.exceptions import AccessDeniedError, InvalidRecordError
from portal.loader import load_file, parse_row
from portal.models import GraduateStudent, HonorsStudent, Student, StudentCollection
from portal.sorting import binary_search, bubble_sort, insertion_sort, selection_sort

DATA = os.path.join(ROOT, "data")


class Dummy:
    role = "viewer"

    @require_role("admin")
    def secret(self):
        """meri docstring"""
        return 1


class SortingTests(unittest.TestCase):
    numbers = [5, 2, 9, 1, 5, 6]

    def test_sorts_match_python_sorted(self):
        for algo in (bubble_sort, selection_sort, insertion_sort):
            self.assertEqual(algo(self.numbers), sorted(self.numbers))

    def test_binary_search(self):
        self.assertEqual(binary_search([1, 3, 5, 7], 5), 2)
        self.assertEqual(binary_search([1, 3, 5, 7], 4), -1)


class ModelTests(unittest.TestCase):
    def setUp(self):
        self.due = date(2026, 9, 1)
        self.today = date(2026, 9, 11)             # 10 din late

    def test_fine_overriding(self):
        ug = Student("A", "a", "CS", 50, self.due)
        gr = GraduateStudent("B", "b", "CS", 50, self.due)
        self.assertEqual(ug.fine(self.today, 10), 100)
        self.assertEqual(gr.fine(self.today, 10), 150)

    def test_honors_fine_limit(self):
        hn = HonorsStudent("C", "c", "CS", 80, date(2025, 1, 1))
        self.assertEqual(hn.fine(self.today, 50), 2000)

    def test_marks_setter_rejects_bad_value(self):
        with self.assertRaises(InvalidRecordError):
            Student("A", "a", "CS", 150, self.due)

    def test_pass_marks_differ_by_level(self):
        self.assertTrue(Student("A", "a", "CS", 45, self.due).failed is False)
        self.assertTrue(GraduateStudent("B", "b", "CS", 45, self.due).failed)

    def test_collection_iterator_and_dunders(self):
        s1 = Student("A", "a", "CS", 50, self.due)
        s2 = Student("B", "b", "CS", 60, self.due)
        both = StudentCollection([s1]) + StudentCollection([s2])
        self.assertEqual(len(both), 2)
        self.assertEqual([s.student_id for s in both], ["A", "B"])
        self.assertIn(s2, both)
        self.assertEqual(both[0], s1)


class LoaderTests(unittest.TestCase):
    def test_good_file(self):
        result = load_file(os.path.join(DATA, "students_cs.csv"))
        self.assertEqual(len(result.students), 6)
        self.assertEqual(result.files_failed, [])

    def test_invalid_rows_are_skipped_not_crash(self):
        result = load_file(os.path.join(DATA, "students_se.csv"))
        self.assertEqual(len(result.students), 3)
        self.assertEqual(len(result.problems), 5)

    def test_corrupt_file(self):
        result = load_file(os.path.join(DATA, "students_corrupt.csv"))
        self.assertEqual(result.files_failed, ["students_corrupt.csv"])
        self.assertEqual(len(result.students), 0)

    def test_missing_file(self):
        result = load_file(os.path.join(DATA, "nahi_hai.csv"))
        self.assertEqual(result.files_failed, ["nahi_hai.csv"])

    def test_parse_row_bad_level(self):
        row = {"student_id": "S1", "name": "x", "level": "ZZ", "department": "CS",
               "marks": "50", "fee_due": "2026-09-01", "fee_paid": ""}
        with self.assertRaises(InvalidRecordError):
            parse_row(row, 2)


class DecoratorTests(unittest.TestCase):
    def test_viewer_blocked(self):
        with self.assertRaises(AccessDeniedError):
            Dummy().secret()

    def test_wraps_keeps_name(self):
        self.assertEqual(Dummy.secret.__name__, "secret")
        self.assertEqual(Dummy.secret.__doc__, "meri docstring")


if __name__ == "__main__":
    unittest.main()
