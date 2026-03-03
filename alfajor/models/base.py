"""Base para modelos con UUID."""

import uuid
from alfajor.extensions import db


def generate_uuid():
    return str(uuid.uuid4())


class BaseModel(db.Model):
    """Modelo base abstracto."""
    __abstract__ = True
