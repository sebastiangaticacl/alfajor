"""
Configuración por entorno.
"""

import os
from pathlib import Path


class Config:
    """Config base."""
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-in-production")
    SESSION_COOKIE_SAMESITE = "Lax"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}


class DevelopmentConfig(Config):
    """Desarrollo: SQLite por defecto."""
    ENV = "development"
    DEBUG = True
    database_url = os.environ.get("DATABASE_URL")
    if database_url and database_url.startswith("postgresql"):
        SQLALCHEMY_DATABASE_URI = database_url
    else:
        base_dir = Path(__file__).resolve().parent.parent
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{base_dir / 'alfajor.db'}"


class ProductionConfig(Config):
    """Producción: PostgreSQL obligatorio."""
    ENV = "production"
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "postgresql://localhost/alfajor"
    )


class TestingConfig(Config):
    """Tests."""
    ENV = "testing"
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
}
