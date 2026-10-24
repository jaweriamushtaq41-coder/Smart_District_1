# Timestamp wali reports. Har baar naya naam banta hai, purani report overwrite nahi hoti.
import csv
import logging
import os
from datetime import datetime

log = logging.getLogger("portal.reports")


def write_reports(report_dir, ranked, failed, fines, problems, dept_summary):
    os.makedirs(report_dir, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    summary_path = os.path.join(report_dir, f"summary_{stamp}.txt")
    failed_path = os.path.join(report_dir, f"failed_students_{stamp}.csv")
    fines_path = os.path.join(report_dir, f"late_fines_{stamp}.csv")

    total_fines = sum(fine for _, fine in fines)

    with open(summary_path, "w", encoding="utf-8") as f:
        f.write(f"ACADEMIC PORTAL REPORT - {datetime.now():%Y-%m-%d %H:%M:%S}\n")
        f.write("=" * 60 + "\n")
        f.write(f"Students loaded : {len(ranked)}\n")
        f.write(f"Failed          : {len(failed)}\n")
        f.write(f"Total fines     : Rs {total_fines:,.2f}\n\n")
        f.write("RANKING\n")
        for position, student in enumerate(ranked, start=1):
            f.write(f"{position:>3}. {student}\n")
        f.write("\nDEPARTMENTS\n")
        for dept, info in dept_summary.items():
            f.write(f"{dept:<5} count={info['count']} avg={info['avg']:.1f} "
                    f"std={info['std']:.1f} failed={info['failed']}\n")
        f.write(f"\nPROBLEMS ({len(problems)})\n")
        for source, message in problems:
            f.write(f"- {source}: {message}\n")

    with open(failed_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["student_id", "name", "level", "department", "marks", "pass_marks"])
        for s in failed:
            writer.writerow([s.student_id, s.name, s.level, s.department, s.marks, s.pass_marks])

    with open(fines_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["student_id", "name", "level", "fine_rs"])
        for s, fine in fines:
            writer.writerow([s.student_id, s.name, s.level, f"{fine:.2f}"])

    log.info("reports ban gayin: %s", stamp)
    return {"summary": summary_path, "failed": failed_path, "fines": fines_path}
