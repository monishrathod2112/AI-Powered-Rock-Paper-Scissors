import os

class Config:
    SECRET_KEY = "AI_RPS_SECRET_KEY"

    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(BASE_DIR, "database", "rps.db")

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # -----------------------------
    # Mail Configuration
    # -----------------------------
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True

    MAIL_USERNAME = "rathodmonish192@gmail.com"

    MAIL_PASSWORD = "hmpx cibc aqqu jbdf"

    UPLOAD_FOLDER = "static/uploads"

    MAX_CONTENT_LENGTH = 2 * 1024 * 1024