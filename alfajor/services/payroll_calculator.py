"""Cálculo de liquidaciones."""

from datetime import datetime
from decimal import Decimal
from alfajor.extensions import db
from alfajor.models import Shift, PayStatement, PayLine, Employee, PayPeriod
from alfajor.enums import ShiftStatus, PayLineType, ReconciliationStatus
from alfajor.services.settings_service import get_setting


def generate_statements_for_period(period_id):
    """Genera PayStatements para todos los empleados con turnos COMPLETADO en el periodo."""
    period = PayPeriod.query.get_or_404(period_id)
    employees_with_shifts = db.session.query(Shift.employee_id).filter(
        Shift.date >= period.start_date,
        Shift.date <= period.end_date,
        Shift.status == ShiftStatus.COMPLETADO.value
    ).distinct().all()
    created = []
    for (emp_id,) in employees_with_shifts:
        st = _calculate_statement(period_id, emp_id)
        if st:
            created.append(st)
    return created


def _calculate_statement(period_id, employee_id):
    """Calcula y crea/actualiza PayStatement para un empleado en un periodo."""
    period = PayPeriod.query.get(period_id)
    employee = Employee.query.get(employee_id)
    if not period or not employee:
        return None
    existing = PayStatement.query.filter_by(pay_period_id=period_id, employee_id=employee_id).first()
    if existing:
        for line in existing.lines:
            db.session.delete(line)
        db.session.delete(existing)
        db.session.flush()
    shifts = Shift.query.filter(
        Shift.employee_id == employee_id,
        Shift.date >= period.start_date,
        Shift.date <= period.end_date,
        Shift.status == ShiftStatus.COMPLETADO.value
    ).all()
    total_base = Decimal("0")
    lines_data = []
    for s in shifts:
        hours = (s.end_time.hour * 60 + s.end_time.minute - s.start_time.hour * 60 - s.start_time.minute) / 60
        amount = Decimal(str(hours)) * employee.hourly_rate
        total_base += amount
        lines_data.append((PayLineType.BASE_HOURS.value, f"Turno {s.date}", hours, float(employee.hourly_rate), amount))
    st = PayStatement(
        pay_period_id=period_id,
        employee_id=employee_id,
        total_base_hours=sum(l[2] for l in lines_data),
        total_overtime_hours=0,
        total_surcharges=0,
        total_bonuses=0,
        total_deductions=0,
        total_calculated=total_base,
        reconciliation_status=ReconciliationStatus.PENDIENTE.value,
        generated_at=datetime.utcnow(),
    )
    db.session.add(st)
    db.session.flush()
    for line_type, desc, qty, rate, amt in lines_data:
        db.session.add(PayLine(
            pay_statement_id=st.id,
            line_type=line_type,
            description=desc,
            quantity=qty,
            unit_rate=rate,
            amount=amt,
        ))
    db.session.commit()
    return st
