# Academic Portal (terminal wali application)
#
# python main.py --demo   -> saare features ek baar apne aap chalte hain
# python main.py          -> menu (admin token do ya Enter dabao = viewer)
import argparse
import getpass
import sys

from portal.config import Settings
from portal.exceptions import PortalError
from portal.logger_setup import setup_logging
from portal.service import AcademicPortal

HEADER = f"{'ID':<6}{'Name':<18}{'Lvl':<4}{'Dept':<5}{'Marks':>6}  Status"

MENU = """
===== ACADEMIC PORTAL  (role: {role}) =====
 1. Load CSV data              [admin]
 2. Ranking
 3. Failed students
 4. Search student by name
 5. Department summary
 6. Grade counts
 7. Late fines                 [admin]
 8. Generate reports           [admin]
 0. Exit
"""


def show_load_summary(result):
    print(f"\nFiles OK     : {', '.join(result.files_ok) or '-'}")
    print(f"Files FAILED : {', '.join(result.files_failed) or '-'}")
    print(f"Students     : {len(result.students)}    Problems: {len(result.problems)}")
    for source, message in result.problems:
        print(f"   ! {source}: {message}")


def show_students(students):
    print(HEADER)
    print("-" * len(HEADER))
    for position, student in enumerate(students, start=1):
        print(f"{position:>2}. {student}")


def show_fines(portal, fines):
    print(f"{'ID':<6}{'Name':<18}{'Lvl':<4}{'Fine (Rs)':>10}")
    for student, fine in fines:
        print(f"{student.student_id:<6}{student.name:<18}{student.level:<4}{fine:>10,.2f}")
    print(f"TOTAL FINES: Rs {portal.total_fines(fines):,.2f}")


def show_departments(portal):
    for dept, info in portal.department_summary().items():
        print(f"{dept:<5} count={info['count']}  avg={info['avg']:.1f}  "
              f"std={info['std']:.1f}  failed={info['failed']}")


def run_demo(portal):
    portal.login(portal.settings.admin_token)
    show_load_summary(portal.load_data())

    print("\n--- RANKING ---")
    show_students(portal.ranking())
    print("\n--- FAILED STUDENTS ---")
    show_students(portal.failed_students())
    print("\n--- LATE FINES ---")
    show_fines(portal, portal.fines())
    print("\n--- DEPARTMENTS ---")
    show_departments(portal)
    print("\n--- GRADES ---")
    print(portal.grade_counts(), f"| pass percentage: {portal.pass_percentage()}%")
    print("\n--- SEARCH 'usman tariq' ---")
    print(portal.find_by_name("usman tariq"))
    print("\n--- REPORTS ---")
    for kind, path in portal.generate_reports().items():
        print(f"{kind:<8}: {path}")

    print("\n--- ACCESS TEST (viewer data load karne ki koshish karta hai) ---")
    viewer = AcademicPortal(portal.settings, role="viewer")
    try:
        viewer.load_data()
    except PortalError as e:
        print("Blocked ->", e)


def run_menu(portal):
    token = getpass.getpass("Admin token (Enter dabao = viewer): ")
    portal.login(token)

    while True:
        print(MENU.format(role=portal.role))
        choice = input("Choice: ").strip()
        try:
            if choice == "1":
                show_load_summary(portal.load_data())
            elif choice == "2":
                show_students(portal.ranking())
            elif choice == "3":
                show_students(portal.failed_students())
            elif choice == "4":
                print(portal.find_by_name(input("Student ka naam: ")))
            elif choice == "5":
                show_departments(portal)
            elif choice == "6":
                print(portal.grade_counts())
            elif choice == "7":
                show_fines(portal, portal.fines())
            elif choice == "8":
                for kind, path in portal.generate_reports().items():
                    print(f"{kind:<8}: {path}")
            elif choice == "0":
                print("Allah hafiz!")
                return
            else:
                print("Galat choice, dobara try karo.")
        except PortalError as e:             # apne errors: message dikhao, crash nahi
            print(f"[!] {e}")


def main():
    parser = argparse.ArgumentParser(description="Academic Portal")
    parser.add_argument("--demo", action="store_true", help="saare features automatically chalao")
    args = parser.parse_args()

    settings = Settings()
    setup_logging(settings.log_file, settings.log_level)
    portal = AcademicPortal(settings)

    try:
        if args.demo:
            run_demo(portal)
        else:
            run_menu(portal)
    except (KeyboardInterrupt, EOFError):
        print("\nBand kar raha hoon.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
