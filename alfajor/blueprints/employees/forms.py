"""Formularios empleados."""

from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, SelectField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Optional, NumberRange


class EmployeeForm(FlaskForm):
    first_name = StringField("Nombre", validators=[DataRequired()])
    last_name = StringField("Apellido", validators=[DataRequired()])
    email = StringField("Email", validators=[Optional()])
    phone = StringField("Teléfono", validators=[Optional()])
    base_role = SelectField("Rol base", choices=[
        ("", "—"),
        ("caja", "Caja"),
        ("barra", "Barra"),
        ("cocina", "Cocina"),
        ("runner", "Runner"),
    ], validators=[Optional()])
    hourly_rate = FloatField("Valor hora", validators=[DataRequired(), NumberRange(min=0)])
    status = SelectField("Estado", choices=[
        ("ACTIVO", "Activo"),
        ("INACTIVO", "Inactivo"),
        ("SUSPENDIDO", "Suspendido"),
    ], validators=[DataRequired()])
    branch_id = SelectField("Sucursal", coerce=str, validators=[Optional()])
