import logging
import os

# DEBUG = os.getenv("ENVIRONEMENT") == "DEV"
DEBUG = True
APPLICATION_ROOT = os.getenv("APPLICATION_APPLICATION_ROOT", "/api/")
HOST = os.getenv("APPLICATION_HOST")
PORT = int(os.getenv("APPLICATION_PORT", "3000"))
SQLALCHEMY_TRACK_MODIFICATIONS = False
SECRET_KEY = os.getenv("APPLICATION_SECRET_KEY")
IMAGE_URL = "/mnt/static/image/"

WINDOWS_EFFICIENCY_APP_API = "https://m20vpzqk-3001.asse.devtunnels.ms/excels"

DB_CONTAINER = os.getenv("APPLICATION_DB_CONTAINER", "103.175.217.118")
POSTGRES = {
    # "user": os.getenv("APPLICATION_POSTGRES_USER", "aimo"),
    "user": "postgres",
    "pw": "postgres",
    # "pw": os.getenv("APPLICATION_POSTGRES_PW", "pass123"),
    # "pw": os.getenv("APPLICATION_POSTGRES_PW", "aimo!@#"),
    "host": "192.168.1.51",
    "port": 5432,
    "db": "digital_twin",
}
DB_URI = "postgresql+psycopg2://%(user)s:%(pw)s@%(host)s:%(port)s/%(db)s" % POSTGRES


logging.basicConfig(
    filename=os.getenv("SERVICE_LOG", "server.log"),
    level=logging.DEBUG,
    format="%(levelname)s: %(asctime)s \
        pid:%(process)s module:%(module)s %(message)s",
    datefmt="%d/%m/%y %H:%M:%S",
)
