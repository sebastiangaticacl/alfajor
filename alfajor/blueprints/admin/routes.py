"""Rutas admin."""

from datetime import date, timedelta
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from alfajor.utils.decorators import admin_required
from alfajor.blueprints.admin import bp
from alfajor.blueprints.admin.forms import UserForm
from alfajor.extensions import db
from alfajor.models import User, Employee, ScheduleWeek, Shift, PayPeriod, PayStatement, ShiftRequest


@bp.route("/")
@login_required
def dashboard():
    today = date.today()
    monday = today - timedelta(days=today.weekday())
    sunday = monday + timedelta(days=6)
    shifts_today = Shift.query.filter(Shift.date == today, Shift.status != "ANULADO").all()
    total_today = len(shifts_today)
    covered_today = sum(1 for s in shifts_today if s.status == "COMPLETADO")
    weeks = ScheduleWeek.query.order_by(ScheduleWeek.start_date.desc()).limit(5).all()
    draft_weeks = sum(1 for w in weeks if w.status == "BORRADOR")
    published_weeks = sum(1 for w in weeks if w.status == "PUBLICADA")
    closed_weeks = sum(1 for w in weeks if w.status == "CERRADA")
    periods = PayPeriod.query.filter(PayPeriod.status.in_(["ABIERTO", "EN_REVISION"])).all()
    pending_requests = ShiftRequest.query.filter_by(status="PENDIENTE").count()
    return render_template(
        "admin/dashboard.html",
        total_today=total_today,
        covered_today=covered_today,
        weeks=weeks,
        draft_weeks=draft_weeks,
        published_weeks=published_weeks,
        closed_weeks=closed_weeks,
        periods=periods,
        pending_requests=pending_requests,
    )


@bp.route("/users")
@login_required
@admin_required
def users():
    users_list = User.query.order_by(User.email).all()
    return render_template("admin/users.html", users=users_list)


@bp.route("/users/new", methods=["GET", "POST"])
@login_required
@admin_required
def user_new():
    form = UserForm()
    form.employee_id.choices = [("", "— Sin vincular")] + [
        (e.id, e.full_name) for e in Employee.query.order_by(Employee.last_name).all()
    ]
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            flash("Ya existe un usuario con ese email.", "danger")
            return render_template("admin/user_form.html", form=form, user=None)
        user = User(
            email=form.email.data,
            role=form.role.data,
            employee_id=form.employee_id.data or None,
            active=form.active.data,
        )
        if form.password.data:
            user.set_password(form.password.data)
        else:
            flash("Debes indicar una contraseña.", "danger")
            return render_template("admin/user_form.html", form=form, user=None)
        db.session.add(user)
        db.session.commit()
        flash("Usuario creado.", "success")
        return redirect(url_for("admin.users"))
    return render_template("admin/user_form.html", form=form, user=None)


@bp.route("/users/<id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def user_edit(id):
    user = User.query.get_or_404(id)
    form = UserForm(obj=user)
    form.employee_id.choices = [("", "— Sin vincular")] + [
        (e.id, e.full_name) for e in Employee.query.order_by(Employee.last_name).all()
    ]
    if form.validate_on_submit():
        other = User.query.filter(User.email == form.email.data, User.id != id).first()
        if other:
            flash("Ya existe otro usuario con ese email.", "danger")
            return render_template("admin/user_form.html", form=form, user=user)
        user.email = form.email.data
        user.role = form.role.data
        user.employee_id = form.employee_id.data or None
        user.active = form.active.data
        if form.password.data:
            user.set_password(form.password.data)
        db.session.commit()
        flash("Usuario actualizado.", "success")
        return redirect(url_for("admin.users"))
    return render_template("admin/user_form.html", form=form, user=user)


@bp.route("/users/<id>/delete", methods=["POST"])
@login_required
@admin_required
def user_delete(id):
    user = User.query.get_or_404(id)
    if user.id == current_user.id:
        flash("No puedes eliminarte a ti mismo.", "danger")
        return redirect(url_for("admin.users"))
    db.session.delete(user)
    db.session.commit()
    flash("Usuario eliminado.", "success")
    return redirect(url_for("admin.users"))
