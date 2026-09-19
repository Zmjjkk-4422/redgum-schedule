"""Application configuration, selected by the FLASK_CONFIG environment variable.

Profiles: dev (default), test, production. All settings that vary between
environments live here or in a local .env file so the same code runs in every
environment (configuration management for ISYS3001 Assessment 2).
"""
import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-secret-change-before-production")
    DATABASE = os.getenv("DATABASE", os.path.join("instance", "redgum.db"))
    # Redgum business rule: sessions are 60 or 90 minutes.
    SESSION_LENGTHS = (60, 90)


class DevConfig(Config):
    DEBUG = True


class TestConfig(Config):
    TESTING = True


class ProductionConfig(Config):
    DEBUG = False


config = {
    "dev": DevConfig,
    "test": TestConfig,
    "production": ProductionConfig,
}
