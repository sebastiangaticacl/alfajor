# ANTIGRAVITY PROMPT — ALFAJOR DASHBOARD UI

Transforma la interfaz de **ALFAJOR – Sistema de Turnos del Café Cosas Ricas (Seba Gatica 2026)** en un dashboard profesional estilo SaaS (similar a Stripe).

## REGLAS
- NO modificar backend Python
- NO cambiar rutas Flask
- NO modificar lógica
- SOLO modificar HTML, CSS y JS mínimo
- Eliminar estilos inline
- Usar un solo sistema CSS global

## OBJETIVO
Que ALFAJOR se vea como un **dashboard moderno** con:

- Sidebar izquierda
- Topbar arriba
- Contenido central
- Cards KPI
- Tablas limpias
- Badges de estado
- Botones consistentes
- Formularios ordenados

## LAYOUT

### Sidebar izquierda
Debe contener navegación:

Dashboard  
Turnos  
Personas  
Pagos  
Ranking  
Configuración  

Mostrar logo textual:

ALFAJOR  
Sistema de Turnos — Café Cosas Ricas

### Topbar
Contiene:

- título de página
- usuario
- botón menú mobile

### Content
contenedor centrado max-width 1300px

## DESIGN SYSTEM

Crear archivo:

static/css/design-system.css

Definir tokens:

--bg-body  
--bg-surface  
--bg-surface-2  

--text-primary  
--text-secondary  

--border-color  

--primary  
--success  
--warning  
--danger  

--radius  
--shadow  

Crear componentes:

.card  
.kpi-card  
.table  
.badge  
.btn  
.btn-primary  
.btn-secondary  
.input  
.select  
.grid  
.alert  
.divider  

## PÁGINAS A REFACTORIZAR

templates/admin/dashboard.html  
templates/shifts/calendar.html  
templates/payroll/index.html  
templates/ranking/index.html  

Cada página debe usar los componentes del design system.

## DASHBOARD

Agregar cards KPI:

Turnos hoy  
Turnos hoy  
Pagos pendientes  
Alertas  

Agregar tabla:

Próximos turnos

## TURNOS

Barra filtros superior:

Semana  
Sucursal  
Rol  
Empleado  

Debajo tabla de turnos.

## PAGOS

Cards resumen:

Total calculado  
Total pagado  
Diferencia  
Pendientes  

Tabla por empleado.

## RANKING

Tabla ranking:

Posición  
Empleado  
Score  
Horas  
Atrasos  
Ausencias  

Score mostrado como barra horizontal.

## FOOTER GLOBAL

Agregar en todas las páginas:

Desarrollado por Seba Gatica · 2026

## RESULTADO ESPERADO

ALFAJOR debe verse como un dashboard SaaS moderno y consistente.

