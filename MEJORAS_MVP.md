# MediTrack Pro — Especificación de mejoras MVP
# Este documento describe lo que se construyó en el prototipo HTML/JS.
# Sirve de base para el sistema real Flask + SQLite + CLAUDE.md.

---

## Qué es este sistema

Sistema de gestión de equipos médicos terapéuticos (ej. dispositivos de electroterapia, ultrasonido, láser) que se asignan temporalmente a pacientes en consulta o domicilio. Registra quién usó cada equipo, cuándo, en qué condiciones y qué se facturó.

---

## Stack del MVP (prototipo actual)

- HTML + CSS + JavaScript vanilla — un solo archivo `index.html`
- Datos en memoria (`const DB = {...}`) — se pierden al recargar
- SheetJS (CDN) para importar Excel
- Sin backend, sin base de datos persistente

## Stack objetivo (sistema real)

- **Backend:** Flask + Python 3
- **BD:** SQLite en modo WAL (igual que TecnoAuladom)
- **Frontend:** Jinja2 + CSS vars (mismo patrón de sistema escolar)
- **Extras:** openpyxl para Excel, ReportLab para PDF, autenticación por roles

---

## Módulos implementados en el MVP

### 1. Dashboard
- Métricas: pacientes únicos, activos ahora, máquinas operativas, facturación del mes
- Tabla de pacientes activos con máquina asignada
- Grid visual de estado de máquinas (verde = con paciente, gris = libre)
- Últimas colocaciones y resumen de facturación por paciente

### 2. Pacientes
- Lista deduplicada por nombre con búsqueda y filtro por estado
- Perfil detallado con dos pestañas: **Datos** e **Historial de colocaciones**
- Acciones rápidas por fila: ver, editar, asignar equipo, eliminar

### 3. Pacientes Activos
- Tabla de registros con estatus `Activo`
- Botón de retiro directo por fila

### 4. Registro Completo
- Tabla de todas las colocaciones (historial completo)
- Filtros: búsqueda libre, estatus, mes
- Botón exportar (stub en MVP, real en Flask)

### 5. Inventario de Máquinas
- Tabla con estado, paciente actual, historial de usos
- Historial por máquina con condiciones de entrega y retorno
- Acciones: ver detalle, asignar paciente, retirar, editar, eliminar

### 6. Facturación
- Totales por mes y por paciente
- Tabla de colocaciones cobradas
- Saldo pendiente detectado por nota en el campo `motivo`

---

## Funcionalidades construidas en la sesión actual

### A · Registro de condiciones de uso (máquina ↔ paciente)

**Cuándo se activa:** Al crear una colocación nueva.

**Campos capturados:**
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `modo_uso` | select | Consulta / Domicilio / Hospitalario |
| `condicion_salida` | select | Óptima / Buena / Requiere revisión |
| `parametros` | textarea | Intensidad, frecuencia, tiempo de sesión |
| `notas` | textarea | Observaciones clínicas |
| `fecha_retiro` | date | Se llena al retirar el equipo |
| `condicion_retorno` | select | Óptima / Buena / Con daños leves / Requiere revisión / Dañado |
| `observaciones_retiro` | textarea | Notas del retiro |

**Lógica al retirar:**
- Si `condicion_retorno = Dañado` → máquina pasa a `Fuera de Servicio`
- Si `condicion_retorno = Requiere revisión` → máquina pasa a `Requiere Revisión`

**Se muestra en:**
- Historial de máquinas (columnas: Cond. salida, Fecha retiro, Cond. retorno)
- Historial del paciente (mismas columnas)
- Panel info de la máquina (campos: Modo de uso, Cond. al entregar, Parámetros)

---

### B · Asignar equipo desde el perfil del paciente

**Flujo:**
1. Abrir perfil de un paciente (clic en fila o botón ojo)
2. Click en **"Asignar equipo"** → modal dedicado
3. Tarjetas visuales de máquinas disponibles (click = selección resaltada)
4. Formulario: fecha, N° colocación, área de lesión, modo de uso, condición, facturación, parámetros, observaciones
5. Guardar → registra la colocación + marca la máquina como en uso

**Acceso también desde:**
- Botón ícono de máquina en tabla de Pacientes (fila)
- Botón "Asignar" en tabla de Máquinas (fila)
- Botón "Asignar paciente" en detalle de máquina

**Regla de negocio:** Si el paciente ya tiene un registro activo, se desactiva automáticamente antes de crear el nuevo.

---

### C · Editar perfil de paciente existente

**Campos editables:**
- Nombre completo (si cambia, se actualiza en todos sus registros históricos)
- Cédula, sexo, edad
- Área de lesión principal
- Dirección / Centro
- Teléfono 1, Teléfono 2
- Dr. que refiere
- ARS / Seguro

**Arquitectura:** Los cambios se guardan en `DB.pacientes_master[nombre]` (objeto separado de los registros). `getPacientesUnicos()` hace merge al momento de renderizar.

**Acceso:** Botón lápiz en tabla de Pacientes / botón "Editar perfil" en detalle del paciente.

**Desde el editor** se puede saltar directo a "Asignar equipo" sin cerrar y reabrir.

---

### D · Importar desde Excel

**Tecnología:** SheetJS (`xlsx.full.min.js` vía CDN).

**Formato esperado (columnas en orden):**

| # | Columna | Ejemplo | Requerido |
|---|---------|---------|-----------|
| 1 | Nombre | Sobeida Mora | Sí |
| 2 | Cédula | 024-0014327-3 | No |
| 3 | Sexo | F | No |
| 4 | Edad | 45 | No |
| 5 | Área de lesión | Pierna Izquierda | No |
| 6 | Dirección | Los Llanos San Pedro | No |
| 7 | Teléfono 1 | 829-469-2280 | No |
| 8 | Teléfono 2 | 809-000-0000 | No |
| 9 | Dr. que refiere | Juan Mendez | No |
| 10 | ARS | Privado | No |
| 11 | Fecha | 2026-05-03 | Sí |
| 12 | ID Máquina | MAQ01 | No |
| 13 | N° Colocación | 1era Colocacion | No |
| 14 | Monto (DOP) | 13000 | No |

**Comportamiento:**
- Filas sin Nombre o Fecha se omiten (se indica cuántas)
- Si el paciente ya existe: actualiza su perfil maestro con los nuevos datos
- Si el ID Máquina no existe en el sistema: se ignora silenciosamente
- Muestra preview de las primeras 10 filas antes de confirmar
- Soporte drag & drop + selector de archivo

**Acceso:** Botón "Importar Excel" en topbar (visible en vistas Pacientes y Registro completo).

---

### E · Eliminar paciente

**Modal de confirmación muestra:**
- Cantidad de registros históricos que se van a borrar
- Aviso si tiene un equipo activo en ese momento

**Al confirmar:**
1. Libera la máquina asignada (si aplica) → `paciente_actual = null`
2. Borra todos sus registros del array `DB.registros`
3. Borra su entrada en `DB.pacientes_master`

**Acceso:** Botón papelera en tabla de Pacientes / botón "Eliminar paciente" en detalle.

---

### F · Eliminar máquina

**Modal de confirmación muestra:**
- En cuántos registros históricos aparece
- Aviso rojo si hay un paciente activo con esa máquina

**Al confirmar:**
1. Desactiva el registro activo si lo hay
2. Limpia el campo `maquina` en todos los registros históricos (quedan sin asignar, no se borran)
3. Elimina la máquina del array `DB.maquinas`

**Acceso:** Botón papelera en tabla de Máquinas / botón "Eliminar" en detalle de máquina.

---

## Modelo de datos (MVP → Flask/SQLite)

### Tabla `pacientes`
```sql
CREATE TABLE pacientes (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre      TEXT NOT NULL,
    cedula      TEXT DEFAULT '',
    sexo        TEXT DEFAULT '',          -- 'M' | 'F' | ''
    edad        INTEGER,
    lesion      TEXT DEFAULT '',          -- área de lesión principal
    direccion   TEXT DEFAULT '',
    tel1        TEXT DEFAULT '',
    tel2        TEXT DEFAULT '',
    dr_refiere  TEXT DEFAULT '',
    ars         TEXT DEFAULT 'Privado',
    activo      INTEGER DEFAULT 1,
    created_at  TEXT DEFAULT (datetime('now'))
);
```

### Tabla `maquinas`
```sql
CREATE TABLE maquinas (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo      TEXT UNIQUE NOT NULL,     -- 'MAQ01', 'MAQ02', etc.
    nombre      TEXT NOT NULL,
    serial      TEXT DEFAULT '',
    estado      TEXT DEFAULT 'Operativa', -- 'Operativa' | 'Requiere Revisión' | 'Fuera de Servicio' | 'Sin registrar'
    ubicacion   TEXT DEFAULT '',          -- 'Consulta' | 'Domicilio'
    notas       TEXT DEFAULT '',
    activo      INTEGER DEFAULT 1,
    created_at  TEXT DEFAULT (datetime('now'))
);
```

### Tabla `colocaciones` (núcleo del sistema)
```sql
CREATE TABLE colocaciones (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    paciente_id         INTEGER NOT NULL REFERENCES pacientes(id),
    maquina_id          INTEGER REFERENCES maquinas(id),
    fecha_inicio        TEXT NOT NULL,               -- ISO: '2026-05-30'
    fecha_retiro        TEXT,                        -- NULL si sigue activo
    numero_colocacion   TEXT DEFAULT '',             -- '1era Colocacion', '2da', etc.
    lesion              TEXT DEFAULT '',             -- puede diferir del perfil base
    modo_uso            TEXT DEFAULT 'Consulta',     -- 'Consulta' | 'Domicilio' | 'Hospitalario'
    condicion_salida    TEXT DEFAULT 'Óptima',       -- estado del equipo al entregar
    condicion_retorno   TEXT DEFAULT '',             -- estado del equipo al devolver
    parametros          TEXT DEFAULT '',             -- configuración del equipo
    notas               TEXT DEFAULT '',             -- observaciones clínicas
    observaciones_retiro TEXT DEFAULT '',            -- notas al retirar
    estatus             TEXT DEFAULT 'Activo',       -- 'Activo' | 'Desactivado'
    facturacion         REAL DEFAULT 0,
    dr_refiere          TEXT DEFAULT '',
    ars                 TEXT DEFAULT 'Privado',
    created_at          TEXT DEFAULT (datetime('now'))
);
```

### Tabla `mensajes_contacto` (futuro)
```sql
CREATE TABLE mensajes_contacto (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    paciente_id INTEGER REFERENCES pacientes(id),
    tipo        TEXT DEFAULT 'nota',      -- 'nota' | 'recordatorio' | 'incidencia'
    cuerpo      TEXT NOT NULL,
    created_at  TEXT DEFAULT (datetime('now'))
);
```

---

## Rutas Flask objetivo

```
GET  /                          → dashboard
GET  /pacientes                 → lista de pacientes
GET  /pacientes/<id>            → detalle del paciente (historial)
POST /pacientes/nuevo           → crear paciente
POST /pacientes/<id>/editar     → actualizar perfil
POST /pacientes/<id>/eliminar   → eliminar paciente y sus registros

GET  /maquinas                  → inventario
GET  /maquinas/<id>             → detalle con historial
POST /maquinas/nueva            → agregar máquina
POST /maquinas/<id>/editar      → actualizar
POST /maquinas/<id>/eliminar    → eliminar máquina

GET  /colocaciones              → registro completo
POST /colocaciones/nueva        → crear colocación (asignar equipo)
POST /colocaciones/<id>/retirar → registrar retiro con condición

GET  /facturacion               → resumen de facturación

POST /importar/excel            → recibir archivo Excel, procesar con openpyxl
GET  /exportar/excel            → generar Excel del registro con openpyxl
```

---

## Lógicas de negocio críticas

1. **Un paciente activo a la vez:** Si se asigna una nueva colocación a un paciente con registro activo, el anterior se cierra automáticamente.

2. **Estado de máquina automático:** Si la condición de retorno es `Dañado` → estado = `Fuera de Servicio`. Si es `Requiere revisión` → estado = `Requiere Revisión`.

3. **Máquina disponible:** Una máquina está disponible si no tiene ninguna colocación con `estatus = Activo`.

4. **Paciente deduplicado:** En la vista de Pacientes, cada persona aparece una sola vez aunque tenga múltiples colocaciones. Se agrega el total de colocaciones y el monto acumulado.

5. **Importar no duplica:** Al importar desde Excel, si el paciente ya existe (por nombre o cédula), se actualiza su perfil, no se crea uno nuevo.

---

## Pendientes para el sistema real

| # | Pendiente | Prioridad |
|---|-----------|-----------|
| P1 | Autenticación con roles (admin, operador, solo lectura) | Alta |
| P2 | Persistencia real en SQLite | Alta |
| P3 | Exportar a Excel con openpyxl (registro filtrado) | Alta |
| P4 | Generación de recibo/factura PDF por colocación (ReportLab) | Media |
| P5 | Módulo de mantenimiento preventivo de máquinas | Media |
| P6 | Recordatorios y seguimiento (pacientes con muchos días activos) | Media |
| P7 | Reportes: máquinas más usadas, pacientes más frecuentes | Baja |
| P8 | Integración ECF/DGII para facturación electrónica | Baja |
| P9 | App móvil o PWA para operadores en domicilio | Baja |

---

## Notas de campo — uso real del sistema

> Anotar aquí mientras se usa el MVP: campos que faltan, comportamientos raros,
> flujos confusos, cosas que se repiten mucho. Esto alimenta el backlog del Flask.

### Campos que faltan o sobran

| Módulo | Campo / situación | Acción sugerida |
|--------|-------------------|-----------------|
| — | — | — |

### Comportamientos que no funcionan como se espera

| Fecha | Descripción | Prioridad |
|-------|-------------|-----------|
| — | — | — |

### Flujos que se usan más (para priorizar en Flask)

- [ ] ...
- [ ] ...

### Backups realizados

| Fecha | Archivo | Observación |
|-------|---------|-------------|
| — | — | — |

---

## Cómo usar este archivo con CLAUDE.md

Cuando se cree el proyecto Flask real, este archivo se convierte en la sección
`## Módulos completados` y `## En desarrollo` del CLAUDE.md del proyecto.

El modelo de datos de arriba es el schema inicial de `db.py` / `init_db()`.
Las rutas son el punto de partida de `app.py` o los blueprints en `/routes/`.

```
medicalsol/
├── CLAUDE.md              ← contexto del proyecto para Claude Code
├── MEJORAS_MVP.md         ← este archivo (referencia de diseño)
├── app.py                 ← factory Flask
├── db.py                  ← init_db() + helpers por tabla
├── routes/
│   ├── pacientes.py
│   ├── maquinas.py
│   ├── colocaciones.py
│   └── facturacion.py
├── templates/
│   ├── base.html
│   ├── dashboard.html
│   ├── pacientes.html
│   └── ...
└── static/
    └── ...
```

---

*MVP construido: Junio 2026 · Erick Hernández · MediTrack Pro*
