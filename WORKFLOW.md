# WORKFLOW — MediTrack Pro · App Web
# De demo HTML a aplicación web completa
# Versión: 1.0 · Junio 2026 · Erick Hernández

---

## 1. DECISIÓN DE STACK

### ¿Por qué NO React + Vite (como planeaba el CLAUDE.md original)?

| Problema | Impacto |
|----------|---------|
| MacBook Pro 2015 con 8GB RAM | Builds de Vite/webpack lentos, hot reload pesado |
| Sin experiencia previa en React | Curva de aprendizaje = semanas de bloqueo |
| El frontend ya funciona al 100% | Reescribir 2,000 líneas de JS que funcionan = riesgo sin beneficio |
| npm + node_modules = 200MB+ | Overhead innecesario para esta escala |

### Stack elegido — Flask + SQLite + Vanilla JS

El mismo patrón que ya usas en **elearning** y **plantillas-web**. Lo conoces, funciona, y el frontend actual solo necesita que le cambies `localStorage` por `fetch()`.

```
┌─────────────────────────────────────────────────────┐
│                  NAVEGADOR                          │
│  index.html (Vanilla JS SPA)                        │
│  • Mismo CSS y render functions que hoy             │
│  • localStorage → reemplazar con fetch() al API     │
└─────────────────────┬───────────────────────────────┘
                      │ HTTP JSON
┌─────────────────────▼───────────────────────────────┐
│                FLASK (Python 3)                     │
│  app.py · blueprints: pacientes, maquinas,          │
│  registros, usuarios, auth                          │
└─────────────────────┬───────────────────────────────┘
                      │ SQL
┌─────────────────────▼───────────────────────────────┐
│              SQLite WAL (meditrack.db)              │
│  Tablas: maquinas · registros · usuarios            │
│          pacientes_master · fotos · productos       │
└─────────────────────────────────────────────────────┘
```

### Herramientas de soporte

| Herramienta | Para qué |
|-------------|---------|
| `python3 -m venv venv` | Entorno virtual local |
| `flask` | Framework web |
| `werkzeug` | Hash de contraseñas |
| `python-dotenv` | Variables de entorno (.env) |
| PythonAnywhere | Deploy (gratis, mismo que plantillas-web) |

---

## 2. ARQUITECTURA DE ARCHIVOS

```
medicalsol/
│
├── app.py                  ← Factory Flask + registro de blueprints
├── db.py                   ← Conexión SQLite + helpers (get_db, init_db)
├── auth.py                 ← Login, logout, sesión, decorador @login_required
├── meditrack.db            ← Base de datos SQLite (WAL mode)
│
├── routes/
│   ├── pacientes.py        ← CRUD pacientes_master
│   ├── maquinas.py         ← CRUD máquinas
│   ├── registros.py        ← CRUD colocaciones
│   ├── usuarios.py         ← CRUD usuarios (solo admin)
│   └── dashboard.py        ← Métricas agregadas para el dashboard
│
├── templates/
│   └── index.html          ← SPA actual (ligeramente modificado)
│
├── static/
│   └── uploads/
│       └── colocacion_<id>/  ← Fotos por colocación
│
├── migrations/
│   └── schema.sql          ← Definición completa de tablas
│
├── .env                    ← SECRET_KEY, configuración (nunca al git)
├── .env.example            ← Plantilla pública del .env
├── requirements.txt        ← flask, werkzeug, python-dotenv
└── CLAUDE.md               ← Contexto del proyecto (actualizar)
```

---

## 3. MODELO DE BASE DE DATOS

### Tablas y relaciones

```
maquinas
  id          TEXT PK   (MAQ01, MAQ02...)
  nombre      TEXT
  serial      TEXT
  estado      TEXT      (Operativa | Requiere Revisión | Fuera de Servicio | Sin registrar)
  ubicacion   TEXT
  notas       TEXT
  fecha_entrada TEXT    (ISO date)
  created_at  TEXT

registros  ← una fila = una colocación
  id          TEXT PK   (R001, R002...)
  fecha       TEXT      (ISO date)
  fecha_retiro TEXT     (ISO date, null si activo)
  proxima_colocacion TEXT
  notas_seguimiento TEXT
  nombre      TEXT      (FK lógica → pacientes_master.nombre)
  cedula      TEXT
  sexo        TEXT
  edad        INTEGER
  lesion      TEXT
  direccion   TEXT
  ubicacion_maps TEXT
  tel1        TEXT
  tel2        TEXT
  dr_refiere  TEXT
  ars         TEXT
  maquina     TEXT      (FK → maquinas.id, null si sin asignar)
  estatus     TEXT      (Activo | Desactivado)
  motivo      TEXT
  facturacion INTEGER   (DOP, sin decimales)
  created_at  TEXT

productos  ← inventario por colocación
  id          INTEGER PK AUTOINCREMENT
  registro_id TEXT      FK → registros.id
  descripcion TEXT
  cantidad    INTEGER
  precio      INTEGER   (DOP)
  orden       INTEGER

fotos  ← fotos por colocación (paths, no base64)
  id          INTEGER PK AUTOINCREMENT
  registro_id TEXT      FK → registros.id
  filename    TEXT      (nombre del archivo en /static/uploads/)
  orden       INTEGER
  created_at  TEXT

pacientes_master  ← ediciones manuales de perfil
  nombre      TEXT PK
  cedula      TEXT
  sexo        TEXT
  edad        INTEGER
  direccion   TEXT
  ubicacion_maps TEXT
  tel1        TEXT
  tel2        TEXT
  dr_refiere  TEXT
  ars         TEXT
  updated_at  TEXT

usuarios
  id          TEXT PK   (U001, U002...)
  user        TEXT UNIQUE
  pass_hash   TEXT      (werkzeug hash, nunca texto plano)
  nombre      TEXT
  rol         TEXT      (admin | usuario)
  activo      INTEGER   (1 = activo, 0 = inactivo)
  created_at  TEXT
```

### Reglas de integridad

- `registros.maquina` → FK a `maquinas.id` (ON DELETE SET NULL)
- `productos.registro_id` → FK a `registros.id` (ON DELETE CASCADE)
- `fotos.registro_id` → FK a `registros.id` (ON DELETE CASCADE)
- Una máquina solo puede tener UN registro con `estatus = 'Activo'` al mismo tiempo (enforced en la lógica de negocio)

---

## 4. API ENDPOINTS

Todos los endpoints devuelven JSON. El frontend los llama con `fetch()`.

### Auth
```
POST /auth/login          body: {user, pass}  → {ok, nombre, rol}
POST /auth/logout         → {ok}
GET  /auth/sesion         → {user, nombre, rol} o 401
```

### Dashboard
```
GET  /api/dashboard       → {activos, pacientes_unicos, maquinas_ok, fact_mes, ...}
```

### Pacientes
```
GET  /api/pacientes       → [{nombre, cedula, colocaciones, total_facturado, estatus}...]
GET  /api/pacientes/<nombre>  → {datos, colocaciones, total_facturado}
PUT  /api/pacientes/<nombre>  body: {campos editables}
```

### Máquinas
```
GET  /api/maquinas        → [maquina...]
POST /api/maquinas        body: {nombre, serial, estado, ...}
PUT  /api/maquinas/<id>   body: {campos a editar}
DELETE /api/maquinas/<id>
```

### Registros (Colocaciones)
```
GET  /api/registros       ?nombre=&estatus=&mes=  → [registro...]
POST /api/registros       body: {todos los campos}
PUT  /api/registros/<id>  body: {campos a editar}
DELETE /api/registros/<id>
POST /api/registros/<id>/retirar  body: {fecha_retiro}
```

### Fotos
```
POST /api/registros/<id>/fotos   multipart/form-data → {urls:[]}
DELETE /api/fotos/<foto_id>
```

### Usuarios (solo admin)
```
GET  /api/usuarios        → [usuario...] (sin pass_hash)
POST /api/usuarios        body: {user, pass, nombre, rol}
PUT  /api/usuarios/<id>   body: {campos editables}
DELETE /api/usuarios/<id>
```

---

## 5. FLUJO DE SESIÓN Y SEGURIDAD

```
Usuario abre la app
    ↓
Flask sirve templates/index.html (ruta GET /)
    ↓
JS llama GET /auth/sesion
    ├── 401 → muestra pantalla de login
    └── 200 → muestra la app con el nombre/rol del usuario
         ↓
Cada POST/PUT/DELETE incluye header X-CSRF-Token
Flask lo verifica antes de procesar
```

### Reglas de seguridad
- Contraseñas: hash con `werkzeug.security.generate_password_hash`
- Sesiones: `flask.session` con `SECRET_KEY` desde `.env`
- CSRF: token en cookie `csrf_token`, verificado en cada mutación
- Uploads: validar magic bytes (PNG/JPG/WebP) antes de guardar
- Rol admin: verificar `session['rol'] == 'admin'` en endpoints de usuarios
- Fotos: guardar en `static/uploads/colocacion_<id>/` con nombre UUID, no el nombre original del archivo

---

## 6. FASES DE DESARROLLO

### FASE 1 — Base de datos y API (sin tocar el frontend)
**Objetivo:** Flask corre, DB existe, endpoints responden JSON correcto.

- [ ] 1.1 `venv` + `requirements.txt` + `.env`
- [ ] 1.2 `migrations/schema.sql` — todas las tablas
- [ ] 1.3 `db.py` — `get_db()`, `init_db()`, helpers CRUD
- [ ] 1.4 `app.py` — factory Flask, sirve `index.html` en `/`
- [ ] 1.5 `auth.py` — login/logout/sesion con hash werkzeug
- [ ] 1.6 `routes/maquinas.py` — GET, POST, PUT, DELETE
- [ ] 1.7 `routes/registros.py` — GET, POST, PUT, DELETE, retirar
- [ ] 1.8 `routes/usuarios.py` — CRUD protegido por admin
- [ ] 1.9 `routes/dashboard.py` — métricas agregadas
- [ ] 1.10 Script de seed: migrar datos del `index.html` a la DB

### FASE 2 — Conectar el frontend al API
**Objetivo:** El `index.html` usa `fetch()` en lugar de `localStorage`.

- [ ] 2.1 Reemplazar `saveDB()` / `loadDB()` por llamadas fetch al API
- [ ] 2.2 Al cargar la app: `GET /auth/sesion` → si 401 mostrar login, si OK cargar datos
- [ ] 2.3 `GET /api/dashboard` → alimenta `renderDash()`
- [ ] 2.4 `GET /api/pacientes` → alimenta `renderPacientes()`
- [ ] 2.5 `POST /api/registros` → reemplaza `guardarColocacion()`
- [ ] 2.6 `POST /api/registros/<id>/retirar` → reemplaza `confirmarRetiro()`
- [ ] 2.7 Fotos: `POST multipart` → guarda en disco, devuelve URL
- [ ] 2.8 Manejo de errores: si 401 en cualquier llamada → logout automático

### FASE 3 — Deploy a PythonAnywhere
**Objetivo:** La app es accesible desde cualquier dispositivo con internet.

- [ ] 3.1 Crear cuenta / webapp en PythonAnywhere
- [ ] 3.2 `git push` → `git pull` en PA → Reload
- [ ] 3.3 `.env` configurado en PA (SECRET_KEY seguro)
- [ ] 3.4 Directorio de uploads con permisos de escritura
- [ ] 3.5 Prueba completa desde celular (acceso externo)

### FASE 4 — Funciones adicionales (post-lanzamiento)
- [ ] Exportar registro filtrado a Excel (openpyxl)
- [ ] Conduce de descargo en PDF (ReportLab)
- [ ] Importar nuevo Excel del cliente
- [ ] Alertas de próxima colocación por WhatsApp (Twilio o CallMeBot)
- [ ] Backup automático de la DB

---

## 7. FLUJO DE TRABAJO DIARIO (cómo trabajaremos)

```
1. Abrir sesión → leer este WORKFLOW.md y el estado de las fases
2. Identificar la tarea más pequeña que avanza el objetivo
3. Construir → probar en local → confirmar que funciona
4. git commit descriptivo
5. Si la fase está completa → marcarla en este archivo
6. Deploy a PA solo cuando una fase completa está testeada
```

### Regla de oro
> Una fase a la vez. No empezar Fase 2 sin que la Fase 1 responda JSON correcto.
> No empezar Fase 3 sin que el frontend funcione localmente contra el API.

---

## 8. CRITERIOS DE "LISTO PARA PRODUCCIÓN"

Antes del primer deploy real al cliente, verificar:

- [ ] Login funciona y rechaza credenciales incorrectas
- [ ] Usuario sin rol admin no ve la sección Usuarios
- [ ] Crear paciente → aparece en lista → se puede editar
- [ ] Asignar máquina → máquina aparece ocupada en inventario
- [ ] Retirar máquina → máquina queda libre
- [ ] Subir foto → se ve en el historial
- [ ] Generar conduce → impresión se ve correcta
- [ ] Backup: exportar JSON / importar JSON funciona
- [ ] Desde un celular externo (no localhost) → todo funciona
- [ ] Contraseñas almacenadas como hash (nunca texto plano en la DB)

---

## 9. RESUMEN EJECUTIVO

| Qué | Decisión |
|-----|---------|
| Backend | Python 3 + Flask + SQLite WAL |
| Frontend | Vanilla JS SPA (el actual, sin reescribir) |
| Auth | Flask sessions + werkzeug hash |
| Fotos | Archivos en disco (`/static/uploads/`) |
| Deploy | PythonAnywhere (mismo flujo que plantillas-web) |
| React/Vite | ❌ No — complejidad sin beneficio real |
| PostgreSQL | ❌ No — SQLite es suficiente para este volumen |
| Render.com | ❌ No — PythonAnywhere ya lo conoces y es gratis |

**Tiempo estimado Fase 1+2:** 3-4 sesiones de trabajo
**Tiempo estimado Fase 3 (deploy):** 1 sesión
**Total para app funcional en producción:** ~5 sesiones

---

*Cuando estés listo para empezar a codear: "Arrancamos Fase 1"*
