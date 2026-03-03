# ALFAJOR – Plan del Primer Paso

**Sistema de Turnos del Café Cosas Ricas** · Desarrollado por Seba Gatica · 2026

---

## 1. ÁRBOL DE CARPETAS PROPUESTO

```
CRT/
├── alfajor/                      # Paquete principal
│   ├── __init__.py              # create_app() factory
│   ├── config.py                # Configuración por entorno
│   ├── extensions.py            # Flask extensions (db, login, migrate)
│   │
│   ├── models/                  # Modelos SQLAlchemy
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── employee.py
│   │   ├── schedule.py          # ScheduleWeek, Shift, Availability
│   │   ├── settings.py          # Setting, ShiftRole, Branch
│   │   ├── requests.py          # ShiftRequest
│   │   ├── attendance.py        # AttendanceEvent
│   │   ├── payroll.py           # PayPeriod, PayStatement, PayLine, PaymentTransaction
│   │   ├── ranking.py           # PerformanceSnapshot
│   │   └── audit.py             # AuditLog
│   │
│   ├── enums.py                 # Todos los enums centralizados
│   │
│   ├── blueprints/
│   │   ├── __init__.py
│   │   ├── auth/
│   │   │   ├── __init__.py
│   │   │   ├── routes.py
│   │   │   └── forms.py
│   │   ├── admin/
│   │   │   ├── __init__.py
│   │   │   ├── routes.py
│   │   │   └── forms.py
│   │   ├── employees/
│   │   │   ├── __init__.py
│   │   │   ├── routes.py
│   │   │   └── forms.py
│   │   ├── shifts/
│   │   │   ├── __init__.py
│   │   │   ├── routes.py
│   │   │   └── forms.py
│   │   ├── settings/
│   │   │   ├── __init__.py
│   │   │   ├── routes.py
│   │   │   └── forms.py
│   │   ├── requests/
│   │   │   ├── __init__.py
│   │   │   ├── routes.py
│   │   │   └── forms.py
│   │   ├── payroll/
│   │   │   ├── __init__.py
│   │   │   ├── routes.py
│   │   │   └── forms.py
│   │   ├── ranking/
│   │   │   ├── __init__.py
│   │   │   ├── routes.py
│   │   │   └── forms.py
│   │   └── reports/
│   │       ├── __init__.py
│   │       └── routes.py
│   │
│   ├── services/                # Lógica de negocio
│   │   ├── __init__.py
│   │   ├── shift_validator.py   # Validaciones de turnos
│   │   ├── payroll_calculator.py
│   │   ├── ranking_calculator.py
│   │   └── audit_service.py
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── decorators.py        # @role_required, etc.
│   │   └── helpers.py
│   │
│   └── templates/
│       ├── base.html
│       ├── auth/
│       │   └── login.html
│       ├── admin/
│       │   ├── dashboard.html
│       │   ├── users.html
│       │   ├── config.html
│       │   └── ranking.html
│       ├── employees/
│       │   ├── list.html
│       │   ├── form.html
│       │   └── detail.html
│       ├── shifts/
│       │   ├── calendar.html
│       │   └── list.html
│       ├── payroll/
│       │   ├── periods.html
│       │   ├── statements.html
│       │   └── reconciliation.html
│       ├── requests/
│       │   └── list.html
│       └── components/          # Macros/partials
│           ├── sidebar.html
│           ├── topbar.html
│           ├── footer.html
│           └── alerts.html
│
├── migrations/                  # Alembic/Flask-Migrate
│   └── versions/
│
├── static/
│   ├── css/
│   │   ├── design-system.css    # Tokens CSS (obligatorio)
│   │   └── app.css
│   ├── js/
│   │   ├── app.js
│   │   ├── calendar.js
│   │   └── dashboard.js
│   └── img/
│       └── logo.svg             # Placeholder futuro
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py              # Fixtures pytest
│   ├── test_auth.py
│   ├── test_shifts.py
│   ├── test_payroll.py
│   └── test_ranking.py
│
├── scripts/
│   ├── seed.py                  # Seed demo
│   └── create_admin.py
│
├── docs/
│   ├── PLAN_PRIMER_PASO.md      # Este documento
│   └── API.md
│
├── .env.example
├── .gitignore
├── requirements.txt
├── wsgi.py                      # Gunicorn entry
└── README.md
```

---

## 2. ESQUEMA DE BASE DE DATOS (CAMPOS COMPLETOS)

### 2.1 User
| Campo | Tipo | Constraints | Descripción |
|-------|------|-------------|-------------|
| id | UUID | PK | |
| email | VARCHAR(255) | UNIQUE, NOT NULL | |
| password_hash | VARCHAR(255) | NOT NULL | |
| role | VARCHAR(20) | NOT NULL, FK→Role | ADMIN, ENCARGADO, CONTABILIDAD, TRABAJADOR |
| employee_id | UUID | FK→Employee, NULL | Vinculación opcional |
| active | BOOLEAN | DEFAULT true | |
| created_at | TIMESTAMP | DEFAULT now() | |
| updated_at | TIMESTAMP | DEFAULT now() | |

### 2.2 Employee
| Campo | Tipo | Constraints | Descripción |
|-------|------|-------------|-------------|
| id | UUID | PK | |
| first_name | VARCHAR(100) | NOT NULL | |
| last_name | VARCHAR(100) | NOT NULL | |
| email | VARCHAR(255) | | |
| phone | VARCHAR(50) | | |
| base_role | VARCHAR(50) | | caja, barra, cocina, runner |
| hourly_rate | DECIMAL(10,2) | NOT NULL | Valor hora base |
| status | VARCHAR(20) | DEFAULT 'ACTIVO' | ACTIVO, INACTIVO, SUSPENDIDO |
| branch_id | UUID | FK→Branch, NULL | Sucursal (opcional) |
| preferences | JSONB | | Restricciones/preferencias |
| created_at | TIMESTAMP | | |
| updated_at | TIMESTAMP | | |

### 2.3 Branch (Sucursal)
| Campo | Tipo | Constraints | Descripción |
|-------|------|-------------|-------------|
| id | UUID | PK | |
| name | VARCHAR(100) | NOT NULL | |
| code | VARCHAR(20) | UNIQUE | |
| address | TEXT | | |
| active | BOOLEAN | DEFAULT true | |
| created_at | TIMESTAMP | | |
| updated_at | TIMESTAMP | | |

### 2.4 ScheduleWeek
| Campo | Tipo | Constraints | Descripción |
|-------|------|-------------|-------------|
| id | UUID | PK | |
| start_date | DATE | NOT NULL | Lunes de la semana |
| end_date | DATE | NOT NULL | Domingo |
| status | VARCHAR(20) | NOT NULL | BORRADOR, PUBLICADA, CERRADA |
| branch_id | UUID | FK→Branch, NULL | |
| created_by | UUID | FK→User | |
| published_at | TIMESTAMP | NULL | |
| closed_at | TIMESTAMP | NULL | |
| created_at | TIMESTAMP | | |
| updated_at | TIMESTAMP | | |

### 2.5 Shift
| Campo | Tipo | Constraints | Descripción |
|-------|------|-------------|-------------|
| id | UUID | PK | |
| schedule_week_id | UUID | FK→ScheduleWeek, NOT NULL | |
| employee_id | UUID | FK→Employee, NOT NULL | |
| shift_role | VARCHAR(50) | NOT NULL | Rol del turno |
| date | DATE | NOT NULL | |
| start_time | TIME | NOT NULL | |
| end_time | TIME | NOT NULL | |
| status | VARCHAR(20) | NOT NULL | PLANIFICADO, CONFIRMADO, COMPLETADO, AUSENTE, ANULADO |
| branch_id | UUID | FK→Branch, NULL | |
| notes | TEXT | | |
| created_at | TIMESTAMP | | |
| updated_at | TIMESTAMP | | |

### 2.6 Availability
| Campo | Tipo | Constraints | Descripción |
|-------|------|-------------|-------------|
| id | UUID | PK | |
| employee_id | UUID | FK→Employee, NOT NULL | |
| day_of_week | INTEGER | 0-6 (Lun-Dom) | |
| start_time | TIME | | NULL = no disponible |
| end_time | TIME | | |
| is_available | BOOLEAN | DEFAULT true | |
| created_at | TIMESTAMP | | |
| updated_at | TIMESTAMP | | |

### 2.7 Setting
| Campo | Tipo | Constraints | Descripción |
|-------|------|-------------|-------------|
| id | UUID | PK | |
| key | VARCHAR(100) | UNIQUE, NOT NULL | |
| value | JSONB | NOT NULL | Config flexible |
| description | TEXT | | |
| updated_at | TIMESTAMP | | |

### 2.8 ShiftRequest
| Campo | Tipo | Constraints | Descripción |
|-------|------|-------------|-------------|
| id | UUID | PK | |
| employee_id | UUID | FK→Employee, NOT NULL | |
| request_type | VARCHAR(30) | | CAMBIO_TURNO, DIA_LIBRE, SWAP |
| shift_id | UUID | FK→Shift, NULL | Si aplica |
| target_shift_id | UUID | FK→Shift, NULL | Para swap |
| requested_date | DATE | | Para día libre |
| reason | TEXT | | |
| status | VARCHAR(20) | | PENDIENTE, APROBADO, RECHAZADO |
| reviewed_by | UUID | FK→User | |
| reviewed_at | TIMESTAMP | | |
| review_comment | TEXT | | |
| created_at | TIMESTAMP | | |
| updated_at | TIMESTAMP | | |

### 2.9 AttendanceEvent
| Campo | Tipo | Constraints | Descripción |
|-------|------|-------------|-------------|
| id | UUID | PK | |
| shift_id | UUID | FK→Shift, NOT NULL | |
| employee_id | UUID | FK→Employee, NOT NULL | |
| event_type | VARCHAR(30) | | CHECK_IN, CHECK_OUT, LATE, ABSENT, INCIDENT |
| recorded_at | TIMESTAMP | NOT NULL | |
| minutes_late | INTEGER | | Si LATE |
| notes | TEXT | | |
| created_at | TIMESTAMP | | |

### 2.10 PayPeriod
| Campo | Tipo | Constraints | Descripción |
|-------|------|-------------|-------------|
| id | UUID | PK | |
| name | VARCHAR(100) | | Ej: "Semana 1-7 Mar 2026" |
| start_date | DATE | NOT NULL | |
| end_date | DATE | NOT NULL | |
| period_type | VARCHAR(20) | | SEMANAL, QUINCENAL, MENSUAL |
| status | VARCHAR(20) | NOT NULL | ABIERTO, EN_REVISION, APROBADO, PAGADO, CERRADO |
| created_by | UUID | FK→User | |
| approved_at | TIMESTAMP | NULL | |
| closed_at | TIMESTAMP | NULL | |
| created_at | TIMESTAMP | | |
| updated_at | TIMESTAMP | | |

### 2.11 PayStatement
| Campo | Tipo | Constraints | Descripción |
|-------|------|-------------|-------------|
| id | UUID | PK | |
| pay_period_id | UUID | FK→PayPeriod, NOT NULL | |
| employee_id | UUID | FK→Employee, NOT NULL | |
| total_base_hours | DECIMAL(10,2) | DEFAULT 0 | |
| total_overtime_hours | DECIMAL(10,2) | DEFAULT 0 | |
| total_surcharges | DECIMAL(10,2) | DEFAULT 0 | |
| total_bonuses | DECIMAL(10,2) | DEFAULT 0 | |
| total_deductions | DECIMAL(10,2) | DEFAULT 0 | |
| total_calculated | DECIMAL(10,2) | NOT NULL | |
| reconciliation_status | VARCHAR(20) | | PENDIENTE, PARCIAL, PAGADO, DIFERENCIA |
| generated_at | TIMESTAMP | | |
| created_at | TIMESTAMP | | |
| updated_at | TIMESTAMP | | |

### 2.12 PayLine
| Campo | Tipo | Constraints | Descripción |
|-------|------|-------------|-------------|
| id | UUID | PK | |
| pay_statement_id | UUID | FK→PayStatement, NOT NULL | |
| line_type | VARCHAR(30) | | BASE_HOURS, OVERTIME, SURCHARGE, BONUS, DEDUCTION |
| description | VARCHAR(255) | | |
| quantity | DECIMAL(10,2) | | Horas o unidades |
| unit_rate | DECIMAL(10,2) | | |
| amount | DECIMAL(10,2) | NOT NULL | |
| reference_id | UUID | | FK shift/attendance si aplica |
| created_at | TIMESTAMP | | |

### 2.13 PaymentTransaction
| Campo | Tipo | Constraints | Descripción |
|-------|------|-------------|-------------|
| id | UUID | PK | |
| employee_id | UUID | FK→Employee, NOT NULL | |
| pay_period_id | UUID | FK→PayPeriod, NOT NULL | |
| method | VARCHAR(30) | | TRANSFER, CASH, CHECK |
| amount | DECIMAL(10,2) | NOT NULL | |
| reference | VARCHAR(100) | | Idempotencia |
| payment_date | DATE | NOT NULL | |
| notes | TEXT | | |
| created_by | UUID | FK→User | |
| created_at | TIMESTAMP | | |
| updated_at | TIMESTAMP | | |

**Índice único idempotencia:** (employee_id, reference, payment_date, amount)

### 2.14 PerformanceSnapshot
| Campo | Tipo | Constraints | Descripción |
|-------|------|-------------|-------------|
| id | UUID | PK | |
| employee_id | UUID | FK→Employee, NOT NULL | |
| pay_period_id | UUID | FK→PayPeriod, NULL | O rango custom |
| period_start | DATE | NOT NULL | |
| period_end | DATE | NOT NULL | |
| branch_id | UUID | FK→Branch, NULL | |
| shift_role | VARCHAR(50) | NULL | |
| score | DECIMAL(5,2) | 0-100 | |
| total_hours | DECIMAL(10,2) | | |
| total_shifts_completed | INTEGER | | |
| total_late_minutes | INTEGER | | |
| total_absences | INTEGER | | |
| total_incidents | INTEGER | | |
| consistency_score | DECIMAL(5,2) | | 0-100 |
| preset_used | VARCHAR(30) | | BALANCEADO, PUNTUALIDAD, ESTABILIDAD |
| breakdown | JSONB | | Detalle pesos |
| created_at | TIMESTAMP | | |

### 2.15 AuditLog
| Campo | Tipo | Constraints | Descripción |
|-------|------|-------------|-------------|
| id | UUID | PK | |
| user_id | UUID | FK→User, NULL | |
| action | VARCHAR(50) | NOT NULL | |
| entity_type | VARCHAR(50) | | |
| entity_id | UUID | | |
| old_value | JSONB | | |
| new_value | JSONB | | |
| ip_address | VARCHAR(45) | | |
| created_at | TIMESTAMP | NOT NULL | |

---

## 3. ENUMS Y REGLAS DE VALIDACIÓN

### 3.1 Enums

```python
# user.py
class UserRole(str, Enum):
    ADMIN = "ADMIN"
    ENCARGADO = "ENCARGADO"
    CONTABILIDAD = "CONTABILIDAD"
    TRABAJADOR = "TRABAJADOR"

# schedule.py
class WeekStatus(str, Enum):
    BORRADOR = "BORRADOR"
    PUBLICADA = "PUBLICADA"
    CERRADA = "CERRADA"

class ShiftStatus(str, Enum):
    PLANIFICADO = "PLANIFICADO"
    CONFIRMADO = "CONFIRMADO"
    COMPLETADO = "COMPLETADO"
    AUSENTE = "AUSENTE"
    ANULADO = "ANULADO"

# payroll.py
class PayPeriodStatus(str, Enum):
    ABIERTO = "ABIERTO"
    EN_REVISION = "EN_REVISION"
    APROBADO = "APROBADO"
    PAGADO = "PAGADO"
    CERRADO = "CERRADO"

class PayPeriodType(str, Enum):
    SEMANAL = "SEMANAL"
    QUINCENAL = "QUINCENAL"
    MENSUAL = "MENSUAL"

class ReconciliationStatus(str, Enum):
    PENDIENTE = "PENDIENTE"
    PARCIAL = "PARCIAL"
    PAGADO = "PAGADO"
    DIFERENCIA = "DIFERENCIA"

class PayLineType(str, Enum):
    BASE_HOURS = "BASE_HOURS"
    OVERTIME = "OVERTIME"
    SURCHARGE = "SURCHARGE"
    BONUS = "BONUS"
    DEDUCTION = "DEDUCTION"

class PaymentMethod(str, Enum):
    TRANSFER = "TRANSFER"
    CASH = "CASH"
    CHECK = "CHECK"

# requests.py
class RequestType(str, Enum):
    CAMBIO_TURNO = "CAMBIO_TURNO"
    DIA_LIBRE = "DIA_LIBRE"
    SWAP = "SWAP"

class RequestStatus(str, Enum):
    PENDIENTE = "PENDIENTE"
    APROBADO = "APROBADO"
    RECHAZADO = "RECHAZADO"

# attendance.py
class AttendanceEventType(str, Enum):
    CHECK_IN = "CHECK_IN"
    CHECK_OUT = "CHECK_OUT"
    LATE = "LATE"
    ABSENT = "ABSENT"
    INCIDENT = "INCIDENT"

# ranking.py
class ScorePreset(str, Enum):
    BALANCEADO = "BALANCEADO"
    PUNTUALIDAD = "PUNTUALIDAD"
    ESTABILIDAD = "ESTABILIDAD"

# employee.py
class EmployeeStatus(str, Enum):
    ACTIVO = "ACTIVO"
    INACTIVO = "INACTIVO"
    SUSPENDIDO = "SUSPENDIDO"
```

### 3.2 Reglas de Validación (Turnos)

| Regla | Descripción | Config Key |
|-------|-------------|------------|
| No solapamientos | Un empleado no puede tener 2 turnos que se solapen | - |
| Horario local | Turno dentro de horario apertura/cierre del día | `schedule.hours` |
| Máx horas semanales | Suma horas ≤ máximo por semana | `rules.max_weekly_hours` |
| Descanso mínimo | Entre turnos ≥ X horas | `rules.min_rest_hours` |
| Máx días seguidos | Sin descanso ≤ X días | `rules.max_consecutive_days` |
| Disponibilidad | Empleado disponible ese día/hora | Availability |

### 3.3 Config JSON (Setting keys)

```json
{
  "schedule.hours": {
    "monday": {"open": "08:00", "close": "22:00"},
    "tuesday": {"open": "08:00", "close": "22:00"},
    ...
  },
  "rules.max_weekly_hours": 48,
  "rules.min_rest_hours": 11,
  "rules.max_consecutive_days": 6,
  "rules.overtime_threshold_hours": 8,
  "rules.overtime_multiplier": 1.5,
  "surcharges": {
    "sunday": 1.5,
    "holiday": 1.75,
    "night": 1.25
  },
  "shift_roles": ["caja", "barra", "cocina", "runner"],
  "ranking.presets": {
    "BALANCEADO": {"w_late": 0.5, "w_absent": 10, "w_inc": 5, "w_completed": 2},
    "PUNTUALIDAD": {"w_late": 2, "w_absent": 15, "w_inc": 8, "w_completed": 1},
    "ESTABILIDAD": {"w_late": 0.3, "w_absent": 20, "w_inc": 3, "w_completed": 3}
  }
}
```

### 3.4 Score Ranking (fórmula)

```
score = 100
  - (minutos_atraso * w_late)
  - (ausencias * w_absent)
  - (incidencias * w_inc)
  + (turnos_completados * w_completed)
  + bonus_consistencia (si cumple criterio)
score = clamp(score, 0, 100)
```

---

## 4. PLAN DE IMPLEMENTACIÓN POR COMMITS

| # | Commit | Contenido |
|---|--------|-----------|
| 1 | `feat: skeleton + layout ALFAJOR` | Estructura carpetas, create_app(), base.html, design-system.css, topbar/sidebar/footer, branding |
| 2 | `feat: migraciones iniciales` | Modelos SQLAlchemy, enums, migración Alembic |
| 3 | `feat: auth + RBAC` | Flask-Login, User, roles, login, decorators @role_required |
| 4 | `feat: CRUD usuarios (ADMIN)` | Blueprint auth, gestión usuarios |
| 5 | `feat: configuración JSON` | Setting, Branch, ShiftRole, /admin/config |
| 6 | `feat: empleados CRUD` | Employee, Availability, Personas |
| 7 | `feat: semanas + turnos` | ScheduleWeek, Shift, validaciones, calendario |
| 8 | `feat: solicitudes + incidencias` | ShiftRequest, AttendanceEvent, aprobaciones |
| 9 | `feat: periodos de pago` | PayPeriod, PayStatement, PayLine, cálculo |
| 10 | `feat: transacciones + conciliación` | PaymentTransaction, idempotencia, estados |
| 11 | `feat: ranking + score` | PerformanceSnapshot, presets, ficha empleado |
| 12 | `feat: dashboard + alertas` | Cards, acciones rápidas, alertas |
| 13 | `feat: exports CSV/PDF` | Reports, CSV pagos/ranking |
| 14 | `feat: auditoría` | AuditLog, hooks en acciones críticas |
| 15 | `feat: seed demo` | Admin, encargado, contabilidad, empleados, semanas, periodo |
| 16 | `docs: README completo` | Env vars, setup, migrate, run, Gunicorn |

---

## 5. PERMISOS POR ROL (MATRIZ)

| Recurso | ADMIN | ENCARGADO | CONTABILIDAD | TRABAJADOR |
|---------|-------|------------|--------------|------------|
| Usuarios CRUD | ✓ | ✗ | ✗ | ✗ |
| Config | ✓ | ✗ | ✗ | ✗ |
| Empleados | ✓ | ✓ (lectura) | ✗ | ✗ (solo propio) |
| Turnos/Semanas | ✓ | ✓ | ✗ (lectura) | ✓ (solo propios) |
| Solicitudes | ✓ | ✓ (aprobar) | ✗ | ✓ (crear propias) |
| Pagos | ✓ | ✗ | ✓ | ✗ (resumen propio) |
| Ranking completo | ✓ | ✓ | ✓ (financiero) | ✗ |
| Mi score | ✓ | ✓ | ✓ | ✓ |
| Dashboard | ✓ | ✓ | ✓ | ✓ (limitado) |

---

*Documento generado para ALFAJOR · Cosas Ricas · Seba Gatica 2026*
