"""ScheduleWeek, Shift."""

import uuid
from datetime import datetime, date, time
from alfajor.extensions import db
from alfajor.enums import WeekStatus, ShiftStatus


class ScheduleWeek(db.Model):
    __tablename__ = "schedule_weeks"
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), nullable=False, default=WeekStatus.BORRADOR.value)
    branch_id = db.Column(db.String(36), db.ForeignKey("branches.id"))
    created_by = db.Column(db.String(36), db.ForeignKey("users.id"))
    published_at = db.Column(db.DateTime)
    closed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    branch = db.relationship("Branch", backref="schedule_weeks")
    creator = db.relationship("User", backref="created_weeks")
    shifts = db.relationship("Shift", backref="schedule_week", cascade="all, delete-orphan")


class Shift(db.Model):
    __tablename__ = "shifts"
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    schedule_week_id = db.Column(db.String(36), db.ForeignKey("schedule_weeks.id"), nullable=False)
    employee_id = db.Column(db.String(36), db.ForeignKey("employees.id"), nullable=False)
    shift_role = db.Column(db.String(50), nullable=False)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    status = db.Column(db.String(20), nullable=False, default=ShiftStatus.PLANIFICADO.value)
    branch_id = db.Column(db.String(36), db.ForeignKey("branches.id"))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    employee = db.relationship("Employee", backref="shifts")
    branch = db.relationship("Branch", backref="shifts")
