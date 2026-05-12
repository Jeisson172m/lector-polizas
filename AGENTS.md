# AGENTS.md - Historial del Proyecto Lector de Pólizas PDF

## Estado del Proyecto

**Versión:** 1.0.0 (Mayo 2026)
**Estado:** En producción
**URL:** https://lector-polizas-1.onrender.com
**Repositorio:** https://github.com/Jeisson172m/lector-polizas

---

## Resumen Ejecutivo

Aplicación web para extraer datos de pólizas de seguros Bolívar mediante OCR (Tesseract) y comparar con archivos Excel de aseguradoras, generando métricas KPIs de calidad de extracción.

El sistema procesa PDFs de pólizas, extrae 24 campos específicos, los compara con datos de la aseguradora y genera reportes en Excel con indicadores de coincidencia.

---

## Contexto de Desarrollo (Mayo 2026)

### Problema Original
Las aseguradoras emiten pólizas en PDF que deben ser contrastadas manualmente con archivos Excel. Este proceso manual es tedioso, propenso a errores y costoso.

### Solución Implementada
- OCR automatizado con Tesseract
- Extracción de 24 campos estructurados
- Comparación inteligente con Excel aseguradora
- Dashboard de KPIs
- Descarga de resultados en Excel

---

## Arquitectura Implementada

```
Frontend (HTML/CSS/JS) ──► Flask API ──► OCR Service (Tesseract + pdfplumber)
                                         │
                                         ├── Bolívar Parser (regex)
                                         ├── Excel Service (comparación)
                                         └── Cache temporal en memoria
```

---

## Decisiones Técnicas Clave

### 1. Stack Tecnológico
- **Backend:** Flask 3.0 + Python 3.11
- **OCR:** Tesseract + pdfplumber + pdf2image
- **Excel:** openpyxl
- **Despliegue:** Render (plan free)

### 2. Procesamiento de PDFs
- Extracción primaria con pdfplumber (ligero)
- Fallback a Tesseract si falla
- Límite de 3 páginas por PDF
- DPI reducido a 200 para optimizar memoria
- Garbage collection explícito después de cada PDF

### 3. Batch Processing
- Frontend procesa PDFs en lotes de 5
- Evita timeout de 300s en Render
- Resultados se concatenan en el frontend

### 4. Normalización de Datos
- Headers: se normalizan para aceptar variaciones (espacios, tildes, guiones)
- Valores numéricos: se elimina sufijo .0 en POLIZA, TOMADOR, ASEGURADO
- Fechas: formato consistente dd/mm/yyyy
- Nombres: NO se modifican espacios dobles (son datos de la aseguradora)

---

## Campos Extraídos (24)

```
ARCHIVO, POLIZA, PLACA, MARCA, LÍNEA,
TOMADOR, NOMBRE TOMADOR, ASEGURADO, NOMBRE ASEGURADO,
CELULAR, CORREO, NIT ONEROSO, BENEFICIARIO ONEROSO,
FECHA INICIO VIGE, FECHA VENC,
VALOR ASEGURADO 2024, VALOR ASEGURADO 2025, SINIESTROS,
PRIMA NETA 2024, PRIMA TOTAL 2024, PRIMA NETA 2025, PRIMA TOTAL 2025,
VARIACIÓN PRIMA NETA, VARIACIÓN PRIMA TOTAL
```

---

## Campos Utilizados en Comparación (13)

```
POLIZA, PLACA, MARCA, LÍNEA, TOMADOR, NOMBRE TOMADOR,
ASEGURADO, NOMBRE ASEGURADO, FECHA INICIO VIGE, FECHA VENC,
VALOR ASEGURADO 2025, PRIMA NETA 2025, PRIMA TOTAL 2025
```

---

## KPIs Generados

| Métrica | Descripción |
|---------|-------------|
| Archivos Procesados | Total de PDFs |
| % Coincidencia Total | Promedio general |
| Campos Comparados | Total de comparaciones |
| Desglose por Campo | OK / Diferencia / Sin datos |

---

## Limitaciones Actuales (Plan Free)

| Recurso | Límite |
|---------|--------|
| RAM | 512 MB |
| Timeout | 300s |
| PDFs óptimo | 30-40 por sesión |

---

## Próxima Funcionalidad: AUTENTICACIÓN

### Preguntas Pendientes por Responder

1. **Autenticación:**
   - ¿Simple (usuario/contraseña en DB) o SSO corporativo (Google/Outlook)?

2. **Base de Datos:**
   - ¿SQLite (ligero, sin instalación)?
   - ¿PostgreSQL (recomendado, disponible en Render)?

3. **Gestión de Usuarios:**
   - ¿Creados manualmente por admin?
   - ¿Auto-registro de usuarios?

4. **Permisos/Roles:**
   - ¿Todos los 5 usuarios mismo acceso?
   - ¿Roles diferenciados (admin vs usuario)?

5. **Funcionalidades Extras:**
   - ¿Historial por usuario?
   - ¿Notificaciones por email?

### Tablas Sugeridas

```sql
-- Tabla de usuarios
users (id, username, password_hash, email, role, created_at)

-- Historial de procesamientos
process_history (id, user_id, filename, timestamp, status, pdf_count)
```

### Estructura Sugerida con Blueprints

```
src/
├── auth/           # Login, logout, register
├── upload/         # Carga de PDFs
├── comparison/     # Comparación y KPIs
└── admin/          # Gestión de usuarios
```

---

## Comandos Rápidos

```bash
# Ejecutar localmente
python Lector_pdf.py

# Desplegar (auto en push a main)
git push

# Ver logs en Render
render logs -s lector-polizas
```

---

## Commits Principales

| Commit | Descripción |
|--------|-------------|
| 84be72c | README completo para inversionistas |
| 0ed7ae7 | Fix formato POLIZA/TOMADOR sin .0 |
| 1b0f240 | Fix KPIs con fechas formateadas |
| bdd9d41 | Fix formato fecha dd/mm/yyyy |
| 705ad2d | Restaurar pdf2image con optimizaciones |
| df43a7a | Batch processing en frontend |
| 7c1e5ad | Optimización de memoria |
| 6f0dba7 | Debug logging en endpoints |
| 23b3ec8 | Fix rutas duplicadas |

---

## Archivos del Proyecto

```
lector-polizas/
├── Lector_pdf.py              # Flask app + rutas
├── src/
│   ├── parsers/
│   │   └── bolivar_parser.py  # Extracción campos
│   └── services/
│       ├── ocr_service.py     # OCR + Tesseract
│       └── excel_service.py  # Comparación + KPIs
├── templates/
│   └── index.html             # Frontend
├── uploads/                   # Temp (gitignored)
├── requirements.txt
├── render.yaml
├── README.md                  # Documentación completa
└── AGENTS.md                  # Este archivo
```

---

## Notas para el Siguiente Agente

1. El proyecto está funcionando en producción en Render
2. La rama principal es `main` (no `master`)
3. El README.md tiene documentación muy completa
4. Para agregar nuevas aseguradoras, crear nuevo parser en `src/parsers/`
5. El sistema de cache temporal guarda el Excel de la aseguradora en memoria con clave UUID
6. Los espacios dobles en nombres NO se normalizan (es información de la aseguradora)
7. El batch processing está en el frontend (5 PDFs por request)

---

*Última actualización: Mayo 2026*
*Desarrollado para: Seguros Bolívar*
*Próximo paso: Sistema de autenticación*