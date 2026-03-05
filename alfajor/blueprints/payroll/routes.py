"""Rutas nómina."""

from datetime import date, timedelta, datetime
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from alfajor.utils.decorators import admin_required, contabilidad_or_admin
from alfajor.blueprints.payroll import bp
from alfajor.extensions import db
from alfajor.models import PayPeriod, PayStatement, PayLine, PaymentTransaction, Employee
from sqlalchemy.orm import selectinload
from alfajor.enums import PayPeriodStatus, PayPeriodType, PaymentMethod, ReconciliationStatus
from alfajor.services.payroll_calculator import generate_statements_for_period


@bp.route("/")
@login_required
def periods():
    if current_user.role == "TRABAJADOR":
        return redirect(url_for("payroll.my_statements"))
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    query = PayPeriod.query.order_by(PayPeriod.start_date.desc())
    total = query.count()
    periods_list = query.limit(per_page).offset((page - 1) * per_page).all()
    return render_template("payroll/periods.html", periods=periods_list, page=page, per_page=per_page, total=total)


@bp.route("/my")
@login_required
def my_statements():
    if not current_user.employee_id:
        return render_template("payroll/my_statements.html", statements=[], page=1, per_page=20, total=0)
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    query = PayStatement.query.options(selectinload(PayStatement.pay_period)).filter_by(
        employee_id=current_user.employee_id
    ).order_by(PayStatement.created_at.desc())
    total = query.count()
    statements = query.limit(per_page).offset((page - 1) * per_page).all()
    return render_template(
        "payroll/my_statements.html",
        statements=statements,
        page=page,
        per_page=per_page,
        total=total,
    )


@bp.route("/period/new", methods=["GET", "POST"])
@login_required
@contabilidad_or_admin
def period_new():
    if request.method == "POST":
        start = request.form.get("start_date")
        end = request.form.get("end_date")
        name = request.form.get("name")
        ptype = request.form.get("period_type", PayPeriodType.SEMANAL.value)
        if not start or not end:
            flash("Fechas requeridas.", "danger")
            return render_template("payroll/period_form.html")
        try:
            start_d = date.fromisoformat(start)
            end_d = date.fromisoformat(end)
        except ValueError:
            flash("Fechas inválidas.", "danger")
            return render_template("payroll/period_form.html")
        period = PayPeriod(
            name=name or f"Periodo {start_d} - {end_d}",
            start_date=start_d,
            end_date=end_d,
            period_type=ptype,
            status=PayPeriodStatus.ABIERTO.value,
            created_by=current_user.id,
        )
        db.session.add(period)
        db.session.commit()
        flash("Periodo creado.", "success")
        return redirect(url_for("payroll.period_detail", id=period.id))
    return render_template("payroll/period_form.html")


@bp.route("/period/<id>")
@login_required
@contabilidad_or_admin
def period_detail(id):
    period = PayPeriod.query.get_or_404(id)
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    query = PayStatement.query.options(selectinload(PayStatement.employee)).filter_by(
        pay_period_id=period.id
    )
    total = query.count()
    statements = query.limit(per_page).offset((page - 1) * per_page).all()
    transactions = PaymentTransaction.query.filter_by(pay_period_id=period.id).all()
    paid_map = {}
    for t in transactions:
        paid_map[t.employee_id] = paid_map.get(t.employee_id, 0) + t.amount
    return render_template(
        "payroll/period_detail.html",
        period=period,
        statements=statements,
        page=page,
        per_page=per_page,
        total=total,
        paid_map=paid_map,
    )


@bp.route("/period/<id>/generate", methods=["POST"])
@login_required
@contabilidad_or_admin
def period_generate(id):
    created = generate_statements_for_period(id)
    db.session.commit()
    flash(f"Generadas {len(created)} liquidaciones.", "success")
    return redirect(url_for("payroll.period_detail", id=id))


@bp.route("/statement/<id>")
@login_required
def statement_detail(id):
    st = PayStatement.query.get_or_404(id)
    if current_user.role == "TRABAJADOR" and current_user.employee_id != st.employee_id:
        from flask import abort
        abort(403)
    return render_template("payroll/statement_detail.html", statement=st)


@bp.route("/transaction/new", methods=["GET", "POST"])
@login_required
@contabilidad_or_admin
def transaction_new():
    if request.method == "POST":
        emp_id = request.form.get("employee_id")
        period_id = request.form.get("pay_period_id")
        amount = request.form.get("amount")
        method = request.form.get("method", PaymentMethod.TRANSFER.value)
        ref = request.form.get("reference", "")
        payment_date = request.form.get("payment_date")
        if not all([emp_id, period_id, amount, payment_date]):
            flash("Datos incompletos.", "danger")
            return redirect(url_for("payroll.periods"))
        try:
            amt = int(amount)
            pay_d = date.fromisoformat(payment_date)
        except (ValueError, TypeError):
            flash("Datos inválidos.", "danger")
            return redirect(url_for("payroll.periods"))
        existing = PaymentTransaction.query.filter_by(
            employee_id=emp_id,
            pay_period_id=period_id,
            reference=ref or None,
            payment_date=pay_d,
            amount=amt,
        ).first()
        if existing:
            flash("Transacción duplicada (idempotencia).", "warning")
            return redirect(url_for("payroll.period_detail", id=period_id))
        tx = PaymentTransaction(
            employee_id=emp_id,
            pay_period_id=period_id,
            method=method,
            amount=amt,
            reference=ref or None,
            payment_date=pay_d,
            created_by=current_user.id,
        )
        db.session.add(tx)
        st = PayStatement.query.filter_by(pay_period_id=period_id, employee_id=emp_id).first()
        if st:
            total_paid = sum(
                int(t.amount) for t in PaymentTransaction.query.filter_by(
                    pay_period_id=period_id, employee_id=emp_id
                ).all()
            ) + amt
            calc = int(st.total_calculated)
            if total_paid >= calc:
                st.reconciliation_status = ReconciliationStatus.PAGADO.value
            elif total_paid > 0:
                st.reconciliation_status = ReconciliationStatus.PARCIAL.value
            db.session.commit()
        db.session.commit()
        flash("Pago registrado.", "success")
        return redirect(url_for("payroll.period_detail", id=period_id))
    periods = PayPeriod.query.order_by(PayPeriod.start_date.desc()).limit(20).all()
    employees = Employee.query.filter_by(status="ACTIVO").order_by(Employee.last_name).all()
    return render_template("payroll/transaction_form.html", periods=periods, employees=employees)
