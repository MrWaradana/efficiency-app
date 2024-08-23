import logging
import os
from dotenv import load_dotenv

load_dotenv()
# DEBUG = os.getenv("ENVIRONEMENT") == "DEV"
DEBUG = True
APPLICATION_ROOT = os.getenv("APPLICATION_APPLICATION_ROOT", "/")
HOST = os.getenv("APPLICATION_HOST")
PORT = int(os.getenv("APPLICATION_PORT", "3000"))
SQLALCHEMY_TRACK_MODIFICATIONS = False
SECRET_KEY = os.getenv("APPLICATION_SECRET_KEY")
IMAGE_URL = "/mnt/static/image/"


WINDOWS_EFFICIENCY_APP_API = os.getenv("WINDOWS_EFFICIENCY_APP_API")
AUTH_SERVICE_API = os.getenv("AUTH_SERVICE_API")

POSTGRES = {
    "user": os.getenv("APPLICATION_POSTGRES_USER"),
    "pw": os.getenv("APPLICATION_POSTGRES_PASSWORD"),
    "host": os.getenv("APPLICATION_POSTGRES_HOST"),
    "port": os.getenv("APPLICATION_POSTGRES_PORT"),
    "db": os.getenv("APPLICATION_POSTGRES_DB"),
}

DB_URI = "postgresql+psycopg2://%(user)s:%(pw)s@%(host)s:%(port)s/%(db)s" % POSTGRES

logging.basicConfig(
    filename=os.getenv("SERVICE_LOG", "server.log"),
    level=logging.DEBUG,
    format="%(levelname)s: %(asctime)s \
        pid:%(process)s module:%(module)s %(message)s",
    datefmt="%d/%m/%y %H:%M:%S",
)
