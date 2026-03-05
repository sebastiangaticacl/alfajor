"""Cálculo de liquidaciones."""

from datetime import datetime
from decimal import Decimal
from alfajor.extensions import db
from alfajor.models import Shift, PayStatement, PayLine, Employee, PayPeriod
from alfajor.enums import ShiftStatus, PayLineType, ReconciliationStatus
from alfajor.utils.timecalc import shift_hours


def generate_statements_for_period(period_id):
    """Genera PayStatements para todos los empleados con turnos COMPLETADO en el periodo."""
    period = PayPeriod.query.get_or_404(period_id)
    shifts = Shift.query.filter(
        Shift.date >= period.start_date,
        Shift.date <= period.end_date,
        Shift.status == ShiftStatus.COMPLETADO.value
    ).all()
    if not shifts:
        return []
    employees = {e.id: e for e in Employee.query.filter(Employee.id.in_({s.employee_id for s in shifts})).all()}
    shifts_by_employee = {}
    for s in shifts:
        shifts_by_employee.setdefault(s.employee_id, []).append(s)
    created = []
    for emp_id, emp_shifts in shifts_by_employee.items():
        employee = employees.get(emp_id)
        if not employee:
            continue
        st = _calculate_statement_from_shifts(period, employee, emp_shifts)
        if st:
            created.append(st)
    return created


def _calculate_statement_from_shifts(period, employee, shifts):
    """Calcula y crea o actualiza PayStatement usando turnos ya cargados."""
    st = PayStatement.query.filter_by(pay_period_id=period.id, employee_id=employee.id).first()
    if not st:
        st = PayStatement(
            pay_period_id=period.id,
            employee_id=employee.id,
            reconciliation_status=ReconciliationStatus.PENDIENTE.value
        )
        db.session.add(st)
        db.session.flush()
    else:
        # Si ya está pagado, no recalculamos para evitar inconsistencias
        if st.reconciliation_status == ReconciliationStatus.PAGADO.value:
            return st
        # Limpiamos líneas antiguas antes de regenerar
        PayLine.query.filter_by(pay_statement_id=st.id).delete(synchronize_session=False)

    total_base = Decimal("0.00")
    lines_data = []
    for s in shifts:
        hours = shift_hours(s.start_time, s.end_time)
        rate = Decimal(str(employee.hourly_rate))
        amount = (hours * rate).quantize(Decimal("0.01"))
        total_base += amount
        lines_data.append((PayLineType.BASE_HOURS.value, f"Turno {s.date}", hours, rate, amount))

    # Actualizamos campos del statement
    st.total_base_hours = sum((l[2] for l in lines_data), Decimal("0.00"))
    st.total_calculated = total_base
    st.generated_at = datetime.utcnow()

    for line_type, desc, qty, rate, amt in lines_data:
        db.session.add(PayLine(
            pay_statement_id=st.id,
            line_type=line_type,
            description=desc,
            quantity=qty,
            unit_rate=rate,
            amount=amt,
        ))
    return st
