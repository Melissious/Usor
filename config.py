import os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path, verbose=True)


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY")
    TOKEN_KEY = os.environ.get("TOKEN_KEY") or SECRET_KEY
    TOTP_KEY = os.environ.get("TOTP_KEY")

    MONGODB_SETTINGS = {
        'db': 'test',
        'host': 'localhost',
        'port': 27017
    }
    CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL")
    CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND")

    MAIL_SERVER = "localhost"
    MAIL_PORT = 1025
    MAIL_USERNAME = None
    MAIL_PASSWORD = None
    MAIL_DEFAULT_SENDER = "admin@localhost.loc"


class Development(Config):
    pass


class Production(Config):
    pass


class Testing(Config):
    pass


config = {
    "default": Development,
    "development": Development,
    "production": Production,
    "testing": Testing
}
