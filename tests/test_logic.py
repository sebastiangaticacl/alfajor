import pytest
from datetime import date, time
from alfajor.services.shift_validator import validate_shift, validate_no_overlap
from alfajor.utils.timecalc import shift_hours
from alfajor.models import Shift, PayStatement, Employee, PayPeriod
from alfajor.enums import ShiftStatus, ReconciliationStatus
from alfajor.extensions import db

@pytest.fixture
def db_session(app):
    with app.app_context():
        yield db

@pytest.fixture
def employee(db_session):
    emp = Employee(
        first_name="Test",
        last_name="User",
        email="test@example.com",
        hourly_rate=1000,
        status="ACTIVO"
    )
    db_session.session.add(emp)
    db_session.session.commit()
    return emp

@pytest.fixture
def pay_period(db_session):
    period = PayPeriod(
        name="Test Period",
        start_date=date(2026, 3, 1),
        end_date=date(2026, 3, 7)
    )
    db_session.session.add(period)
    db_session.session.commit()
    return period

def test_shift_hours_midnight():
    # 22:00 to 02:00 = 4 hours
    assert shift_hours(time(22, 0), time(2, 0)) == 4

def test_overlap_midnight_detection(app, db_session, employee):
    with app.app_context():
        # Shift A: Monday 22:00 -> 02:00 (into Tuesday)
        s1 = Shift(
            employee_id=employee.id,
            date=date(2026, 3, 2), # Monday
            start_time=time(22, 0),
            end_time=time(2, 0),
            status=ShiftStatus.PLANIFICADO.value,
            shift_role="caja",
            schedule_week_id="dummy"
        )
        db_session.session.add(s1)
        db_session.session.commit()

        # Shift B: Tuesday 01:00 -> 05:00 (Overlaps A)
        ok, err = validate_no_overlap(employee.id, date(2026, 3, 3), time(1, 0), time(5, 0))
        assert ok is False
        assert "Solapamiento" in err

        # Shift C: Monday 21:00 -> 23:00 (Overlaps A)
        ok, err = validate_no_overlap(employee.id, date(2026, 3, 2), time(21, 0), time(23, 0))
        assert ok is False

def test_payroll_regeneration_preserves_paid_status(app, db_session, employee, pay_period):
    from alfajor.services.payroll_calculator import _calculate_statement_from_shifts
    
    with app.app_context():
        # Create a paid statement
        st = PayStatement(
            pay_period_id=pay_period.id,
            employee_id=employee.id,
            total_calculated=100,
            reconciliation_status=ReconciliationStatus.PAGADO.value
        )
        db_session.session.add(st)
        db_session.session.commit()
        
        # Regenerate
        new_st = _calculate_statement_from_shifts(pay_period, employee, [])
        
        assert new_st.id == st.id
        assert new_st.reconciliation_status == ReconciliationStatus.PAGADO.value
