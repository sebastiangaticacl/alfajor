"""Servicio de auditoría."""

from flask import request
from alfajor.extensions import db
from alfajor.models import AuditLog


def log(action, entity_type=None, entity_id=None, old_value=None, new_value=None, user_id=None):
    """Registra una acción en el audit log."""
    entry = AuditLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=str(entity_id) if entity_id else None,
        old_value=old_value,
        new_value=new_value,
        ip_address=request.remote_addr if request else None,
    )
    db.session.add(entry)
    db.session.commit()
