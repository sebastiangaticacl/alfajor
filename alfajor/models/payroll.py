"""PayPeriod, PayStatement, PayLine, PaymentTransaction."""

import uuid
from datetime import datetime
from alfajor.extensions import db
from alfajor.enums import PayPeriodStatus, PayPeriodType, ReconciliationStatus, PayLineType, PaymentMethod


class PayPeriod(db.Model):
    __tablename__ = "pay_periods"
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100))
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    period_type = db.Column(db.String(20))
    status = db.Column(db.String(20), nullable=False, default=PayPeriodStatus.ABIERTO.value)
    created_by = db.Column(db.String(36), db.ForeignKey("users.id"))
    approved_at = db.Column(db.DateTime)
    closed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    creator = db.relationship("User", backref="created_periods")
    statements = db.relationship("PayStatement", backref="pay_period", cascade="all, delete-orphan")
    transactions = db.relationship("PaymentTransaction", backref="pay_period", cascade="all, delete-orphan")


class PayStatement(db.Model):
    __tablename__ = "pay_statements"
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    pay_period_id = db.Column(db.String(36), db.ForeignKey("pay_periods.id"), nullable=False)
    employee_id = db.Column(db.String(36), db.ForeignKey("employees.id"), nullable=False)
    total_base_hours = db.Column(db.Numeric(10, 2), default=0)
    total_overtime_hours = db.Column(db.Numeric(10, 2), default=0)
    total_surcharges = db.Column(db.Numeric(10, 2), default=0)
    total_bonuses = db.Column(db.Numeric(10, 2), default=0)
    total_deductions = db.Column(db.Numeric(10, 2), default=0)
    total_calculated = db.Column(db.Numeric(10, 2), nullable=False)
    reconciliation_status = db.Column(db.String(20), default=ReconciliationStatus.PENDIENTE.value)
    generated_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    employee = db.relationship("Employee", backref="pay_statements")
    lines = db.relationship("PayLine", backref="pay_statement", cascade="all, delete-orphan")


class PayLine(db.Model):
    __tablename__ = "pay_lines"
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    pay_statement_id = db.Column(db.String(36), db.ForeignKey("pay_statements.id"), nullable=False)
    line_type = db.Column(db.String(30))
    description = db.Column(db.String(255))
    quantity = db.Column(db.Numeric(10, 2))
    unit_rate = db.Column(db.Numeric(10, 2))
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    reference_id = db.Column(db.String(36))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class PaymentTransaction(db.Model):
    __tablename__ = "payment_transactions"
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    employee_id = db.Column(db.String(36), db.ForeignKey("employees.id"), nullable=False)
    pay_period_id = db.Column(db.String(36), db.ForeignKey("pay_periods.id"), nullable=False)
    method = db.Column(db.String(30))
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    reference = db.Column(db.String(100))
    payment_date = db.Column(db.Date, nullable=False)
    notes = db.Column(db.Text)
    created_by = db.Column(db.String(36), db.ForeignKey("users.id"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    employee = db.relationship("Employee", backref="payment_transactions")
    creator = db.relationship("User", backref="created_transactions")

    __table_args__ = (
        db.UniqueConstraint("employee_id", "reference", "payment_date", "amount", name="uq_payment_idempotency"),
    )
