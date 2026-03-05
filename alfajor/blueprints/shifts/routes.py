"""Rutas turnos."""

from datetime import date, timedelta, time
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from alfajor.utils.decorators import encargado_or_admin
from alfajor.blueprints.shifts import bp
from alfajor.extensions import db
from alfajor.models import ScheduleWeek, Shift, Employee, Branch
from sqlalchemy.orm import selectinload
from alfajor.enums import WeekStatus, ShiftStatus
from decimal import Decimal
from alfajor.services.shift_validator import validate_shift
from alfajor.services.settings_service import get_setting
from alfajor.utils.timecalc import shift_hours


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
    shifts = Shift.query.options(selectinload(Shift.employee)).filter(
        Shift.date >= monday,
        Shift.date <= sunday
    ).order_by(Shift.date, Shift.start_time).all()
    if current_user.role in ("ADMIN", "ENCARGADO"):
        employees = Employee.query.filter_by(status="ACTIVO").order_by(Employee.last_name).all()
    else:
        employees = [current_user.employee] if current_user.employee else []
    branches = Branch.query.filter_by(active=True).all()
    week_days = [monday + timedelta(days=i) for i in range(7)]
    schedule_map = {}
    employee_hours = {}
    branch_totals = {}
    day_totals = {d.isoformat(): Decimal("0.00") for d in week_days}
    day_segments = {
        d.isoformat(): {"M": Decimal("0.00"), "T": Decimal("0.00"), "N": Decimal("0.00")}
        for d in week_days
    }
    segment_totals = {"M": Decimal("0.00"), "T": Decimal("0.00"), "N": Decimal("0.00")}

    def get_segment(start_t):
        hour = start_t.hour
        if hour < 12:
            return "M"
        if hour < 18:
            return "T"
        return "N"
    for s in shifts:
        emp_map = schedule_map.setdefault(str(s.employee_id), {})
        day_key = s.date.isoformat()
        emp_map.setdefault(day_key, []).append(s)
        hours = shift_hours(s.start_time, s.end_time)
        employee_hours[str(s.employee_id)] = employee_hours.get(str(s.employee_id), Decimal("0.00")) + hours
        day_totals[day_key] += hours
        seg = get_segment(s.start_time)
        day_segments[day_key][seg] += hours
        segment_totals[seg] += hours
        branch_id = str(s.branch_id or (s.employee.branch_id if s.employee else ""))
        branch_totals[branch_id] = branch_totals.get(branch_id, Decimal("0.00")) + hours

    shift_roles = get_setting("shift_roles", ["caja", "barra", "cocina", "runner"])
    branch_groups = {}
    for e in employees:
        key = str(e.branch_id or "")
        branch_groups.setdefault(key, {"branch": e.branch, "employees": []})
        branch_groups[key]["employees"].append(e)
    ordered_groups = sorted(
        branch_groups.values(),
        key=lambda g: (g["branch"].name if g["branch"] else "Sin sucursal")
    )

    return render_template(
        "shifts/calendar.html",
        week=week,
        shifts=shifts,
        week_days=week_days,
        schedule_map=schedule_map,
        employee_hours=employee_hours,
        branch_groups=ordered_groups,
        branch_totals=branch_totals,
        day_totals=day_totals,
        day_segments=day_segments,
        segment_totals=segment_totals,
        shift_roles=shift_roles,
        monday=monday,
        sunday=sunday,
        prev_week=(monday - timedelta(days=7)).isoformat(),
        next_week=(monday + timedelta(days=7)).isoformat(),
        employees=employees,
        branches=branches,
    )


@bp.route("/week/new", methods=["POST"])
@login_required
@encargado_or_admin
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
@encargado_or_admin
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
@encargado_or_admin
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
@encargado_or_admin
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
@encargado_or_admin
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


@bp.route("/shift/<id>/update", methods=["POST"])
@login_required
@encargado_or_admin
def shift_update(id):
    shift = Shift.query.get_or_404(id)
    current_week = shift.schedule_week
    if current_week.status == WeekStatus.CERRADA.value:
        msg = "No se pueden modificar turnos de semana cerrada."
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return {"status": "error", "message": msg}, 400
        flash(msg, "danger")
        return redirect(url_for("shifts.calendar", week=current_week.start_date.isoformat()))

    employee_id = request.form.get("employee_id") or shift.employee_id
    shift_role = request.form.get("shift_role") or shift.shift_role
    date_str = request.form.get("date")
    start_str = request.form.get("start_time")
    end_str = request.form.get("end_time")

    try:
        shift_date = date.fromisoformat(date_str) if date_str else shift.date
        if start_str:
            start_parts = start_str.split(":")
            start_time = time(int(start_parts[0]), int(start_parts[1]) if len(start_parts) > 1 else 0)
        else:
            start_time = shift.start_time
        if end_str:
            end_parts = end_str.split(":")
            end_time = time(int(end_parts[0]), int(end_parts[1]) if len(end_parts) > 1 else 0)
        else:
            end_time = shift.end_time
    except (ValueError, TypeError):
        msg = "Datos inválidos."
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return {"status": "error", "message": msg}, 400
        flash(msg, "danger")
        return redirect(url_for("shifts.calendar", week=week.start_date.isoformat()))

    monday = shift_date - timedelta(days=shift_date.weekday())
    sunday = monday + timedelta(days=6)
    target_week = ScheduleWeek.query.filter_by(start_date=monday, end_date=sunday).first()
    if not target_week:
        msg = "No existe una semana creada para esa fecha."
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return {"status": "error", "message": msg}, 400
        flash(msg, "danger")
        return redirect(url_for("shifts.calendar", week=monday.isoformat()))
    if target_week.status == WeekStatus.CERRADA.value:
        msg = "No se pueden modificar turnos de semana cerrada."
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return {"status": "error", "message": msg}, 400
        flash(msg, "danger")
        return redirect(url_for("shifts.calendar", week=monday.isoformat()))

    ok, err = validate_shift(employee_id, shift_date, start_time, end_time, exclude_shift_id=shift.id)
    if not ok:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return {"status": "error", "message": err}, 400
        flash(err, "danger")
        return redirect(url_for("shifts.calendar", week=week.start_date.isoformat()))

    shift.employee_id = employee_id
    shift.shift_role = shift_role
    shift.date = shift_date
    shift.start_time = start_time
    shift.end_time = end_time
    shift.schedule_week_id = target_week.id
    if target_week.branch_id:
        shift.branch_id = target_week.branch_id
    db.session.commit()
    msg = "Turno actualizado."
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return {"status": "success", "message": msg}
    flash(msg, "success")
    return redirect(url_for("shifts.calendar", week=target_week.start_date.isoformat()))


@bp.route("/shift/create", methods=["POST"])
@login_required
@encargado_or_admin
def shift_create():
    data = request.get_json(silent=True) or request.form
    employee_id = data.get("employee_id")
    shift_role = data.get("shift_role", "caja")
    date_str = data.get("date")
    start_str = data.get("start_time", "09:00")
    end_str = data.get("end_time", "17:00")
    try:
        shift_date = date.fromisoformat(date_str)
        start_parts = start_str.split(":")
        end_parts = end_str.split(":")
        start_time = time(int(start_parts[0]), int(start_parts[1]) if len(start_parts) > 1 else 0)
        end_time = time(int(end_parts[0]), int(end_parts[1]) if len(end_parts) > 1 else 0)
    except (ValueError, TypeError):
        return {"status": "error", "message": "Datos inválidos."}, 400
    monday = shift_date - timedelta(days=shift_date.weekday())
    sunday = monday + timedelta(days=6)
    target_week = ScheduleWeek.query.filter_by(start_date=monday, end_date=sunday).first()
    if not target_week:
        return {"status": "error", "message": "No existe una semana creada para esa fecha."}, 400
    if target_week.status == WeekStatus.CERRADA.value:
        return {"status": "error", "message": "No se pueden modificar turnos de semana cerrada."}, 400
    ok, err = validate_shift(employee_id, shift_date, start_time, end_time)
    if not ok:
        return {"status": "error", "message": err}, 400
    shift = Shift(
        schedule_week_id=target_week.id,
        employee_id=employee_id,
        shift_role=shift_role,
        date=shift_date,
        start_time=start_time,
        end_time=end_time,
        status=ShiftStatus.PLANIFICADO.value,
        branch_id=target_week.branch_id,
    )
    db.session.add(shift)
    db.session.commit()
    return {"status": "success", "shift_id": shift.id}


@bp.route("/shift/bulk-update", methods=["POST"])
@login_required
@encargado_or_admin
def shift_bulk_update():
    payload = request.get_json(silent=True) or {}
    shift_ids = payload.get("shift_ids", [])
    if not shift_ids:
        return {"status": "error", "message": "Sin turnos seleccionados."}, 400
    updates = {
        "employee_id": payload.get("employee_id"),
        "date": payload.get("date"),
        "start_time": payload.get("start_time"),
        "end_time": payload.get("end_time"),
        "shift_role": payload.get("shift_role"),
    }
    shifts = Shift.query.filter(Shift.id.in_(shift_ids)).all()
    if not shifts:
        return {"status": "error", "message": "No se encontraron turnos."}, 404

    parsed = []
    for shift in shifts:
        if shift.schedule_week.status == WeekStatus.CERRADA.value:
            return {"status": "error", "message": "No se pueden modificar turnos de semana cerrada."}, 400
        employee_id = updates["employee_id"] or shift.employee_id
        shift_role = updates["shift_role"] or shift.shift_role
        try:
            shift_date = date.fromisoformat(updates["date"]) if updates["date"] else shift.date
            if updates["start_time"]:
                start_parts = updates["start_time"].split(":")
                start_time = time(int(start_parts[0]), int(start_parts[1]) if len(start_parts) > 1 else 0)
            else:
                start_time = shift.start_time
            if updates["end_time"]:
                end_parts = updates["end_time"].split(":")
                end_time = time(int(end_parts[0]), int(end_parts[1]) if len(end_parts) > 1 else 0)
            else:
                end_time = shift.end_time
        except (ValueError, TypeError):
            return {"status": "error", "message": "Datos inválidos."}, 400
        monday = shift_date - timedelta(days=shift_date.weekday())
        sunday = monday + timedelta(days=6)
        target_week = ScheduleWeek.query.filter_by(start_date=monday, end_date=sunday).first()
        if not target_week:
            return {"status": "error", "message": "No existe una semana creada para alguna fecha."}, 400
        if target_week.status == WeekStatus.CERRADA.value:
            return {"status": "error", "message": "No se pueden modificar turnos de semana cerrada."}, 400
        ok, err = validate_shift(employee_id, shift_date, start_time, end_time, exclude_shift_id=shift.id)
        if not ok:
            return {"status": "error", "message": err}, 400
        parsed.append((shift, employee_id, shift_role, shift_date, start_time, end_time, target_week))

    for shift, employee_id, shift_role, shift_date, start_time, end_time, target_week in parsed:
        shift.employee_id = employee_id
        shift.shift_role = shift_role
        shift.date = shift_date
        shift.start_time = start_time
        shift.end_time = end_time
        shift.schedule_week_id = target_week.id
        if target_week.branch_id:
            shift.branch_id = target_week.branch_id
    db.session.commit()
    return {"status": "success", "message": "Turnos actualizados."}
