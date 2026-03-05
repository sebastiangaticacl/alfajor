# ALFAJOR

Sistema de gestión de turnos, pagos y ranking para el Café Cosas Ricas.

**Desarrollado por Seba Gatica · 2026**

---

## Características

- **Turnos**: Calendario semanal, validaciones, estados (borrador/publicada/cerrada)
- **Pagos**: Periodos, liquidaciones explicables, conciliación, export CSV
- **Ranking**: Score configurable por presets, snapshots, export CSV
- **RBAC**: Admin, Encargado, Contabilidad, Trabajador
- **UI**: Tema oscuro/claro, paleta Cosas Ricas, responsive

## Requisitos

- Python 3.9+
- Docker & Docker Compose (Recomendado)
- PostgreSQL (producción) / SQLite (desarrollo local sin Docker)

## Ejecución con Docker (Recomendado)

```bash
docker-compose up --build
```
Esto inicializará la aplicación y la base de datos PostgreSQL automáticamente.

## Instalación Manual (Sin Docker)

```bash
git clone https://github.com/stvaldiviazal-create/alfajor.git
cd alfajor

python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

make install
# o: pip install -r requirements.txt

cp .env.example .env
# Editar .env con SECRET_KEY y DATABASE_URL
```

## Base de datos

```bash
make migrate
make seed
```

## Ejecución

**Desarrollo:**
```bash
make run
```

**Producción:**
```bash
make run-prod
```

## Variables de entorno

| Variable     | Descripción              | Default           |
|--------------|--------------------------|-------------------|
| FLASK_APP    | Módulo de la aplicación  | alfajor           |
| FLASK_ENV    | Entorno                  | development       |
| SECRET_KEY   | Clave secreta Flask      | (requerido)       |
| DATABASE_URL | Conexión a base de datos | sqlite:///alfajor.db |

## Estructura del proyecto

```
alfajor/
├── alfajor/           # Aplicación Flask
│   ├── blueprints/    # Módulos (auth, admin, shifts, payroll...)
│   ├── models/        # SQLAlchemy
│   ├── services/      # Lógica de negocio
│   └── templates/
├── migrations/        # Alembic
├── scripts/           # Seed, utilidades
└── docs/              # Documentación
```

## Licencia

Proyecto privado · Café Cosas Ricas
