"""Rutas de autenticación."""

from flask import render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from alfajor.blueprints.auth import bp
from alfajor.blueprints.auth.forms import LoginForm
from alfajor.models import User


@bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # Modo demo: acepta cualquier dato y entra como admin
        admin = User.query.filter_by(email="admin").first()
        if admin:
            login_user(admin, remember=form.remember.data)
            return redirect(url_for("admin.dashboard"))
        flash("Demo no disponible.", "danger")
    return render_template("auth/login.html", form=form)


@bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Sesión cerrada.", "info")
    return redirect(url_for("auth.login"))
