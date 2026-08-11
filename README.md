# MediTrack Pro — Demo v0.1

Sistema de gestión de activos médicos (equipos, mantenimiento, agenda, cotizaciones y facturación ECF-DGII).

## Cómo usar el demo

**No requiere servidor ni instalación.** Solo abre el archivo en el navegador:

```
Doble clic en index.html
```

O desde la terminal:
```bash
open index.html          # macOS
start index.html         # Windows
xdg-open index.html      # Linux
```

## Qué puedes probar

| Módulo | Qué hacer |
|--------|-----------|
| **Dashboard** | Ver métricas, alertas de mantenimiento, citas y facturación |
| **Inventario** | Filtrar por categoría/estado, buscar, ver detalle completo de equipo (pestañas: info, vida útil, mantenimiento) |
| **Agenda** | Ver calendario con días marcados, lista de citas, confirmar citas |
| **Mantenimiento** | Lista priorizada por urgencia con alertas de color |
| **Cotizaciones** | Ver detalle, convertir a factura con un clic |
| **Facturas ECF** | Ver comprobante con NCF, campos DGII, botón de envío |
| **Importar** | Simular importación Excel/XML |

## Flujos que funcionan

- ✅ Crear nuevo equipo (botón "Nuevo Equipo" en Inventario) → aparece en la lista
- ✅ Agendar cita desde el detalle del equipo
- ✅ Crear cotización desde el inventario → aparece en Cotizaciones
- ✅ Convertir cotización → Factura ECF (con NCF generado)
- ✅ Crear factura directamente desde el módulo de Facturas
- ✅ Confirmar citas desde la agenda
- ✅ Filtros de búsqueda en inventario

## Notas de producción

Cuando escalemos a producción necesitaremos:
- Backend Flask/Python con SQLite o PostgreSQL
- Integración real con **ECF SSD** ($3/1,000 e-CFs) como PSFE
- Parser real de Excel (`openpyxl`/`pandas`) y XML
- Autenticación por roles
- Firma digital de comprobantes
- Reportes 606 y 607 para la DGII

## Estructura de datos

Los datos de prueba están en el objeto `DB` dentro del `<script>` en `index.html`.
Para agregar equipos de prueba adicionales, agrega entradas al array `DB.productos`.

---
*Desarrollado para el sector médico / adaptable a cualquier rubro de activos físicos*
