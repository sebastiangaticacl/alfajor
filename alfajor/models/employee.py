"""Employee, Availability."""

import uuid
from datetime import datetime
from alfajor.extensions import db
from alfajor.enums import EmployeeStatus


class Employee(db.Model):
    __tablename__ = "employees"
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255))
    phone = db.Column(db.String(50))
    base_role = db.Column(db.String(50))
    hourly_rate = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(20), default=EmployeeStatus.ACTIVO.value)
    branch_id = db.Column(db.String(36), db.ForeignKey("branches.id"))
    preferences = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    branch = db.relationship("Branch", backref="employees")

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class Availability(db.Model):
    __tablename__ = "availabilities"
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    employee_id = db.Column(db.String(36), db.ForeignKey("employees.id"), nullable=False)
    day_of_week = db.Column(db.Integer)  # 0-6 Lun-Dom
    start_time = db.Column(db.Time)
    end_time = db.Column(db.Time)
    is_available = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    employee = db.relationship("Employee", backref="availabilities")
