"""Rutas de autenticación."""

from flask import render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from alfajor.blueprints.auth import bp
from alfajor.blueprints.auth.forms import LoginForm
from alfajor.models import User


@bp.route("/iniciar-sesion", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.strip()).first()
        if user and user.check_password(form.password.data):
            if not user.active:
                flash("Usuario inactivo.", "danger")
            else:
                login_user(user, remember=form.remember.data)
                return redirect(url_for("admin.dashboard"))
        else:
            flash("Usuario o contraseña incorrectos.", "danger")
    return render_template("auth/login.html", form=form)


@bp.route("/cerrar-sesion", methods=["POST"])
@login_required
def logout():
    logout_user()
    flash("Sesión cerrada.", "info")
    return redirect(url_for("auth.login"))
