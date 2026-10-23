"""Academic Portal - terminal application.

Run:   python main.py            (interactive menu)
       python main.py --demo     (runs every feature once, no typing needed)
"""
import argparse
import getpass
import sys

from portal.config import load_settings
from portal.exceptions import PortalError
from portal.logger_setup import setup_logging
from portal.service import AcademicPortal

HEADER = f"{'ID':<6}{'Name':<18}{'Lvl':<4}{'Dept':<5}{'Marks':>6}  Status"


def show_load_summary(res):
    print(f"\nFiles OK     : {', '.join(res.files_ok) or '-'}")
    print(f"Files FAILED : {', '.join(res.files_failed) or '-'}")
    print(f"Students     : {len(res.students)}   Problems logged: {len(res.errors)}")
    for src, msg in res.errors:
        print(f"   ! {src}: {msg}")


def show_students(students):
    print(HEADER + "\n" + "-" * len(HEADER))
    for rank, s in enumerate(students, start=1):
        print(f"{rank:>2}. {s}")


def show_fines(portal, fines):
    print(f"{'ID':<6}{'Name':<18}{'Lvl':<4}{'Fine (Rs)':>10}")
    for s, fine in fines:
        print(f"{s.student_id:<6}{s.name:<18}{s.level:<4}{fine:>10,.2f}")
    print(f"TOTAL FINES: Rs {portal.total_fines(fines):,.2f}")


def run_demo(portal):
    portal.login(portal.settings.admin_token)
    show_load_summary(portal.load_data())
    print("\n--- RANKING ---");        show_students(portal.ranking())
    print("\n--- FAILED ---");         show_students(portal.failed_students())
    print("\n--- FINES ---");          show_fines(portal, portal.fines())
    print("\n--- DEPARTMENTS ---")
    for dept, v in portal.department_summary().items():
        print(f"{dept:<5} count={v['count']} avg={v['avg']:.1f} failed={v['failed']}")
    print("\n--- SEARCH 'usman tariq' ---")
    print(portal.find_by_name("usman tariq"))
    print("\n--- REPORTS ---")
    for kind, path in portal.generate_reports().items():
        print(f"{kind:<8}: {path}")
    print("\n--- ACCESS CONTROL TEST (viewer tries to load) ---")
    viewer = AcademicPortal(portal.settings, role="viewer")
    try:
        viewer.load_data()
    except PortalError as exc:
        print("Blocked ->", exc)


MENU = """
===== ACADEMIC PORTAL  (role: {role}) =====
 1. Load CSV data            [admin]
 2. Ranking
 3. Failed students
 4. Search student by name
 5. Department summary
 6. Late fines               [admin]
 7. Generate reports         [admin]
 0. Exit
"""


def run_menu(portal):
    token = getpass.getpass("Admin token (press Enter to continue as viewer): ")
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
                print(portal.find_by_name(input("Student name: ")))
            elif choice == "5":
                for dept, v in portal.department_summary().items():
                    print(f"{dept:<5} count={v['count']} avg={v['avg']:.1f} failed={v['failed']}")
            elif choice == "6":
                show_fines(portal, portal.fines())
            elif choice == "7":
                for kind, path in portal.generate_reports().items():
                    print(f"{kind:<8}: {path}")
            elif choice == "0":
                print("Khuda hafiz!")
                return
            else:
                print("Invalid choice.")
        except PortalError as exc:           # our own errors: show nicely, never crash
            print(f"[!] {exc}")


def main():
    parser = argparse.ArgumentParser(description="Academic Portal")
    parser.add_argument("--demo", action="store_true", help="run all features automatically")
    args = parser.parse_args()
    settings = load_settings()
    setup_logging(settings.log_file, settings.log_level)
    portal = AcademicPortal(settings)
    try:
        run_demo(portal) if args.demo else run_menu(portal)
    except (KeyboardInterrupt, EOFError):
        print("\nExiting.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
