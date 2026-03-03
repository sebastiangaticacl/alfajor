"""Cálculo de score de ranking."""

from decimal import Decimal
from alfajor.models import Shift, AttendanceEvent, Employee, PerformanceSnapshot, PayPeriod
from alfajor.enums import ShiftStatus, ScorePreset
from alfajor.services.settings_service import get_setting


def get_preset_weights(preset="BALANCEADO"):
    defaults = {
        "BALANCEADO": {"w_late": 0.5, "w_absent": 10, "w_inc": 5, "w_completed": 2},
        "PUNTUALIDAD": {"w_late": 2, "w_absent": 15, "w_inc": 8, "w_completed": 1},
        "ESTABILIDAD": {"w_late": 0.3, "w_absent": 20, "w_inc": 3, "w_completed": 3},
    }
    config = get_setting("ranking.presets", {})
    if isinstance(config, dict) and preset in config:
        return config[preset]
    return defaults.get(preset, defaults["BALANCEADO"])


def calculate_score(employee_id, period_start, period_end, preset="BALANCEADO"):
    """Calcula score para un empleado en un periodo."""
    w = get_preset_weights(preset)
    shifts_completed = Shift.query.filter(
        Shift.employee_id == employee_id,
        Shift.date >= period_start,
        Shift.date <= period_end,
        Shift.status == ShiftStatus.COMPLETADO.value,
    ).count()
    events = AttendanceEvent.query.join(Shift).filter(
        Shift.employee_id == employee_id,
        Shift.date >= period_start,
        Shift.date <= period_end,
    ).all()
    late_minutes = sum(e.minutes_late or 0 for e in events if e.event_type == "LATE")
    absences = sum(1 for e in events if e.event_type == "ABSENT")
    incidents = sum(1 for e in events if e.event_type == "INCIDENT")
    score = 100
    score -= late_minutes * w.get("w_late", 0.5)
    score -= absences * w.get("w_absent", 10)
    score -= incidents * w.get("w_inc", 5)
    score += shifts_completed * w.get("w_completed", 2)
    score = max(0, min(100, score))
    return {
        "score": round(score, 2),
        "shifts_completed": shifts_completed,
        "late_minutes": late_minutes,
        "absences": absences,
        "incidents": incidents,
        "breakdown": w,
    }


def build_ranking(period_start, period_end, branch_id=None, shift_role=None, preset="BALANCEADO"):
    """Construye ranking de empleados."""
    from alfajor.extensions import db
    employees = Employee.query.filter_by(status="ACTIVO")
    if branch_id:
        employees = employees.filter_by(branch_id=branch_id)
    results = []
    for emp in employees.all():
        data = calculate_score(emp.id, period_start, period_end, preset)
        shifts = Shift.query.filter(
            Shift.employee_id == emp.id,
            Shift.date >= period_start,
            Shift.date <= period_end,
            Shift.status == ShiftStatus.COMPLETADO.value,
        )
        if shift_role:
            shifts = shifts.filter(Shift.shift_role == shift_role)
        total_hours = sum(
            (s.end_time.hour * 60 + s.end_time.minute - s.start_time.hour * 60 - s.start_time.minute) / 60
            for s in shifts.all()
        )
        results.append({
            "employee": emp,
            "score": data["score"],
            "total_hours": round(total_hours, 2),
            **data,
        })
    results.sort(key=lambda x: x["score"], reverse=True)
    return results
