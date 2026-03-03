"""ShiftRequest."""

import uuid
from datetime import datetime
from alfajor.extensions import db
from alfajor.enums import RequestType, RequestStatus


class ShiftRequest(db.Model):
    __tablename__ = "shift_requests"
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    employee_id = db.Column(db.String(36), db.ForeignKey("employees.id"), nullable=False)
    request_type = db.Column(db.String(30))
    shift_id = db.Column(db.String(36), db.ForeignKey("shifts.id"))
    target_shift_id = db.Column(db.String(36), db.ForeignKey("shifts.id"))
    requested_date = db.Column(db.Date)
    reason = db.Column(db.Text)
    status = db.Column(db.String(20), default=RequestStatus.PENDIENTE.value)
    reviewed_by = db.Column(db.String(36), db.ForeignKey("users.id"))
    reviewed_at = db.Column(db.DateTime)
    review_comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    employee = db.relationship("Employee", backref="shift_requests")
    shift = db.relationship("Shift", foreign_keys=[shift_id])
    target_shift = db.relationship("Shift", foreign_keys=[target_shift_id])
    reviewer = db.relationship("User", backref="reviewed_requests")
