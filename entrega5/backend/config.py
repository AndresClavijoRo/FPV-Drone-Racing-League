# ENV varaibles and configuration settings
import os
from dotenv import load_dotenv

try:
    load_dotenv(".env")
except Exception:
    pass

DATABASSE_USER = os.getenv("DATABASE_USER", "ifpv_user")
DATABASE_PASS = os.getenv("DATABASE_PASS", "ifpv_pass")
DATABASE_SERVER = os.getenv("DATABASE_SERVER", "localhost:5432/backend_ifpv")

DATABASE_URL = f"postgresql://{DATABASSE_USER}:{DATABASE_PASS}@{DATABASE_SERVER}"
SECRET_KEY = os.getenv("SECRET_KEY", "this_is_the_scret")
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "db+sqlite:///celery_results.sqlite")
ROOT_SERVER_URL = os.getenv("ROOT_SERVER_URL", "http://localhost:5000")
HOURS_TO_EXPIRE = int(os.getenv("HOURS_TO_EXPIRE", "24"))
GOOGLE_STORAGE_BUCKET = os.getenv("GOOGLE_STORAGE_BUCKET", "fpv-videos-grupo-6")
URL_HOURS_TO_EXPIRE = int(os.getenv("URL_HOURS_TO_EXPIRE", "1"))

# Pub/Sub
PUB_TOPIC_NAME = os.getenv("PUB_TOPIC_NAME", "projects/elated-coil-323901/topics/task_processing")
SUB_NAME=os.getenv("SUB_NAME", "projects/elated-coil-323901/subscriptions/task_processing")
AS_WORKER = os.getenv("AS_WORKER", "True")