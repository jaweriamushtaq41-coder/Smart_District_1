# CSV files padhna: safe tareeqe se, generator se, aur asyncio se saari files ek saath
import asyncio
import csv
import logging
import os
import threading
from datetime import datetime
from itertools import chain

from .exceptions import CorruptFileError, InvalidRecordError
from .models import LEVELS, StudentCollection

log = logging.getLogger("portal.loader")

REQUIRED_COLUMNS = {"student_id", "name", "level", "department", "marks", "fee_due", "fee_paid"}

# files worker threads mein padhi jati hain, isliye shared list par lock lagana zaroori hai
_lock = threading.Lock()
_files_seen = []


class LoadResult:
    def __init__(self):
        self.students = StudentCollection()
        self.problems = []          # (source, message)
        self.files_ok = []
        self.files_failed = []


def parse_date(text):
    return datetime.strptime(text.strip(), "%Y-%m-%d").date()


def parse_row(row, line_no):
    """Ek row check karke Student object banata hai. Galat ho to InvalidRecordError."""
    try:
        student_id = row["student_id"].strip()
        if student_id == "":
            raise InvalidRecordError("student_id khali hai")

        student_class = LEVELS.get(row["level"].strip().upper())
        if student_class is None:
            raise InvalidRecordError(f"level samajh nahi aya: {row['level']!r}")

        paid_text = (row["fee_paid"] or "").strip()
        return student_class(
            student_id,
            row["name"].strip().title(),
            row["department"].strip().upper(),
            float(row["marks"]),
            parse_date(row["fee_due"]),
            parse_date(paid_text) if paid_text else None,
        )
    except InvalidRecordError as e:
        raise InvalidRecordError(f"line {line_no}: {e}") from e
    except (ValueError, TypeError, KeyError, AttributeError) as e:
        raise InvalidRecordError(f"line {line_no}: {e}") from e


def read_students(path, problems):
    """Generator: ek waqt mein ek hi student yield karta hai, poori file memory mein nahi aati."""
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames or not REQUIRED_COLUMNS <= set(reader.fieldnames):
            raise CorruptFileError("header row theek nahi hai")
        for line_no, row in enumerate(reader, start=2):
            try:
                yield parse_row(row, line_no)
            except InvalidRecordError as e:
                log.warning("%s: row skip - %s", os.path.basename(path), e)
                problems.append((os.path.basename(path), str(e)))


def load_file(path):
    """Ek file padhta hai. Kabhi crash nahi karta, har masla log aur result mein chala jata hai."""
    name = os.path.basename(path)
    result = LoadResult()
    message = None
    try:
        for student in read_students(path, result.problems):
            result.students.add(student)
    except FileNotFoundError:
        message = "file nahi mili"
    except (UnicodeDecodeError, csv.Error):
        message = "file corrupt hai"
    except CorruptFileError as e:
        message = f"file corrupt hai ({e})"
    except OSError as e:
        message = f"file khuli nahi ({e})"
    else:
        result.files_ok.append(name)
        log.info("%s: %d students load hue", name, len(result.students))
    finally:
        with _lock:
            _files_seen.append(name)

    if message:
        log.error("%s: %s", name, message)
        result.problems.append((name, message))
        result.files_failed.append(name)
        result.students = StudentCollection()     # adhoori file ka data nahi rakhna
    return result


async def load_file_async(path):
    # file padhna blocking kaam hai, isliye alag thread mein bhej diya
    return await asyncio.to_thread(load_file, path)


async def load_all(paths):
    results = await asyncio.gather(*(load_file_async(p) for p in paths))

    merged = LoadResult()
    merged.problems = list(chain.from_iterable(r.problems for r in results))
    merged.files_ok = list(chain.from_iterable(r.files_ok for r in results))
    merged.files_failed = list(chain.from_iterable(r.files_failed for r in results))

    seen_ids = set()
    for student in chain.from_iterable(r.students for r in results):
        if student.student_id in seen_ids:
            log.warning("duplicate id %s chhod di", student.student_id)
            merged.problems.append(("merge", f"duplicate student_id {student.student_id}"))
            continue
        seen_ids.add(student.student_id)
        merged.students.add(student)
    return merged
