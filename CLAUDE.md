# CLAUDE.md — MediTrack Pro

> Archivo de contexto del proyecto para Claude Code (`cc`).
> Léelo antes de tocar cualquier archivo del proyecto.

---

## Descripción del proyecto

**MediTrack Pro** es un sistema de gestión de activos médicos y pacientes, desarrollado para un negocio de terapias médicas en Santo Domingo, República Dominicana. El negocio presta máquinas terapéuticas a pacientes en sus domicilios o en centros médicos, y registra cada colocación con su facturación correspondiente.

El sistema reemplaza un flujo manual en Excel (archivo: `Registro_Pacientes_Mayo_2026-Activos.xlsx`) y lo convierte en una aplicación web estructurada, conectada y expandible.

**Estado actual:** Demo funcional en un solo archivo HTML (`index.html`) con datos reales importados del Excel original. Base de datos en memoria (JavaScript). Sin backend aún.

---

## Stack tecnológico

| Capa | Tecnología | Notas |
|------|-----------|-------|
| Frontend actual | HTML + CSS + Vanilla JS | Un solo archivo `index.html` |
| Frontend futuro | React + Vite + TypeScript | Migración planificada |
| Backend planificado | Python 3.11 + Flask | Mismo patrón que Facturar.do |
| Base de datos planificada | SQLite → PostgreSQL | SQLite para dev, Postgres para producción |
| Hosting planificado | Render.com | Igual que Facturar.do |
| Íconos | Tabler Icons (webfont CDN) | `ti ti-*` |
| Colores de marca | Crimson `#7B1A1A`, Negro `#1A1A1A`, Blanco `#FFFFFF` | Paleta EHA personal |

---

## Estructura actual del proyecto

```
meditrack-pro/
├── index.html          # App completa (frontend + datos en memoria)
├── README.md           # Instrucciones para correr el demo
├── CLAUDE.md           # Este archivo
└── meditrack-plantilla.xlsx  # Plantilla de importación (generada)
```

### Estructura planificada (fase backend)

```
meditrack-pro/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── views/
│   │   │   ├── Dashboard.tsx
│   │   │   ├── Pacientes.tsx
│   │   │   ├── Activos.tsx
│   │   │   ├── Registro.tsx
│   │   │   ├── Maquinas.tsx
│   │   │   └── Facturacion.tsx
│   │   ├── api.ts          # Llamadas al backend
│   │   └── main.tsx
│   └── index.html
├── backend/
│   ├── app.py              # Flask app principal
│   ├── models.py           # SQLAlchemy models
│   ├── routes/
│   │   ├── pacientes.py
│   │   ├── maquinas.py
│   │   ├── registros.py
│   │   └── facturacion.py
│   ├── importar.py         # Parser Excel/XML
│   └── requirements.txt
└── CLAUDE.md
```

---

## Módulos del sistema

### 1. Dashboard
Vista principal con métricas en tiempo real:
- Pacientes únicos totales
- Activos con máquina asignada ahora
- Máquinas operativas vs en uso
- Facturación del mes

### 2. Pacientes (Clientes)
Lista deduplicada de todos los pacientes únicos.
- Un paciente puede tener múltiples colocaciones (filas en el registro histórico)
- La deduplicación se hace por **nombre** (en producción será por cédula)
- Cada paciente tiene ficha con: datos personales, historial de colocaciones, total facturado
- Acciones: nueva colocación, activar/desactivar

### 3. Activos ahora
Subvista filtrada: solo pacientes con `estatus = Activo`.
- Fuente: hoja `Pacientes Activos` del Excel original (usaba `FILTER()` de Google Sheets)
- En el sistema: filtrado en tiempo real desde `DB.registros`
- Acción rápida: "Retirar" desactiva al paciente y libera su máquina

### 4. Registro Completo
Todas las filas del Excel original — cada fila es una colocación.
- Filtros: nombre/cédula, estado (Activo/Desactivado), mes
- Exportar a Excel (pendiente en producción)
- Fuente del Excel: hoja `Registro Pacientes`, fila 4 = encabezados, fila 5 en adelante = datos

### 5. Máquinas (Inventario)
Las 8 máquinas terapéuticas del negocio.
- Fuente del Excel: hoja `Inventario de Maquinas`
- Cada máquina tiene: nombre, serial, estado, paciente actual (si aplica), historial de todos los pacientes que la usaron
- Conexión en tiempo real: asignar paciente ↔ aparece en "Activos" ↔ máquina marcada como ocupada
- Acciones: asignar, retirar, editar, nueva máquina

### 6. Facturación
- Resumen de facturación por paciente
- Saldos pendientes (ej: Ramón Campusano — RD$35,000 pendiente)
- Base para futura emisión de e-CF (Comprobante Fiscal Electrónico) vía DGII
- **Pendiente:** integración con ECF SSD como PSFE ($3/1,000 e-CFs)

---

## Modelo de datos

### Máquina
```js
{
  id: 'MAQ01',             // MAQ + número con cero
  nombre: 'Maquina No. 1', // Nombre original del Excel
  serial: '250619003',     // Serial del fabricante
  estado: 'Operativa',     // Operativa | Requiere Revisión | Fuera de Servicio | Sin registrar
  ubicacion: 'Consulta',   // Consulta | Domicilio | ...
  paciente_actual: null,   // nombre del paciente si está activa, null si disponible
  notas: ''
}
```

### Registro (Colocación)
```js
{
  id: 'R001',
  fecha: '2026-05-05',           // ISO date string
  nombre: 'Sebastian Adolfo...',  // Nombre completo del paciente
  cedula: '001-0553575-1',        // Cédula dominicana
  sexo: 'M',                      // M | F | ''
  edad: 83,                       // número o null
  lesion: 'Pierna Derecha',       // Área de lesión tratada
  direccion: 'Hospital...',       // Domicilio o centro médico
  tel1: '829-702-2598 (Kelvin)',  // Incluye nombre del contacto entre paréntesis
  tel2: '',
  dr_refiere: '',                 // Médico que refirió al paciente
  ars: 'Privado',                 // ARS o 'Privado'
  maquina: 'MAQ01',               // ID de la máquina | '' si no asignada
  estatus: 'Activo',              // Activo | Desactivado
  motivo: '2da Colocacion',       // Número de colocación o motivo de retiro
  facturacion: 13000              // Monto cobrado en DOP, 0 si no cobrado
}
```

### Vista Paciente Único (derivada)
No se almacena — se calcula en runtime desde `DB.registros`:
```js
{
  ...datosUltimoRegistro,
  colocaciones: [...todosLosRegistros],  // array de todos sus registros
  total_facturado: 52000,                // suma de facturacion
  estatus: 'Activo'  // si cualquier registro tiene estatus Activo
}
```

---

## Reglas de negocio importantes

1. **Una máquina = un paciente a la vez.** Si una máquina tiene `paciente_actual !== null`, no puede asignarse a otro.
2. **Múltiples colocaciones por paciente.** Cada visita/sesión es una fila nueva en el registro. No se editan filas — se agregan.
3. **Deduplicación por cédula** (en producción). En el demo actual se deduplica por nombre porque varios registros no tienen cédula.
4. **Montos en DOP** (pesos dominicanos). Sin decimales en la presentación. Usar `Intl.NumberFormat('es-DO', {currency:'DOP'})`.
5. **ITBIS 18%** aplica a los servicios. Se calculará al momento de emitir el e-CF.
6. **Saldo pendiente** (ej: Ramón Campusano): el motivo de la colocación incluye `"Resta RD$35,000.00"`. En producción esto debe ser un campo separado `saldo_pendiente: number`.
7. **Fechas**: el Excel almacenaba números seriales de fecha (ej: 46172). Al importar se convierten a ISO date string `YYYY-MM-DD`.

---

## Conexiones entre módulos

```
Máquinas ──────────────────────────────────────────┐
   │ maquina.id ↔ registro.maquina                  │
   ↓                                                 │
Registro completo ──────────────────── Activos ahora│
   │ agrupa por nombre/cédula                        │
   ↓                                                 │
Pacientes (vista única) ────────── Dashboard KPIs ──┘
   │ suma facturación
   ↓
Facturación ────── (futuro) ────── ECF SSD / DGII
```

---

## Próximos pasos (roadmap)

### Fase 1 — Demo local (ACTUAL ✅)
- [x] Frontend HTML+CSS+JS en un solo archivo
- [x] Datos reales importados del Excel original
- [x] 6 módulos: Dashboard, Pacientes, Activos, Registro, Máquinas, Facturación
- [x] Conexión en tiempo real entre módulos (asignar/retirar máquina)
- [x] Modales de detalle con historial por paciente y por máquina
- [x] Formularios: nueva colocación, nuevo paciente, nueva máquina

### Fase 2 — Backend Flask (PENDIENTE)
- [ ] Crear `backend/app.py` con Flask + SQLAlchemy
- [ ] Modelos: `Maquina`, `Paciente`, `Colocacion`, `Factura`
- [ ] API REST: CRUD completo para cada modelo
- [ ] Parser de importación: leer `Registro Pacientes` y `Inventario de Maquinas` del Excel
- [ ] Endpoint `POST /importar/excel` — recibe el archivo y procesa las 3 hojas
- [ ] Migrar frontend a React + Vite + TypeScript
- [ ] Despliegue en Render.com

### Fase 3 — Facturación DGII (PENDIENTE)
- [ ] Integración con ECF SSD como PSFE
- [ ] Generar e-CF tipo 01 (Crédito Fiscal) y 02 (Consumidor Final)
- [ ] Reportes 606 (compras) y 607 (ventas) para la DGII
- [ ] Campo `saldo_pendiente` en modelo `Colocacion`
- [ ] Historial de pagos parciales

### Fase 4 — Funciones avanzadas (FUTURO)
- [ ] Agenda de citas / mantenimiento de máquinas
- [ ] Alertas por WhatsApp cuando vence una colocación
- [ ] App móvil (Héctor Soriano — Flutter o React Native)
- [ ] Multi-rubro: el sistema es genérico, puede adaptarse a otros tipos de activos físicos (no solo médico)
- [ ] Exportar registro filtrado a Excel (mismo formato del original)

---

## Instrucciones para Claude Code

### Al abrir el proyecto
```bash
# No requiere instalación — es HTML puro
open index.html   # macOS
```

### Al modificar `index.html`
1. Todo el estado vive en el objeto `DB` al inicio del `<script>`
2. Las vistas se renderizan en `<div id="content">` vía `innerHTML`
3. Los modales van en `<div id="modal-root">`
4. El router es la función `go(view)` — agrega aquí si creas nuevas vistas
5. `getPacientesUnicos()` es la función clave que deduplica el registro histórico
6. Después de cualquier operación que modifique `DB`, llama a la función de render del view actual

### Convenciones de código
- Funciones de render: `renderXxx()` — escriben en `#content`
- Funciones de modal: `abrirXxx()` / `verXxxDetalle()` — escriben en `#modal-root`
- Funciones de guardar: `guardarXxx()` — modifican `DB` y cierran modal
- IDs de inputs en modales: prefijo de 2-3 letras + guion + campo (ej: `col-pac`, `np-nombre`)
- Nunca usar `position:fixed` — rompe el layout del iframe
- Colores: SOLO usar variables CSS (`--brand`, `--ok`, `--warn`, `--danger`, etc.)
- Nunca hardcodear colores hex en el HTML

### Al agregar un nuevo módulo de vista
```js
// 1. Agregar ítem en el sidebar
<div class="nav-item" onclick="go('nuevo')" id="nav-nuevo">
  <i class="ti ti-xxx"></i><span>Nuevo módulo</span>
</div>

// 2. Agregar al objeto TITLES y NUEVO_LABELS en el router
const TITLES = { ..., nuevo: 'Nombre del módulo' }
const NUEVO_LABELS = { ..., nuevo: 'Crear nuevo' }

// 3. Agregar función de render
function renderNuevo() {
  document.getElementById('content').innerHTML = `...`
}

// 4. Registrar en el router go()
({..., nuevo: renderNuevo})[v]?.()
```

---

## Contexto del negocio

- **Tipo de negocio:** Terapia médica con máquinas de presoterapia / terapia de compresión (basado en los datos — `área de lesión`, `colocaciones`, retiro de máquinas)
- **Operación:** Las máquinas se colocan en pacientes en domicilio o centro médico. Un técnico las instala y retira. Cada colocación = una sesión de tratamiento con cobro.
- **Clientes:** Todos `Privado` en el dataset actual. Posibles ARS en el futuro.
- **Volumen:** ~32 registros en mayo 2026, ~15 pacientes únicos, 8 máquinas
- **Facturación típica:** RD$13,000 – RD$22,000 por colocación
- **Flujo típico:** Paciente llama → se agenda colocación → técnico instala máquina → máquina queda en casa X días → técnico retira → se cobra
- **Adaptable a otros rubros:** el sistema es genérico (activos físicos + clientes + colocaciones/usos). Se puede usar para alquiler de equipos de construcción, audiovisual, etc.

---

## Archivos de referencia

| Archivo | Descripción |
|---------|-------------|
| `Registro_Pacientes_Mayo_2026-Activos.xlsx` | Excel original del cliente — fuente de verdad de todos los datos |
| `index.html` | Demo completo actual |
| `meditrack-plantilla.xlsx` | Plantilla generada para importación futura |
| `~/.claude/CLAUDE.md` | Configuración global de Claude Code (dev-debug-ia, convenciones) |

---

*Proyecto: MediTrack Pro · Cliente: Sector médico, Santo Domingo RD · Dev: Erick Hernández Arias · Inicio: junio 2026*
