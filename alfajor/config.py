"""
Configuración por entorno.
"""

import os
from pathlib import Path


class Config:
    """Config base."""
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-in-production")
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_HTTPONLY = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}


class DevelopmentConfig(Config):
    """Desarrollo: SQLite por defecto."""
    ENV = "development"
    DEBUG = True
    base_dir = Path(__file__).resolve().parent.parent
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    if not SQLALCHEMY_DATABASE_URI:
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{base_dir / 'alfajor.db'}"
    elif SQLALCHEMY_DATABASE_URI.startswith("sqlite:///") and not SQLALCHEMY_DATABASE_URI.startswith("sqlite:////"):
        # Ruta relativa -> absoluta para evitar problemas con cwd
        rel_path = SQLALCHEMY_DATABASE_URI.replace("sqlite:///", "")
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{base_dir / rel_path}"


class ProductionConfig(Config):
    """Producción: PostgreSQL obligatorio."""
    ENV = "production"
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
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
