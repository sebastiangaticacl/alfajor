"""Validaciones de turnos."""

from datetime import time, date
from alfajor.models import Shift, Employee, Availability
from alfajor.services.settings_service import get_setting


def validate_no_overlap(employee_id, date_val, start_time, end_time, exclude_shift_id=None):
    """Verifica que no haya solapamiento con otros turnos del empleado.
    Busca turnos en el día anterior, actual y siguiente para cubrir cruce de medianoche.
    """
    from datetime import timedelta
    # Rango de fechas a buscar para cubrir posibles cruces de medianoche
    search_dates = [date_val - timedelta(days=1), date_val, date_val + timedelta(days=1)]

    # Datos del nuevo turno: si cruza medianoche (end <= start)
    is_midnight = end_time <= start_time

    shifts = Shift.query.filter(
        Shift.employee_id == employee_id,
        Shift.date.in_(search_dates),
        Shift.status != "ANULADO"
    )
    if exclude_shift_id:
        shifts = shifts.filter(Shift.id != exclude_shift_id)

    for s in shifts.all():
        # Lógica de solapamiento manual para manejar fechas y horas
        # Turno A (Existente): s.date, s.start_time, s.end_time
        # Turno B (Nuevo): date_val, start_time, end_time

        # Normalizamos a "minutos desde el inicio de search_dates[0]"
        def to_abs_min(d, t):
            base = search_dates[0]
            days = (d - base).days
            return days * 1440 + t.hour * 60 + t.minute

        a_start = to_abs_min(s.date, s.start_time)
        a_end = to_abs_min(s.date, s.end_time)
        if s.end_time <= s.start_time: a_end += 1440

        b_start = to_abs_min(date_val, start_time)
        b_end = to_abs_min(date_val, end_time)
        if is_midnight: b_end += 1440

        if a_start < b_end and b_start < a_end:
            return False, f"Solapamiento con turno el {s.date.strftime('%d/%m')} ({s.start_time.strftime('%H:%M')}-{s.end_time.strftime('%H:%M')})"

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
    from alfajor.utils.timecalc import shift_hours
    total = sum(shift_hours(s.start_time, s.end_time) for s in shifts)
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
    from alfajor.utils.timecalc import shift_hours
    hours = shift_hours(start_time, end_time)
    from datetime import timedelta
    week_start = date_val - timedelta(days=date_val.weekday())
    ok, err = validate_weekly_hours(employee_id, week_start, hours, exclude_shift_id)
    if not ok:
        return ok, err
    return True, None
