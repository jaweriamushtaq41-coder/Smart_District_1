# Settings .env file se aati hain (secret code mein nahi likhe)
import os

from dotenv import load_dotenv

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Settings:
    def __init__(self):
        load_dotenv(os.path.join(ROOT, ".env"))

        self.admin_token = os.getenv("ADMIN_TOKEN", "")
        self.fine_per_day = float(os.getenv("FINE_PER_DAY", "50"))
        self.log_level = os.getenv("LOG_LEVEL", "INFO").upper()

        self.data_dir = os.path.join(ROOT, os.getenv("DATA_DIR", "data"))
        self.report_dir = os.path.join(ROOT, os.getenv("REPORT_DIR", "reports"))
        self.log_file = os.path.join(ROOT, os.getenv("LOG_FILE", "logs/portal.log"))

        # in files ka hona zaroori hai, na milein to "missing" report hogi
        names = os.getenv("EXPECTED_FILES", "").split(",")
        self.expected_files = [n.strip() for n in names if n.strip()]
