"""Timestamped report generation (Days 2-3)."""
import csv
import logging
from datetime import datetime

log = logging.getLogger("portal.reports")


def write_reports(report_dir, ranked, failed, fines, errors, dept_summary):
    """Write 3 timestamped files and return their paths."""
    report_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    paths = {
        "summary": report_dir / f"summary_{stamp}.txt",
        "failed": report_dir / f"failed_students_{stamp}.csv",
        "fines": report_dir / f"late_fines_{stamp}.csv",
    }

    with open(paths["summary"], "w", encoding="utf-8") as fh:
        fh.write(f"ACADEMIC PORTAL REPORT - {datetime.now():%Y-%m-%d %H:%M:%S}\n{'=' * 60}\n")
        fh.write(f"Students loaded : {len(ranked)}\nFailed          : {len(failed)}\n")
        fh.write(f"Total fines     : Rs {sum(f for _, f in fines):,.2f}\n\nRANKING\n")
        fh.writelines(f"{rank:>3}. {s}\n" for rank, s in enumerate(ranked, start=1))
        fh.write("\nDEPARTMENT SUMMARY\n")
        fh.writelines(f"{d:<6} count={v['count']:<3} avg={v['avg']:.1f} failed={v['failed']}\n"
                      for d, v in dept_summary.items())
        fh.write(f"\nPROBLEMS ({len(errors)})\n")
        fh.writelines(f"- {src}: {msg}\n" for src, msg in errors)

    with open(paths["failed"], "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["student_id", "name", "level", "department", "marks", "pass_marks"])
        writer.writerows([s.student_id, s.name, s.level, s.department, s.marks, s.pass_marks] for s in failed)

    with open(paths["fines"], "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["student_id", "name", "level", "fine_rs"])
        writer.writerows([s.student_id, s.name, s.level, f"{fine:.2f}"] for s, fine in fines)

    log.info("reports written: %s", ", ".join(p.name for p in paths.values()))
    return paths
