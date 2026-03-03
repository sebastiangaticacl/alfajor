"""Formularios admin."""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField
from wtforms.validators import DataRequired, Email, Length, Optional


class UserForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Contraseña", validators=[Optional(), Length(min=6)])
    role = SelectField("Rol", choices=[
        ("ADMIN", "Admin"),
        ("ENCARGADO", "Encargado"),
        ("CONTABILIDAD", "Contabilidad"),
        ("TRABAJADOR", "Trabajador"),
    ], validators=[DataRequired()])
    employee_id = SelectField("Empleado", coerce=str, validators=[Optional()])
    active = BooleanField("Activo", default=True)
