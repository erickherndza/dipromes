# CLAUDE.md — DIPROMES

> Archivo de contexto del proyecto para Claude Code (`cc`).
> Léelo antes de tocar cualquier archivo del proyecto.

---

## Descripción del proyecto

**DIPROMES** (antes MediTrack Pro) es un sistema de gestión de activos médicos y pacientes para **Dipromes Terapias VAC**, negocio de terapia de compresión/presoterapia en Santo Domingo, República Dominicana. El negocio coloca máquinas terapéuticas en pacientes en domicilio o centros médicos y registra cada colocación con su facturación.

El sistema reemplazó un flujo manual en Excel y está desplegado en producción en Render.com con base de datos PostgreSQL.

**Estado actual:** Aplicación web full-stack en producción. Backend Flask + PostgreSQL en Render. Frontend HTML+CSS+Vanilla JS en un solo archivo `index.html`.

**URL de producción:** `https://dipromes.onrender.com`
**Repositorio:** `https://github.com/erickherndza/dipromes`

---

## Stack tecnológico

| Capa | Tecnología | Notas |
|------|-----------|-------|
| Frontend | HTML + CSS + Vanilla JS | Un solo archivo `index.html` |
| Backend | Python 3.11 + Flask | `backend/app.py` |
| ORM | SQLAlchemy (Flask-SQLAlchemy 3.1) | Modelos en `backend/models.py` |
| Base de datos | SQLite (dev local) → PostgreSQL (Render) | Driver: `pg8000` (pure Python, sin C) |
| Hosting | Render.com (free tier) | `render.yaml` + `wsgi.py` |
| Servidor WSGI | Gunicorn 22 | 2 workers, timeout 60s |
| Íconos | Tabler Icons (webfont CDN) | `ti ti-*` |
| Colores de marca | Crimson `#7B1A1A`, Negro `#1A1A1A`, Blanco `#FFFFFF` | Paleta EHA |
| Export | openpyxl (Excel/CSV), HTML printable (PDF via browser) | Sin reportlab |

---

## Estructura del proyecto

```
dipromes/
├── index.html              # Frontend completo (SPA vanilla JS)
├── wsgi.py                 # Entry point Gunicorn — init DB en first request
├── render.yaml             # Configuración Render.com
├── CLAUDE.md               # Este archivo
├── backend/
│   ├── app.py              # Flask app: rutas, auth, seguridad
│   ├── models.py           # SQLAlchemy models
│   ├── exportar.py         # Helpers: Excel, CSV, PDF/HTML, consent_html
│   └── requirements.txt    # 6 paquetes (sin C extensions)
└── meditrack-plantilla.xlsx  # Plantilla de importación
```

---

## Módulos del sistema

### 1. Dashboard
Métricas en tiempo real: pacientes únicos, activos ahora, máquinas operativas, facturación del mes.

### 2. Pacientes
Lista deduplicada por nombre (→ por cédula en el futuro). Ficha con historial de colocaciones y total facturado.

### 3. Colocaciones (Activos ahora)
Filtrado en tiempo real: `estatus = Activo`. Acción rápida de retiro.

### 4. Registro Completo
Todas las colocaciones. Filtros por nombre/cédula, estado, mes. Exportar a Excel/CSV/PDF.

### 5. Máquinas (Inventario)
8 máquinas terapéuticas. Asignación 1:1 con paciente activo. CRUD completo.

### 6. Conduces de Descargo (Facturación)
Resumen de facturación y saldos pendientes por paciente.

### 7. Consentimiento Informado ← NUEVO
- Módulo en sidebar: **Documentos → Consentimiento**
- Tabla `consentimientos` en PostgreSQL
- Pestaña **Registros guardados**: listado de consentimientos con estado Firmado/Pendiente, botones Imprimir y Eliminar
- Pestaña **Nuevo consentimiento**: formulario con autocompletar desde pacientes existentes, campos: nombre, cédula, edad, dirección, teléfono, médico, centro de salud, fecha firma, firmado (checkbox), notas
- `GET /api/consentimientos/<id>/pdf` → genera HTML A4 server-side (sin reportlab), fiel al documento `consentimiento-VAC.docx` original
- Botón **"Formulario en blanco"** en topbar y en la vista

### 8. Mapa GPS
Vista de pacientes activos con coordenadas.

### 9. Usuarios (admin)
Gestión de usuarios del sistema. Solo visible para rol `admin`.

---

## Seguridad implementada

| Aspecto | Implementación |
|---------|---------------|
| Autenticación | Flask `session` con cookie httpOnly firmada (SECRET_KEY fija en Render env) |
| Contraseñas | `werkzeug` scrypt hash — auto-upgrade de plaintext en primer login |
| Autorización | `@login_required` / `@admin_required` en todas las rutas |
| Rate limiting | In-memory: 10 req/min por IP en `/api/auth/login` |
| CORS | Restringido a `ALLOWED_ORIGIN` en producción |
| Headers | X-Frame-Options, X-Content-Type-Options, HSTS, Referrer-Policy |
| CSP | `Content-Security-Policy` con nonce por request (`secrets.token_urlsafe`) — `before_request` genera nonce, `after_request` emite header, ruta `/` lo inyecta en el `<script>` inline |
| SRI | Todos los recursos CDN (Tabler Icons @3.46.0, Leaflet CSS/JS, XLSX.js) tienen `integrity="sha384-..."` y `crossorigin="anonymous"` |
| XSS | Función `esc()` en todo innerHTML del frontend |
| Reset emergencia | `ADMIN_RESET_PASS` env var → eliminar después de usar |

**Mozilla Observatory:** A+ (100/100) — auditado agosto 2026.

**Variables de entorno requeridas en Render:**
- `DATABASE_URL` — provista automáticamente por Render PostgreSQL
- `SECRET_KEY` — string fijo y largo (crítico para sesiones multi-worker)
- `ALLOWED_ORIGIN` — `https://dipromes.onrender.com`
- `ADMIN_PASS` / `DR1_PASS` — contraseñas iniciales (solo aplican en seed)

---

## Modelo de datos

### Maquina (`maquinas`)
```python
id: String(10) PK          # MAQ01, MAQ02…
nombre: String(100)
serial: String(50)
estado: String(50)         # Operativa | Requiere Revisión | Fuera de Servicio
ubicacion: String(100)
notas: Text
```

### Registro (`registros`) — una fila por colocación
```python
id: String(10) PK          # R001, R002…
fecha: String(10)          # YYYY-MM-DD
nombre: String(200)
cedula: String(30)
sexo: String(1)            # M | F
edad: Integer
lesion: String(200)
direccion: String(300)
tel1, tel2: String(100)
dr_refiere: String(200)
ars: String(100)           # Privado | nombre ARS
maquina: String(10)        # FK → maquinas.id
estatus: String(20)        # Activo | Desactivado
motivo: String(300)
facturacion: Float
saldo_pendiente: Float
modo_uso, condicion_salida, condicion_retorno: String(100)
parametros, notas, notas_seguimiento: Text
proxima_colocacion, fecha_retiro: String(10)
observaciones_retiro: Text
lat, lng: Float
productos, fotos: Text     # JSON arrays
```

### Usuario (`usuarios`)
```python
id: String(10) PK          # U001…
user: String(50) UNIQUE
pass: Text                 # scrypt hash
nombre: String(200)
rol: String(20)            # admin | usuario
activo: Boolean
```

### Consentimiento (`consentimientos`) ← NUEVO
```python
id: String(10) PK          # C001…
fecha_firma: String(10)    # YYYY-MM-DD
nombre: String(200)
cedula: String(30)
edad: Integer
direccion: String(300)
telefono: String(100)
medico: String(200)
centro_salud: String(200)
firmado: Boolean
notas: Text
```

### PacienteMaster (`pacientes_master`)
```python
nombre: String(200) PK
datos: Text                # JSON con datos extendidos
```

### Config (`config`)
```python
key: String(50) PK         # ej: 'ars'
value: Text                # JSON
```

---

## Reglas de negocio

1. **Una máquina = un paciente a la vez.** `paciente_actual` se calcula en runtime.
2. **Múltiples colocaciones por paciente.** No se editan — se agregan filas nuevas.
3. **Deduplicación por nombre** (→ por cédula en el futuro).
4. **Montos en DOP** sin decimales. `Intl.NumberFormat('es-DO', {currency:'DOP'})`.
5. **ITBIS 18%** — futuro, al emitir e-CF.
6. **`apply_migrations()`** en `wsgi.py` corre antes de seed — maneja ALTER TABLE que `create_all` no puede.
7. **No instalar paquetes con C extensions** — Render free tier se cuelga. Usar solo pure-Python.

---

## Importación de datos

El frontend acepta **Excel (.xlsx/.xls) y CSV (.csv)**:
- Función `parsearArchivo(file)` detecta extensión y usa XLSX.js
- CSV → `reader.readAsText` + `XLSX.read(text, {type:'string'})`
- Excel → `reader.readAsArrayBuffer` + `XLSX.read(data, {type:'array'})`
- Envía JSON a `POST /api/registros/bulk`

**Columnas esperadas** (primera fila del archivo):
`Nombre, Cédula, Sexo, Edad, Área de lesión, Dirección, Teléfono 1, Teléfono 2, Dr. que refiere, ARS, ID Máquina, N° Colocación, Monto (DOP), Fecha`

---

## Exportación

| Endpoint | Formato | Función |
|----------|---------|---------|
| `GET /api/exportar/registros/excel` | .xlsx | `generate_excel()` |
| `GET /api/exportar/registros/csv` | .csv UTF-8 BOM | `generate_csv()` |
| `GET /api/exportar/registros/pdf` | HTML printable | `generate_pdf()` (requiere reportlab — NO instalado) |
| `GET /api/exportar/maquinas/excel` | .xlsx | inline en app.py |
| `GET /api/exportar/backup` | .json | backup completo (admin) |
| `POST /api/importar/backup` | .json | restaurar backup (admin) |
| `GET /api/consentimientos/<id>/pdf` | HTML printable | `consent_html()` — sin deps extras |

---

## Convenciones de código (frontend)

- Funciones de render: `renderXxx()` → escriben en `#content`
- Funciones de modal: `abrirXxx()` / `verXxxDetalle()` → escriben en `#modal-root`
- Funciones de guardar: `guardarXxx()` → llaman al API y actualizan `DB`
- IDs de inputs: prefijo 2-3 letras + guion + campo (`col-pac`, `cn-nombre`)
- **Nunca** `position:fixed` — rompe el layout
- **Siempre** `esc()` para cualquier valor dinámico en `innerHTML`
- Colores: solo variables CSS (`--brand`, `--ok`, `--warn`, `--danger`)

### Agregar un nuevo módulo de vista
```js
// 1. Sidebar
<div class="nav-item" onclick="go('nuevo')" id="nav-nuevo">
  <i class="ti ti-xxx"></i><span>Nombre</span>
</div>

// 2. Router objects
TITLES    = { ..., nuevo: 'Título de la vista' }
NUEVO_LABELS = { ..., nuevo: 'Acción nueva' }

// 3. Render function
async function renderNuevo(){ ... }

// 4. Router go()
({..., nuevo: renderNuevo})[v]?.()

// 5. handleNuevo()
({..., nuevo: ()=>accionNuevo()})[VIEW]?.()
```

---

## Roadmap

### ✅ Completado
- [x] Backend Flask + PostgreSQL desplegado en Render
- [x] Autenticación segura (scrypt, sessions, rate limiting, headers)
- [x] CRUD completo: Registros, Máquinas, Usuarios, Config
- [x] Importar Excel y CSV (client-side parsing → `/api/registros/bulk`)
- [x] Exportar Excel, CSV desde backend
- [x] Backup/restore JSON completo
- [x] Módulo Consentimiento Informado (DB + PDF server-side)
- [x] Mapa GPS de pacientes activos
- [x] Gestión de usuarios (admin)

### 🔲 Pendiente
- [ ] Integración ECF SSD como PSFE (e-CF DGII tipo 01/02)
- [ ] Reportes 606/607 para la DGII
- [ ] Historial de pagos parciales (tabla `pagos`)
- [ ] Agenda de citas / mantenimiento de máquinas
- [ ] Alertas WhatsApp al vencer colocación
- [ ] App móvil (Flutter o React Native)
- [ ] Migrar frontend a React + Vite + TypeScript
- [ ] SSL explícito en conexión PostgreSQL (pg8000 ssl_context)
- [ ] Fotos migradas a Cloudinary (actualmente base64 en DB)

---

## Contexto del negocio

- **Empresa:** Dipromes Terapias VAC · Calle 6 Santo Tomás de Aquino No. 55, Zona Universitaria, Santo Domingo · RNC 131950965
- **Operación:** Máquinas de terapia VAC se colocan en pacientes en domicilio o centros médicos. Técnico instala → máquina queda X días → técnico retira → se cobra.
- **Volumen:** ~32 registros mayo 2026, ~15 pacientes únicos, 8 máquinas
- **Facturación típica:** RD$13,000 – RD$22,000 por colocación
- **ARS:** Actualmente todos `Privado`. ARS previstas en el futuro.
- **Dev:** Erick Hernández Arias · Inicio: junio 2026

---

## Archivos de referencia

| Archivo | Descripción |
|---------|-------------|
| `Registro_Pacientes_Mayo_2026-Activos.xlsx` | Excel original — fuente de verdad inicial |
| `consentimiento-VAC.docx` | Documento original de consentimiento informado |
| `index.html` | Frontend SPA completo |
| `backend/app.py` | Flask app: todas las rutas y lógica de negocio |
| `backend/models.py` | Modelos SQLAlchemy |
| `backend/exportar.py` | Helpers de exportación |
| `wsgi.py` | Entry point: init DB, migrations, seed, emergency reset |
| `render.yaml` | Config de deploy (pythonVersion: 3.11.0) |

---

*Proyecto: DIPROMES · Cliente: Dipromes Terapias VAC, Santo Domingo RD · Dev: Erick Hernández Arias · Inicio: junio 2026*
