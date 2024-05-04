# ENV varaibles and configuration settings
import os
from dotenv import load_dotenv

try:
    load_dotenv(".env")
except Exception:
    pass

DATABASSE_USER = os.getenv("DATABASE_USER", "postgres")
DATABASE_PASS = os.getenv("DATABASE_PASS", "postgres")
DATABASE_SERVER = os.getenv("DATABASE_SERVER", "localhost:5432/backend_ifpv")

DATABASE_URL = f"postgresql://{DATABASSE_USER}:{DATABASE_PASS}@{DATABASE_SERVER}"
# DATABASE_URL = "sqlite:///fpv.db"
SECRET_KEY = os.getenv("SECRET_KEY", "this_is_the_scret")
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.getenv(
    "CELERY_RESULT_BACKEND", "db+sqlite:///celery_results.sqlite"
)
ROOT_SERVER_URL = os.getenv("ROOT_SERVER_URL", "http://localhost:5000")
HOURS_TO_EXPIRE = int(os.getenv("HOURS_TO_EXPIRE", "24"))
UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "uploads")
