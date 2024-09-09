import logging
import os
from enum import Enum

import pytz
from dotenv import load_dotenv

load_dotenv()


class EnvironmentType(str, Enum):
    DEVELOPMENT = "development"
    PRODUCTION = "production"
    TEST = "test"


class Config:
    DEBUG: int = 1
    DEFAULT_LOCALE: str = "en_US"
    ENVIRONMENT: str = EnvironmentType.DEVELOPMENT
    TIMEZONE = pytz.timezone("Asia/Bangkok")

    APPLICATION_ROOT = os.getenv("APPLICATION_APPLICATION_ROOT", "/")
    HOST = os.getenv("APPLICATION_HOST")
    PORT = os.getenv("APPLICATION_PORT", "3000")

    POSTGRES = {
        "user": os.getenv("APPLICATION_POSTGRES_USER"),
        "pw": os.getenv("APPLICATION_POSTGRES_PASSWORD"),
        "host": os.getenv("APPLICATION_POSTGRES_HOST"),
        "port": os.getenv("APPLICATION_POSTGRES_PORT"),
        "db": os.getenv("APPLICATION_POSTGRES_DB"),
    }

    DB_URI: str = (
        "postgresql+psycopg2://%(user)s:%(pw)s@%(host)s:%(port)s/%(db)s" % POSTGRES
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    REDIS_URL: str = "redis://192.168.1.51:6379/7"
    RELEASE_VERSION: str = "0.1"
    SHOW_SQL_ALCHEMY_QUERIES: int = 0
    SECRET_KEY = os.getenv("APPLICATION_SECRET_KEY")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60 * 24
    CELERY_BROKER_URL: str = "amqp://rabbit:password@localhost:5672"
    CELERY_BACKEND_URL: str = "redis://localhost:6379/0"
    WINDOWS_EFFICIENCY_APP_API = os.getenv("WINDOWS_EFFICIENCY_APP_API")
    AUTH_SERVICE_API = os.getenv("AUTH_SERVICE_API")


logging.basicConfig(
    filename=os.getenv("SERVICE_LOG", "server.log"),
    level=logging.DEBUG,
    format="%(levelname)s: %(asctime)s \
        pid:%(process)s module:%(module)s %(message)s",
    datefmt="%d/%m/%y %H:%M:%S",
)

config: Config = Config()
