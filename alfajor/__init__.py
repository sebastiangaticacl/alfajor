"""
ALFAJOR - Sistema de Turnos del Café Cosas Ricas
Desarrollado por Seba Gatica · 2026
"""

from flask import Flask, redirect, url_for
from typing import Optional


def create_app(config_name: Optional[str] = None) -> Flask:
    """Factory de aplicación Flask."""
    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static",
    )

    # Configuración
    from alfajor.config import config
    env = config_name or "development"
    app.config.from_object(config[env])

    # Extensiones
    from alfajor.extensions import db, login_manager, migrate
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    # Modelos (para migraciones)
    import alfajor.models  # noqa: F401

    # Login manager
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Debes iniciar sesión para acceder."

    @login_manager.user_loader
    def load_user(user_id):
        from alfajor.models import User
        return User.query.get(user_id)

    # Blueprints
    from alfajor.blueprints.auth import bp as auth_bp
    from alfajor.blueprints.admin import bp as admin_bp
    from alfajor.blueprints.shifts import bp as shifts_bp
    from alfajor.blueprints.employees import bp as employees_bp
    from alfajor.blueprints.requests import bp as requests_bp
    from alfajor.blueprints.payroll import bp as payroll_bp
    from alfajor.blueprints.ranking import bp as ranking_bp
    from alfajor.blueprints.settings import bp as settings_bp
    from alfajor.blueprints.reports import bp as reports_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(shifts_bp)
    app.register_blueprint(employees_bp)
    app.register_blueprint(requests_bp)
    app.register_blueprint(payroll_bp)
    app.register_blueprint(ranking_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(reports_bp)

    # Filtro template para JSON
    import json
    @app.template_filter("json_dumps")
    def json_dumps_filter(val):
        if val is None:
            return ""
        if isinstance(val, str):
            return val
        return json.dumps(val, ensure_ascii=False)

    # Ruta raíz → dashboard o login
    @app.route("/")
    def index():
        from flask_login import current_user
        if current_user.is_authenticated:
            return redirect(url_for("admin.dashboard"))
        return redirect(url_for("auth.login"))

    return app
