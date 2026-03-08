import os


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-production")
    ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")
