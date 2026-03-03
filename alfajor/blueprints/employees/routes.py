"""Rutas empleados."""

from flask import render_template, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from alfajor.utils.decorators import encargado_or_admin
from alfajor.blueprints.employees import bp
from alfajor.blueprints.employees.forms import EmployeeForm
from alfajor.extensions import db
from alfajor.models import Employee, Branch


@bp.route("/")
@login_required
def list():
    if current_user.role in ("ADMIN", "ENCARGADO"):
        employees = Employee.query.order_by(Employee.last_name).all()
    else:
        employees = [current_user.employee] if current_user.employee else []
    return render_template("employees/list.html", employees=employees)


@bp.route("/new", methods=["GET", "POST"])
@login_required
@encargado_or_admin
def new():
    form = EmployeeForm()
    form.branch_id.choices = [("", "—")] + [(b.id, b.name) for b in Branch.query.order_by(Branch.name).all()]
    if form.validate_on_submit():
        emp = Employee(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data or None,
            phone=form.phone.data or None,
            base_role=form.base_role.data or None,
            hourly_rate=form.hourly_rate.data,
            status=form.status.data,
            branch_id=form.branch_id.data or None,
        )
        db.session.add(emp)
        db.session.commit()
        flash("Empleado creado.", "success")
        return redirect(url_for("employees.list"))
    return render_template("employees/form.html", form=form, employee=None)


@bp.route("/<id>")
@login_required
def detail(id):
    employee = Employee.query.get_or_404(id)
    if current_user.role == "TRABAJADOR" and current_user.employee_id != employee.id:
        abort(403)
    return render_template("employees/detail.html", employee=employee)


@bp.route("/<id>/edit", methods=["GET", "POST"])
@login_required
@encargado_or_admin
def edit(id):
    employee = Employee.query.get_or_404(id)
    form = EmployeeForm(obj=employee)
    form.branch_id.choices = [("", "—")] + [(b.id, b.name) for b in Branch.query.order_by(Branch.name).all()]
    if form.validate_on_submit():
        employee.first_name = form.first_name.data
        employee.last_name = form.last_name.data
        employee.email = form.email.data or None
        employee.phone = form.phone.data or None
        employee.base_role = form.base_role.data or None
        employee.hourly_rate = form.hourly_rate.data
        employee.status = form.status.data
        employee.branch_id = form.branch_id.data or None
        db.session.commit()
        flash("Empleado actualizado.", "success")
        return redirect(url_for("employees.detail", id=employee.id))
    return render_template("employees/form.html", form=form, employee=employee)


@bp.route("/<id>/delete", methods=["POST"])
@login_required
@encargado_or_admin
def delete(id):
    employee = Employee.query.get_or_404(id)
    db.session.delete(employee)
    db.session.commit()
    flash("Empleado eliminado.", "success")
    return redirect(url_for("employees.list"))
