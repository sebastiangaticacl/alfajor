# ALFAJOR

**Sistema de Turnos del Café Cosas Ricas**

Desarrollado por Seba Gatica · 2026

---

## Requisitos

- Python 3.9+
- PostgreSQL (opcional, SQLite para desarrollo)

## Setup

```bash
# Clonar / entrar al proyecto
cd CRT

# Entorno virtual
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# Dependencias
pip install -r requirements.txt

# Variables de entorno
cp .env.example .env
# Editar .env: SECRET_KEY, DATABASE_URL (opcional)
```

## Base de datos

```bash
# Crear tablas (SQLite por defecto en dev)
FLASK_APP=alfajor flask db upgrade

# Seed demo (usuarios, empleados, semanas, periodo)
python scripts/seed.py
```

## Ejecutar

```bash
FLASK_APP=alfajor flask run
```

O con Gunicorn (producción):

```bash
gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app
```

## Usuarios demo (después del seed)

| Rol           | Email                      | Contraseña |
|---------------|----------------------------|------------|
| Admin         | admin                      | admin      |
| Encargado     | encargado@cosasricas.local | enc123     |
| Contabilidad  | contabilidad@cosasricas.local | cont123  |
| Trabajador    | juan@cosasricas.local      | trab123    |

## Migraciones

```bash
FLASK_APP=alfajor flask db migrate -m "descripción"
FLASK_APP=alfajor flask db upgrade
```

## Variables de entorno

| Variable     | Descripción                    | Default        |
|--------------|--------------------------------|----------------|
| FLASK_APP    | Módulo de la app               | alfajor        |
| FLASK_ENV    | development / production       | development    |
| SECRET_KEY   | Clave secreta Flask            | (obligatorio)  |
| DATABASE_URL | PostgreSQL o SQLite            | sqlite:///alfajor.db |

## Estructura

- `alfajor/` - Aplicación Flask
- `alfajor/models/` - Modelos SQLAlchemy
- `alfajor/blueprints/` - Rutas por módulo
- `alfajor/services/` - Lógica de negocio
- `alfajor/templates/` - Jinja2
- `alfajor/static/` - CSS, JS
- `migrations/` - Alembic
- `scripts/` - Seed, utilidades

## Módulos

- **Auth**: Login, usuarios (ADMIN)
- **Dashboard**: Resumen, alertas
- **Turnos**: Calendario, semanas, validaciones
- **Personas**: Empleados, disponibilidad
- **Solicitudes**: Cambios, aprobaciones
- **Pagos**: Periodos, liquidaciones, conciliación, CSV
- **Ranking**: Score, presets, CSV
- **Config**: Horarios, reglas, sucursales

---

Ver `docs/PLAN_PRIMER_PASO.md` para el plan completo.
