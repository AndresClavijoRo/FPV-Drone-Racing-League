# ENV varaibles and configuration settings
import os

# DATABASE_URL = os.getenv("DATABASE_URL","postgresql://localhost/fpv?user=postgres&password=postgres") 
DATABASE_URL = "sqlite:///fpv.db"
SECRET_KEY = os.getenv("SECRET_KEY","this_is_the_scret")
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL","redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND","redis://localhost:6379/0")