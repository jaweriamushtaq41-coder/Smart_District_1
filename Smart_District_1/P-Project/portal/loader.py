"""CSV loading: safe file handling, generators, asyncio (Days 2, 6, 10)."""
import asyncio
import csv
import itertools
import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from .exceptions import CorruptFileError, InvalidRecordError
from .models import LEVELS

log = logging.getLogger("portal.loader")
REQUIRED = {"student_id", "name", "level", "department", "marks", "fee_due", "fee_paid"}


@dataclass
class LoadResult:
    students: list = field(default_factory=list)
    errors: list = field(default_factory=list)       # (source, message)
    files_ok: list = field(default_factory=list)
    files_failed: list = field(default_factory=list)


def _parse_date(text):
    return datetime.strptime(text.strip(), "%Y-%m-%d").date()


def parse_row(row: dict, line_no: int):
    """Validate one row and return a Student object, or raise InvalidRecordError."""
    try:
        student_id = row["student_id"].strip()
        if not student_id:
            raise InvalidRecordError("empty student_id")
        cls = LEVELS.get(row["level"].strip().upper())
        if cls is None:
            raise InvalidRecordError(f"unknown level {row['level']!r}")
        paid_raw = (row["fee_paid"] or "").strip()
        return cls(
            student_id,
            row["name"].strip().title(),
            row["department"].strip().upper(),
            float(row["marks"]),
            _parse_date(row["fee_due"]),
            _parse_date(paid_raw) if paid_raw else None,
        )
    except InvalidRecordError as exc:
        raise InvalidRecordError(f"line {line_no}: {exc}") from exc
    except (ValueError, TypeError, KeyError, AttributeError) as exc:
        raise InvalidRecordError(f"line {line_no}: {exc}") from exc


def iter_students(path: Path, errors: list):
    """Generator: yields one valid Student at a time (never loads whole file)."""
    with open(path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        if not reader.fieldnames or not REQUIRED <= set(reader.fieldnames):
            raise CorruptFileError("missing/invalid header row")
        for line_no, row in enumerate(reader, start=2):
            try:
                yield parse_row(row, line_no)
            except InvalidRecordError as exc:
                log.warning("%s: skipped row - %s", path.name, exc)
                errors.append((path.name, str(exc)))


def load_file(path) -> LoadResult:
    """Read one file safely. Never raises: every failure is logged and recorded."""
    path = Path(path)
    result = LoadResult()
    try:
        result.students = list(iter_students(path, result.errors))
    except FileNotFoundError:
        msg = "file not found"
    except (UnicodeDecodeError, csv.Error) as exc:
        msg = f"corrupt file ({type(exc).__name__})"
    except CorruptFileError as exc:
        msg = f"corrupt file ({exc})"
    except OSError as exc:
        msg = f"cannot read file ({exc})"
    else:
        result.files_ok.append(path.name)
        log.info("%s: loaded %d students", path.name, len(result.students))
        return result
    finally:
        log.debug("finished processing %s", path.name)
    log.error("%s: %s", path.name, msg)
    result.errors.append((path.name, msg))
    result.files_failed.append(path.name)
    result.students = []
    return result


async def load_file_async(path) -> LoadResult:
    return await asyncio.to_thread(load_file, path)       # blocking IO in a worker thread


async def load_all(paths) -> LoadResult:
    """Load every file concurrently, merge results, drop duplicate IDs."""
    results = await asyncio.gather(*(load_file_async(p) for p in paths))
    merged = LoadResult(
        students=[],
        errors=list(itertools.chain.from_iterable(r.errors for r in results)),
        files_ok=list(itertools.chain.from_iterable(r.files_ok for r in results)),
        files_failed=list(itertools.chain.from_iterable(r.files_failed for r in results)),
    )
    seen = set()
    for student in itertools.chain.from_iterable(r.students for r in results):
        if student.student_id in seen:
            log.warning("duplicate student_id %s ignored", student.student_id)
            merged.errors.append(("merge", f"duplicate student_id {student.student_id}"))
            continue
        seen.add(student.student_id)
        merged.students.append(student)
    return merged
