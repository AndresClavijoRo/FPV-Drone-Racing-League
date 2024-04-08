# ENV varaibles and configuration settings
import os

# DATABASE_URL = os.getenv("DATABASE_URL","postgresql://localhost/fpv?user=postgres&password=postgres") 
DATABASE_URL = "sqlite:///fpv.db"
SECRET_KEY = os.getenv("SECRET_KEY","this_is_the_scret")
