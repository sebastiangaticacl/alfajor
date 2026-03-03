"""Validaciones de turnos."""

from datetime import time, date
from alfajor.models import Shift, Employee, Availability
from alfajor.services.settings_service import get_setting


def validate_no_overlap(employee_id, date_val, start_time, end_time, exclude_shift_id=None):
    """Verifica que no haya solapamiento con otros turnos del empleado."""
    q = Shift.query.filter(
        Shift.employee_id == employee_id,
        Shift.date == date_val,
        Shift.status != "ANULADO"
    )
    if exclude_shift_id:
        q = q.filter(Shift.id != exclude_shift_id)
    for s in q.all():
        if _times_overlap(start_time, end_time, s.start_time, s.end_time):
            return False, f"Solapamiento con turno existente"
    return True, None


def _times_overlap(a_start, a_end, b_start, b_end):
    return a_start < b_end and b_start < a_end


def validate_availability(employee_id, day_of_week, start_time, end_time):
    """Verifica disponibilidad del empleado."""
    avail = Availability.query.filter_by(
        employee_id=employee_id,
        day_of_week=day_of_week,
        is_available=True
    ).first()
    if not avail:
        return True, None  # Sin restricción
    if avail.start_time is None:
        return True, None
    if start_time < avail.start_time or end_time > avail.end_time:
        return False, "Fuera de horario de disponibilidad"
    return True, None


def validate_weekly_hours(employee_id, week_start, new_hours, exclude_shift_id=None):
    """Verifica máximo de horas semanales."""
    from datetime import timedelta
    max_h = get_setting("rules.max_weekly_hours", 48)
    week_end = week_start + timedelta(days=6)
    q = Shift.query.filter(
        Shift.employee_id == employee_id,
        Shift.date >= week_start,
        Shift.date <= week_end,
        Shift.status != "ANULADO"
    )
    if exclude_shift_id:
        q = q.filter(Shift.id != exclude_shift_id)
    shifts = q.all()
    total = sum(
        (s.end_time.hour * 60 + s.end_time.minute - s.start_time.hour * 60 - s.start_time.minute) / 60
        for s in shifts
    )
    total += new_hours
    if total > max_h:
        return False, f"Máximo {max_h}h semanales"
    return True, None


def validate_shift(employee_id, date_val, start_time, end_time, exclude_shift_id=None):
    """Valida un turno completo."""
    ok, err = validate_no_overlap(employee_id, date_val, start_time, end_time, exclude_shift_id)
    if not ok:
        return ok, err
    dow = date_val.weekday()
    ok, err = validate_availability(employee_id, dow, start_time, end_time)
    if not ok:
        return ok, err
    hours = (end_time.hour * 60 + end_time.minute - start_time.hour * 60 - start_time.minute) / 60
    from datetime import timedelta
    week_start = date_val - timedelta(days=date_val.weekday())
    ok, err = validate_weekly_hours(employee_id, week_start, hours, exclude_shift_id)
    if not ok:
        return ok, err
    return True, None
