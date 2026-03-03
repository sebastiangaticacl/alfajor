"""PerformanceSnapshot."""

import uuid
from datetime import datetime
from alfajor.extensions import db


class PerformanceSnapshot(db.Model):
    __tablename__ = "performance_snapshots"
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    employee_id = db.Column(db.String(36), db.ForeignKey("employees.id"), nullable=False)
    pay_period_id = db.Column(db.String(36), db.ForeignKey("pay_periods.id"))
    period_start = db.Column(db.Date, nullable=False)
    period_end = db.Column(db.Date, nullable=False)
    branch_id = db.Column(db.String(36), db.ForeignKey("branches.id"))
    shift_role = db.Column(db.String(50))
    score = db.Column(db.Numeric(5, 2))
    total_hours = db.Column(db.Numeric(10, 2))
    total_shifts_completed = db.Column(db.Integer)
    total_late_minutes = db.Column(db.Integer)
    total_absences = db.Column(db.Integer)
    total_incidents = db.Column(db.Integer)
    consistency_score = db.Column(db.Numeric(5, 2))
    preset_used = db.Column(db.String(30))
    breakdown = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    employee = db.relationship("Employee", backref="performance_snapshots")
    pay_period = db.relationship("PayPeriod", backref="performance_snapshots")
    branch = db.relationship("Branch", backref="performance_snapshots")
