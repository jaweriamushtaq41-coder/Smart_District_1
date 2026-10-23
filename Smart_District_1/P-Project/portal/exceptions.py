"""Custom exception hierarchy (Day 2: raise + custom exception classes)."""


class PortalError(Exception):
    """Base class for every portal-specific error."""


class InvalidRecordError(PortalError):
    """A single CSV row has invalid data."""


class CorruptFileError(PortalError):
    """A whole CSV file is unreadable or has the wrong structure."""


class AccessDeniedError(PortalError):
    """The current role is not allowed to run an action."""


class StudentNotFoundError(PortalError):
    """Search did not find the requested student."""
