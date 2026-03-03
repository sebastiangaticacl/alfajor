"""AttendanceEvent."""

import uuid
from datetime import datetime
from alfajor.extensions import db


class AttendanceEvent(db.Model):
    __tablename__ = "attendance_events"
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    shift_id = db.Column(db.String(36), db.ForeignKey("shifts.id"), nullable=False)
    employee_id = db.Column(db.String(36), db.ForeignKey("employees.id"), nullable=False)
    event_type = db.Column(db.String(30))
    recorded_at = db.Column(db.DateTime, nullable=False)
    minutes_late = db.Column(db.Integer)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    shift = db.relationship("Shift", backref="attendance_events")
    employee = db.relationship("Employee", backref="attendance_events")
