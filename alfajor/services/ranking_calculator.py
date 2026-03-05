"""Cálculo de score de ranking."""

from collections import defaultdict
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
        "score": round(score, 0),
        "shifts_completed": shifts_completed,
        "late_minutes": late_minutes,
        "absences": absences,
        "incidents": incidents,
        "breakdown": w,
    }


def build_ranking(period_start, period_end, branch_id=None, shift_role=None, preset="BALANCEADO"):
    """Construye ranking de empleados."""
    employees_query = Employee.query.filter_by(status="ACTIVO")
    if branch_id:
        employees_query = employees_query.filter_by(branch_id=branch_id)
    employees = employees_query.all()
    if not employees:
        return []

    emp_ids = [e.id for e in employees]
    weights = get_preset_weights(preset)

    shifts_query = Shift.query.filter(
        Shift.employee_id.in_(emp_ids),
        Shift.date >= period_start,
        Shift.date <= period_end,
        Shift.status == ShiftStatus.COMPLETADO.value,
    )
    if shift_role:
        shifts_query = shifts_query.filter(Shift.shift_role == shift_role)
    shifts = shifts_query.all()

    events = AttendanceEvent.query.join(Shift).filter(
        Shift.employee_id.in_(emp_ids),
        Shift.date >= period_start,
        Shift.date <= period_end,
    ).all()

    stats = defaultdict(lambda: {
        "shifts_completed": 0,
        "late_minutes": 0,
        "absences": 0,
        "incidents": 0,
        "total_hours": 0,
    })

    for s in shifts:
        stats[s.employee_id]["shifts_completed"] += 1
        hours = (s.end_time.hour * 60 + s.end_time.minute - s.start_time.hour * 60 - s.start_time.minute) / 60
        stats[s.employee_id]["total_hours"] += hours

    for e in events:
        emp_id = e.employee_id
        if e.event_type == "LATE":
            stats[emp_id]["late_minutes"] += e.minutes_late or 0
        elif e.event_type == "ABSENT":
            stats[emp_id]["absences"] += 1
        elif e.event_type == "INCIDENT":
            stats[emp_id]["incidents"] += 1

    results = []
    for emp in employees:
        data = stats.get(emp.id, {})
        score = 100
        score -= data.get("late_minutes", 0) * weights.get("w_late", 0.5)
        score -= data.get("absences", 0) * weights.get("w_absent", 10)
        score -= data.get("incidents", 0) * weights.get("w_inc", 5)
        score += data.get("shifts_completed", 0) * weights.get("w_completed", 2)
        score = max(0, min(100, score))
        results.append({
            "employee": emp,
            "score": round(score, 0),
            "total_hours": round(data.get("total_hours", 0), 0),
            "shifts_completed": data.get("shifts_completed", 0),
            "late_minutes": data.get("late_minutes", 0),
            "absences": data.get("absences", 0),
            "incidents": data.get("incidents", 0),
            "breakdown": weights,
        })
    results.sort(key=lambda x: x["score"], reverse=True)
    return results
