"""Rutas turnos."""

from datetime import date, timedelta, time
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from alfajor.blueprints.shifts import bp
from alfajor.extensions import db
from alfajor.models import ScheduleWeek, Shift, Employee, Branch
from alfajor.enums import WeekStatus, ShiftStatus
from alfajor.services.shift_validator import validate_shift


@bp.route("/")
@login_required
def calendar():
    week_str = request.args.get("week")
    if week_str:
        try:
            base = date.fromisoformat(week_str)
        except ValueError:
            base = date.today()
    else:
        base = date.today()
    monday = base - timedelta(days=base.weekday())
    sunday = monday + timedelta(days=6)
    week = ScheduleWeek.query.filter(
        ScheduleWeek.start_date == monday,
        ScheduleWeek.end_date == sunday
    ).first()
    shifts = Shift.query.filter(
        Shift.date >= monday,
        Shift.date <= sunday
    ).order_by(Shift.date, Shift.start_time).all() if week else []
    employees = Employee.query.filter_by(status="ACTIVO").order_by(Employee.last_name).all()
    branches = Branch.query.filter_by(active=True).all()
    return render_template(
        "shifts/calendar.html",
        week=week,
        shifts=shifts,
        monday=monday,
        sunday=sunday,
        prev_week=(monday - timedelta(days=7)).isoformat(),
        next_week=(monday + timedelta(days=7)).isoformat(),
        employees=employees,
        branches=branches,
    )


@bp.route("/week/new", methods=["POST"])
@login_required
def week_new():
    start = request.form.get("start_date")
    if not start:
        flash("Fecha requerida.", "danger")
        return redirect(url_for("shifts.calendar"))
    try:
        monday = date.fromisoformat(start)
    except ValueError:
        flash("Fecha inválida.", "danger")
        return redirect(url_for("shifts.calendar"))
    if monday.weekday() != 0:
        monday = monday - timedelta(days=monday.weekday())
    sunday = monday + timedelta(days=6)
    if ScheduleWeek.query.filter_by(start_date=monday).first():
        flash("Ya existe una semana para esas fechas.", "warning")
        return redirect(url_for("shifts.calendar", week=monday.isoformat()))
    week = ScheduleWeek(
        start_date=monday, end_date=sunday,
        status=WeekStatus.BORRADOR.value,
        created_by=current_user.id
    )
    db.session.add(week)
    db.session.commit()
    flash("Semana creada.", "success")
    return redirect(url_for("shifts.calendar", week=monday.isoformat()))


@bp.route("/week/<id>/publish", methods=["POST"])
@login_required
def week_publish(id):
    from datetime import datetime
    week = ScheduleWeek.query.get_or_404(id)
    week.status = WeekStatus.PUBLICADA.value
    week.published_at = datetime.utcnow()
    db.session.commit()
    flash("Semana publicada.", "success")
    return redirect(url_for("shifts.calendar", week=week.start_date.isoformat()))


@bp.route("/week/<id>/close", methods=["POST"])
@login_required
def week_close(id):
    from datetime import datetime
    week = ScheduleWeek.query.get_or_404(id)
    week.status = WeekStatus.CERRADA.value
    week.closed_at = datetime.utcnow()
    db.session.commit()
    flash("Semana cerrada.", "success")
    return redirect(url_for("shifts.calendar", week=week.start_date.isoformat()))


@bp.route("/shift/new", methods=["POST"])
@login_required
def shift_new():
    try:
        shift_date = date.fromisoformat(request.form.get("date"))
        start = request.form.get("start_time", "09:00").split(":")
        end = request.form.get("end_time", "17:00").split(":")
        start_time = time(int(start[0]), int(start[1]) if len(start) > 1 else 0)
        end_time = time(int(end[0]), int(end[1]) if len(end) > 1 else 0)
    except (ValueError, TypeError):
        flash("Datos inválidos.", "danger")
        return redirect(url_for("shifts.calendar"))
    employee_id = request.form.get("employee_id")
    shift_role = request.form.get("shift_role", "caja")
    week_id = request.form.get("week_id")
    if not employee_id or not week_id:
        flash("Empleado y semana requeridos.", "danger")
        return redirect(url_for("shifts.calendar"))
    week = ScheduleWeek.query.get_or_404(week_id)
    if week.status == WeekStatus.CERRADA.value:
        flash("No se pueden agregar turnos a semana cerrada.", "danger")
        return redirect(url_for("shifts.calendar"))
    ok, err = validate_shift(employee_id, shift_date, start_time, end_time)
    if not ok:
        flash(err, "danger")
        return redirect(url_for("shifts.calendar", week=week.start_date.isoformat()))
    shift = Shift(
        schedule_week_id=week_id,
        employee_id=employee_id,
        shift_role=shift_role,
        date=shift_date,
        start_time=start_time,
        end_time=end_time,
        status=ShiftStatus.PLANIFICADO.value,
    )
    db.session.add(shift)
    db.session.commit()
    flash("Turno creado.", "success")
    return redirect(url_for("shifts.calendar", week=week.start_date.isoformat()))


@bp.route("/shift/<id>/delete", methods=["POST"])
@login_required
def shift_delete(id):
    shift = Shift.query.get_or_404(id)
    week_start = shift.schedule_week.start_date
    if shift.schedule_week.status == WeekStatus.CERRADA.value:
        flash("No se pueden modificar turnos de semana cerrada.", "danger")
        return redirect(url_for("shifts.calendar", week=week_start.isoformat()))
    db.session.delete(shift)
    db.session.commit()
    flash("Turno eliminado.", "success")
    return redirect(url_for("shifts.calendar", week=week_start.isoformat()))
