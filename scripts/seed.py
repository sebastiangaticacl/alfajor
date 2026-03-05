#!/usr/bin/env python3
"""
Seed demo para ALFAJOR.
Crea: admin, encargado, contabilidad, empleados, sucursal, semanas, periodo.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from datetime import datetime, date, time, timedelta
from alfajor import create_app
from alfajor.extensions import db
from alfajor.models import (
    User, Employee, Branch, Setting,
    ScheduleWeek, Shift,
    PayPeriod, PayStatement, PayLine,
)
from alfajor.enums import UserRole, WeekStatus, ShiftStatus, PayPeriodStatus, PayPeriodType


def seed():
    app = create_app()
    with app.app_context():
        if app.config.get("ENV") != "development":
            print("Seed solo permitido en desarrollo.")
            return
        existing_admin = User.query.filter_by(email="admin").first()
        if existing_admin:
            print("Seed ya ejecutado. Saltando.")
            return
        # Migrar admin antiguo si existe
        old_admin = User.query.filter_by(email="admin@cosasricas.local").first()
        if old_admin:
            old_admin.email = "admin"
            old_admin.set_password("admin")
            db.session.commit()
            print("Admin actualizado: admin / admin")
            return

        # Sucursal
        branch = Branch(name="Café Cosas Ricas Centro", code="CENTRO", address="Av. Principal 123")
        db.session.add(branch)
        db.session.flush()

        # Empleados
        emp_admin = Employee(
            first_name="Admin", last_name="Sistema",
            email="admin@cosasricas.local",
            base_role="admin", hourly_rate=100, status="ACTIVO", branch_id=branch.id
        )
        emp_enc = Employee(
            first_name="María", last_name="Encargada",
            email="encargado@cosasricas.local",
            base_role="caja", hourly_rate=50, status="ACTIVO", branch_id=branch.id
        )
        emp_cont = Employee(
            first_name="Pedro", last_name="Contador",
            email="contabilidad@cosasricas.local",
            base_role="caja", hourly_rate=45, status="ACTIVO", branch_id=branch.id
        )
        emp1 = Employee(
            first_name="Juan", last_name="Pérez",
            email="juan@cosasricas.local",
            base_role="caja", hourly_rate=40, status="ACTIVO", branch_id=branch.id
        )
        emp2 = Employee(
            first_name="Ana", last_name="García",
            email="ana@cosasricas.local",
            base_role="barra", hourly_rate=42, status="ACTIVO", branch_id=branch.id
        )
        for e in [emp_admin, emp_enc, emp_cont, emp1, emp2]:
            db.session.add(e)
        db.session.flush()

        # Usuarios
        admin = User(email="admin", role=UserRole.ADMIN.value, employee_id=emp_admin.id)
        admin.set_password("admin")
        enc = User(email="encargado@cosasricas.local", role=UserRole.ENCARGADO.value, employee_id=emp_enc.id)
        enc.set_password("enc123")
        cont = User(email="contabilidad@cosasricas.local", role=UserRole.CONTABILIDAD.value, employee_id=emp_cont.id)
        cont.set_password("cont123")
        trab = User(email="juan@cosasricas.local", role=UserRole.TRABAJADOR.value, employee_id=emp1.id)
        trab.set_password("trab123")
        for u in [admin, enc, cont, trab]:
            db.session.add(u)
        db.session.flush()

        # Settings
        settings_data = [
            ("schedule.hours", {
                "monday": {"open": "08:00", "close": "22:00"},
                "tuesday": {"open": "08:00", "close": "22:00"},
                "wednesday": {"open": "08:00", "close": "22:00"},
                "thursday": {"open": "08:00", "close": "22:00"},
                "friday": {"open": "08:00", "close": "22:00"},
                "saturday": {"open": "09:00", "close": "23:00"},
                "sunday": {"open": "10:00", "close": "20:00"},
            }),
            ("rules.max_weekly_hours", 48),
            ("rules.min_rest_hours", 11),
            ("rules.max_consecutive_days", 6),
            ("rules.overtime_threshold_hours", 8),
            ("rules.overtime_multiplier", 1.5),
            ("shift_roles", ["caja", "barra", "cocina", "runner"]),
        ]
        for k, v in settings_data:
            db.session.add(Setting(key=k, value=v))
        db.session.flush()

        # Semana demo
        today = date.today()
        monday = today - timedelta(days=today.weekday())
        sunday = monday + timedelta(days=6)
        week = ScheduleWeek(
            start_date=monday, end_date=sunday,
            status=WeekStatus.PUBLICADA.value,
            branch_id=branch.id, created_by=admin.id,
            published_at=datetime.utcnow()
        )
        db.session.add(week)
        db.session.flush()

        # Turnos demo
        for i, emp in enumerate([emp1, emp2]):
            for d in range(3):
                shift_date = monday + timedelta(days=d)
                db.session.add(Shift(
                    schedule_week_id=week.id, employee_id=emp.id,
                    shift_role="caja" if i == 0 else "barra",
                    date=shift_date,
                    start_time=time(9, 0), end_time=time(17, 0),
                    status=ShiftStatus.COMPLETADO.value,
                    branch_id=branch.id
                ))

        # Periodo de pago
        period = PayPeriod(
            name=f"Semana {monday} - {sunday}",
            start_date=monday, end_date=sunday,
            period_type=PayPeriodType.SEMANAL.value,
            status=PayPeriodStatus.ABIERTO.value,
            created_by=admin.id
        )
        db.session.add(period)
        db.session.flush()

        # PayStatements demo
        for emp in [emp1, emp2]:
            st = PayStatement(
                pay_period_id=period.id, employee_id=emp.id,
                total_base_hours=24, total_calculated=int(emp.hourly_rate) * 24,
                reconciliation_status="PENDIENTE",
                generated_at=datetime.utcnow()
            )
            db.session.add(st)
            db.session.flush()
            db.session.add(PayLine(
                pay_statement_id=st.id, line_type="BASE_HOURS",
                description="Horas base", quantity=24, unit_rate=int(emp.hourly_rate),
                amount=int(emp.hourly_rate) * 24
            ))

        db.session.commit()
        print("Seed completado.")
        print("  Admin: admin / admin")
        print("  Encargado: encargado@cosasricas.local / enc123")
        print("  Contabilidad: contabilidad@cosasricas.local / cont123")
        print("  Trabajador: juan@cosasricas.local / trab123")


if __name__ == "__main__":
    seed()
