# Apne custom errors. Sab PortalError se bante hain taake main.py mein ek hi except se pakad sakein.

class PortalError(Exception):
    pass


class InvalidRecordError(PortalError):
    """CSV ki ek row ka data galat hai"""


class CorruptFileError(PortalError):
    """Poori file kharab hai ya header theek nahi"""


class AccessDeniedError(PortalError):
    """Role ko ye kaam karne ki ijazat nahi"""


class StudentNotFoundError(PortalError):
    """Naam se search kiya magar student nahi mila"""
