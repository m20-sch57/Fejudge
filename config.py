import os


class Config(object):
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'surprise!'
    MAX_CONTENT_LENGTH = 1024 * 65536

    # Max submission size
    MAX_SUBMISSION_SIZE = 1024 * 1024

    # Mail server
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = os.environ.get('MAIL_PORT') or 587
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') or True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or ''
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or ''

    # NATS server
    NATS_URL = os.environ.get('NATS_URL') or 'nats://localhost:4222'

    # Storage
    STORAGE_DIR = os.environ.get('STORAGE_DIR') or ''
    SUBMISSIONS_DOWNLOAD_PATH = os.path.join(STORAGE_DIR, 'download', 'submissions')
    PROBLEMS_UPLOAD_PATH = os.path.join(STORAGE_DIR, 'upload', 'problems')
    PROBLEMS_PATH = os.path.join(STORAGE_DIR, 'problems')

    # SQLAlchemy database
    POSTGRES_URL = os.environ.get('POSTGRES_URL') or 'localhost:5432'
    POSTGRES_USER = os.environ.get('POSTGRES_USER') or 'postgres'
    POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD') or 'postgres'
    POSTGRES_DB = os.environ.get('POSTGRES_DB') or 'database.db'
    SQLALCHEMY_DATABASE_URI = 'postgresql://{user}:{password}@{url}/{db}'.format(
        user=POSTGRES_USER, password=POSTGRES_PASSWORD, url=POSTGRES_URL, db=POSTGRES_DB)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
