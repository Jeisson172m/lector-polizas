# LECTOR DE PÓLIZAS PDF

Aplicación web para extraer datos de pólizas de seguros mediante OCR y comparar con archivos Excel de aseguradoras, generando métricas KPIs de calidad de extracción.

---

## TABLA DE CONTENIDOS

1. [Descripción del Proyecto](#1-descripción-del-proyecto)
2. [Arquitectura del Sistema](#2-arquitectura-del-sistema)
3. [Diagrama de Flujo](#3-diagrama-de-flujo)
4. [Campos Extraídos](#4-campos-extraídos)
5. [Lógica de Comparación](#5-lógica-de-comparación)
6. [Métricas KPIs](#6-métricas-kpis)
7. [Limitaciones del Plan Free](#7-limitaciones-del-plan-free)
8. [Hoja de Ruta - Escalabilidad](#8-hoja-de-ruta---escalabilidad)
9. [Instalación Local](#9-instalación-local)
10. [Despliegue en Render](#10-despliegue-en-render)
11. [Estructura del Proyecto](#11-estructura-del-proyecto)
12. [Uso de la Aplicación](#12-uso-de-la-aplicación)
13. [Mantenimiento y Soporte](#13-mantenimiento-y-soporte)

---

## 1. DESCRIPCIÓN DEL PROYECTO

### Problema que resuelve

Las aseguradoras emiten pólizas en formato PDF que deben ser contrastadas manualmente con archivos Excel de sus asegurados. Este proceso manual es:
- **Tedioso**: 30-40 pólizas pueden tomar horas de trabajo manual
- **Propenso a errores**: La transcripción manual genera inconsistencias
- **Costoso**: Requiere personal dedicado tiempo completo

### Solución

Lector de Pólizas PDF automatiza la extracción de datos de pólizas Bolívar mediante OCR (Optical Character Recognition) y los compara automáticamente con el Excel de la aseguradora, generando:
- Archivo Excel con todos los datos extraídos
- Reporte comparativo detallado con indicadores de coincidencia
- Dashboard de KPIs con porcentaje de calidad por campo

### Público Objetivo

- Compañías de seguros y reaseguros
- Corredores de seguros
- Departamentos de suscripción y renovaciones
- Administradoras de riesgos laborales (ARL)

---

## 2. ARQUITECTURA DEL SISTEMA

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           FRONTEND (Cliente)                            │
│                    HTML5 + CSS3 + JavaScript vanilla                    │
│                      Diseño responsivo, sin dependencias                  │
└─────────────────────────────────┬───────────────────────────────────────┘
                                  │ HTTP/HTTPS
                                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                           BACKEND (Servidor)                            │
│                      Flask 3.0 + Python 3.11                            │
│                                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │ OCR Service  │  │ Parser       │  │ Excel        │  │ Cache        │ │
│  │ (Tesseract)  │  │ (Bolívar)    │  │ Service      │  │ (Insurer)    │ │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘ │
│         │                │                │                │              │
│         ▼                ▼                ▼                ▼              │
│  ┌─────────────────────────────────────────────────────────────────────┐ │
│  │                    pdfplumber (extracción texto)                     │ │
│  │                    pdf2image + PIL (imágenes para OCR)               │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         ALMACENAMIENTO                                  │
│  ┌─────────────────────┐           ┌─────────────────────────────────┐  │
│  │ Archivos temporales │           │ Excel Aseguradora (en memoria)  │  │
│  │ (uploads/)          │           │ cache_key system                │  │
│  └─────────────────────┘           └─────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
```

### Componentes Tecnológicos

| Componente | Tecnología | Función |
|------------|------------|---------|
| Frontend | HTML5 + CSS3 + JS | Interfaz de usuario, uploads, visualización |
| Backend | Flask 3.0 | API REST, orquestación de servicios |
| OCR | Tesseract 5.x + pdf2image | Extracción de texto de PDFs escaneados/impresos |
| Parser | Regex + pdfplumber | Extracción estructurada de campos específicos |
| Excel | openpyxl | Generación de archivos Excel formateados |
| Cache | RAM del servidor | Almacenamiento temporal de Excel aseguradora |
| Despliegue | Render + Gunicorn | Hosting en la nube |

---

## 3. DIAGRAMA DE FLUJO

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              FLUJO DE DATOS                                  │
└─────────────────────────────────────────────────────────────────────────────┘

    ┌──────────┐      ┌──────────────┐      ┌───────────────┐
    │ Usuario  │      │   Frontend    │      │   Backend     │
    │ carga    │─────▶│   (HTML)      │─────▶│   (Flask)     │
    │ archivos │      │              │      │               │
    └──────────┘      └──────────────┘      └───────┬───────┘
                                                    │
                    ┌───────────────────────────────┼───────────────────────────┐
                    │                               │                           │
                    ▼                               ▼                           ▼
          ┌──────────────────┐           ┌──────────────────┐        ┌──────────────────┐
          │  OCR Service     │           │  Bolívar Parser  │        │  Excel Service   │
          │                  │           │                  │        │                  │
          │ 1. pdfplumber    │           │  Extrae campos   │        │ 1. load_insurer  │
          │ 2. pdf2image     │──────────▶│  específicos     │        │ 2. compare       │
          │ 3. Tesseract     │           │  con regex       │        │ 3. calculate_kpis│
          │                  │           │                  │        │ 4. create_xlsx   │
          └──────────────────┘           └──────────────────┘        └──────────────────┘
                    │                               │                           │
                    └───────────────────────────────┼───────────────────────────┘
                                                    │
                                                    ▼
                                        ┌───────────────────────┐
                                        │   Descarga de         │
                                        │   Resultados          │
                                        │                       │
                                        │  - resultados.xlsx    │
                                        │  - comparativo.xlsx   │
                                        │  - KPIs en pantalla   │
                                        └───────────────────────┘

═══════════════════════════════════════════════════════════════════════════════

                    PROCESAMIENTO POR LOTES (BATCH)

    ┌──────────────────────────────────────────────────────────────────────┐
    │                     FRONTEND - Lotes de 5 PDFs                        │
    └──────────────────────────────────────────────────────────────────────┘

    Archivo 1 ─┐
    Archivo 2 ─┤
    Archivo 3 ─┼── Lote 1 ──▶ Request 1 ──▶ Procesa ──▶ Resultados 1
    Archivo 4 ─┤                    │
    Archivo 5 ─┘                    ▼
                               ┌──────────────────┐
    Archivo 6 ─┐                 │  Concatenar      │
    Archivo 7 ─┤                 │  Resultados      │
    Archivo 8 ─┼── Lote 2 ──▶ Request 2 ──▶ Procesa ──▶ Resultados 1+2
    Archivo 9 ─┤                    │
    Archivo 10 ─┘                    ▼
                               ┌──────────────────┐
        ...                     │  Almacena todos  │
        ...                     │  los resultados  │
        ...                     └──────────────────┘

═══════════════════════════════════════════════════════════════════════════════

                            LÓGICA DE COMPARACIÓN

    ┌───────────────────┐           ┌───────────────────┐
    │  PDF Extraído     │           │  Excel            │
    │                   │           │  Aseguradora      │
    │ POLIZA: 150551... │           │ POLIZA: 150551... │
    │ PLACA: WDS053     │           │ PLACA: WDS053     │
    │ MARCA: FORD       │           │ MARCA: FORD       │
    │ ...               │           │ ...               │
    └─────────┬─────────┘           └─────────┬─────────┘
              │                               │
              │        ┌───────────────────────┤
              │        │                       │
              ▼        ▼                       ▼
    ┌─────────────────────────────────────────────────────┐
    │                  Excel Service                       │
    │                                                     │
    │  _normalize_value()  ──▶  Normalización strings      │
    │  _format_value()     ──▶  Formato consistente        │
    │  _compare_values()   ──▶  Comparación inteligente    │
    │                                                     │
    │  Resultados: ✓ (match) | ✗ (diferencia) | - (sin dato)│
    └─────────────────────────────────────────────────────┘
```

---

## 4. CAMPOS EXTRAÍDOS

### 4.1 Campos del PDF (24 columnas)

| # | Campo | Descripción | Tipo | Ejemplo |
|---|-------|-------------|------|---------|
| 1 | ARCHIVO | Nombre del PDF procesado | string | WDS053_1118775435.pdf |
| 2 | POLIZA | Número de póliza | string | 1505512426108 |
| 3 | PLACA | Placa del vehículo | string | WDS053 |
| 4 | MARCA | Marca del vehículo | string | FORD |
| 5 | LÍNEA | Línea/modelo del vehículo | string | RANGER |
| 6 | TOMADOR | Identificación del tomador | string | 1118775435 |
| 7 | NOMBRE TOMADOR | Nombre completo del tomador | string | ALEXANDRA BARRAGAN M. |
| 8 | ASEGURADO | Identificación del asegurado | string | 1118775435 |
| 9 | NOMBRE ASEGURADO | Nombre completo del asegurado | string | ALEXANDRA BARRAGAN M. |
| 10 | CELULAR | Teléfono de contacto | string | 3001234567 |
| 11 | CORREO | Email de contacto | string | email@ejemplo.com |
| 12 | NIT ONEROSO | NIT beneficiario oneroso | string | 901234567-1 |
| 13 | BENEFICIARIO ONEROSO | Nombre beneficiario oneroso | string | FINESA S.A. |
| 14 | FECHA INICIO VIGE | Fecha inicio de vigencia | date | 28/05/2026 |
| 15 | FECHA VENC | Fecha vencimiento | date | 28/05/2027 |
| 16 | VALOR ASEGURADO 2024 | Valor asegurado año anterior | number | 120000000 |
| 17 | VALOR ASEGURADO 2025 | Valor asegurado año actual | number | 131800000 |
| 18 | SINIESTROS | Indicador de siniestros | string | NO |
| 19 | PRIMA NETA 2024 | Prima neta año anterior | number | 2900000 |
| 20 | PRIMA TOTAL 2024 | Prima total año anterior | number | 3900000 |
| 21 | PRIMA NETA 2025 | Prima neta año actual | number | 3309499 |
| 22 | PRIMA TOTAL 2025 | Prima total año actual | number | 4334161 |
| 23 | VARIACIÓN PRIMA NETA | % variación vs año anterior | number | 14.1% |
| 24 | VARIACIÓN PRIMA TOTAL | % variación total | number | 11.1% |

### 4.2 Campos Utilizados en Comparación (13 columnas)

| # | Campo | Prioridad | Mapeo Excel Flexible |
|---|-------|-----------|---------------------|
| 1 | POLIZA | Crítica | POLIZA, NOPOLIZA, POLIZANO |
| 2 | PLACA | Crítica | PLACA, PLACAVEHI |
| 3 | MARCA | Alta | MARCA |
| 4 | LÍNEA | Alta | LÍNEA, LINEA, CLASE |
| 5 | TOMADOR | Crítica | TOMADOR, IDTOMADOR |
| 6 | NOMBRE TOMADOR | Media | NOMBRETOMADOR, NOMBRE TOMADOR |
| 7 | ASEGURADO | Crítica | ASEGURADO, IDASEGURADO |
| 8 | NOMBRE ASEGURADO | Media | NOMBREASEGURADO, NOMBRE ASEGURADO |
| 9 | FECHA INICIO VIGE | Alta | FECHAINICIOVIGE, FECHA INICIO VIGE |
| 10 | FECHA VENC | Alta | FECHAVENC, FECHA VENC |
| 11 | VALOR ASEGURADO 2025 | Crítica | VALORASEGURADO2025 |
| 12 | PRIMA NETA 2025 | Crítica | PRIMANETA2025, PRIMA NETA 2025 |
| 13 | PRIMA TOTAL 2025 | Crítica | PRIMATOTAL2025, PRIMA TOTAL 2025 |

---

## 5. LÓGICA DE COMPARACIÓN

### 5.1 Normalización de Headers

```python
def _normalize_header(header):
    # Elimina espacios, puntos, guiones
    # Convierte a mayúsculas
    # Reemplaza caracteres especiales (Ó→O, Í→I)
    # Resultado: "FECHA DE INICIO VIGENCIA" → "FECHAINICIOVIGENCIA"
```

### 5.2 Normalización de Valores

```python
def _normalize_value(val):
    # Floats sin decimales → integers: 1505512426108.0 → "1505512426108"
    # Integers → strings: 1118775435 → "1118775435"
    # Fechas → consistencia en formato dd/mm/yyyy
    # Eliminación de espacios en blanco extremos
```

### 5.3 Comparación Inteligente

| Tipo de Campo | Lógica de Comparación |
|---------------|----------------------|
| **Poliza/Tomador/Asegurado** | Comparación exacta después de normalización |
| **Fechas** | Parseo múltiple (dd/mm/yyyy, dd-mm-yyyy, yyyy-mm-dd) y comparación de fechas |
| **Valores numéricos** | Comparación numérica con tolerancia de 100 (para decimales mal extraídos) |
| **Nombres** | Comparación exacta (espacios dobles se mantienen - son datos de la aseguradora) |
| **Valores vacíos en Excel** | Retorna "-" (no cuenta como error) |

### 5.4 Mapeo Flexible de Headers

El sistema intenta múltiples variantes de headers del Excel:
```python
header_mappings = {
    'POLIZA': ['POLIZA', 'NOPOLIZA', 'POLIZANO'],
    'PLACA': ['PLACA', 'PLACAVEHI'],
    'FECHA INICIO VIGE': ['FECHAINICIOVIGE', 'FECHA INICIO VIGE'],
    # ...
}
```

---

## 6. MÉTRICAS KPIs

### 6.1 Indicadores Globales

| Métrica | Descripción | Ejemplo |
|---------|-------------|---------|
| Archivos Procesados | Total de PDFs procesados | 27 |
| % Coincidencia Total | Porcentaje de campos que coinciden | 75% |
| Con Diferencias | Archivos con al menos 1 diferencia | 27 |
| Campos Comparados | Total de comparaciones realizadas | 351 |

### 6.2 Desglose por Campo

Para cada campo en COLUMNS_TO_COMPARE se calcula:

| Indicador | Descripción |
|-----------|-------------|
| OK | Campos que coinciden exactamente |
| Diferencia | Campos con valores diferentes |
| Sin datos | Campos vacíos en el Excel aseguradora |
| % OK | (OK / Total) × 100 |

### 6.3 Ejemplo de Salida

```
POLIZA         100% (OK: 27 | Dif: 0 | Sin datos: 0)
PLACA          100% (OK: 27 | Dif: 0 | Sin datos: 0)
FECHA VENC     100% (OK: 27 | Dif: 0 | Sin datos: 0)
NOMBRE TOMADOR  66% (OK: 18 | Dif: 9 | Sin datos: 0)
```

### 6.4 Interpretación

- **100%**: Extracción perfecta, datos coincidentes
- **66%**: 9 diferencias - verificar calidad OCR o discrepancias reales
- **0% en fechas pero sin diferencias en Excel**: Indica fechas faltantes en el Excel de la aseguradora
- **NOMBRE ASEGURADO bajo %**: Comúnmente el Excel no tiene este dato

---

## 7. LIMITACIONES DEL PLAN FREE

### 7.1 Restricciones de Render (Free Tier)

| Recurso | Límite | Impacto |
|---------|--------|---------|
| **RAM** | 512 MB | Limita tamaño de batch |
| **Timeout** | 300 segundos | Máximo tiempo de procesamiento |
| **CPU** | Compartido | Puede haber lentitud |
| **Sleep** | 15 min inactividad | Primera request tarda ~30s en despertar |
| **Disco** | Efímero | Archivos temporales se eliminan |

### 7.2 Límites Operativos Actuales

| Métrica | Valor Actual | Notas |
|---------|--------------|-------|
| PDFs por lote (frontend) | 5 | Para evitar timeout |
| Tiempo estimado por lote | 15-30 segundos | Depende de complejidad PDF |
| PDFs óptimo por sesión | 30-40 | Con Excel aseguradora |
| RAM por PDF (~) | 10-15 MB | Con optimización actual |
| Total RAM utilizada | ~75-150 MB | Con 10-15 PDFs en memoria |

### 7.3 ¿Por qué puede fallar con 100+ PDFs?

```
Cálculo de memoria:
100 PDFs × 15 MB/PDF = 1,500 MB (excede 512 MB disponible)

Timeout:
100 PDFs ÷ 5 por lote = 20 requests
20 requests × 20 seg/request = 400 segundos
Límite actual: 300 segundos ❌
```

---

## 8. HOJA DE RUTA - ESCALABILIDAD

### 8.1 Inversiones Recomendadas por Capacidad

| Plan | Costo Mensual | RAM | Timeout | Capacidad Estimada | Trabajadores |
|------|---------------|-----|---------|-------------------|--------------|
| **Free (actual)** | $0 | 512 MB | 300s | 30-40 PDFs | 1 |
| **Starter** | ~$7 | 1 GB | 600s | 100-150 PDFs | 2 |
| **Pro** | ~$25 | 2 GB | 1200s | 300-500 PDFs | 4 |
| **Performance** | ~$75 | 4 GB | 3600s | 1000+ PDFs | 8 |

### 8.2 Optimizaciones en Progreso

| Mejora | Estado | Impacto |
|--------|--------|---------|
| Reducción DPI (200→150) | ✅ Implementado | -25% RAM por imagen |
| Límite 3 páginas por PDF | ✅ Implementado | -60% imágenes procesadas |
| Batch processing (frontend) | ✅ Implementado | Evita timeout |
| Garbage collection explícito | ✅ Implementado | Libera RAM entre lotes |
| Límite máximo páginas OCR | ✅ Implementado | Previene PDFs excesivamente largos |

### 8.3 Próximas Optimizaciones Sugeridas

| Mejora | Prioridad | Esfuerzo | Impacto |
|--------|-----------|----------|---------|
| Procesamiento worker background | Alta | Alto | Elimina límites de timeout |
| Compresión de imágenes antes OCR | Media | Medio | -40% RAM |
| Cache de PDFs ya procesados | Media | Medio | Rapidez en re-procesos |
| Cola de trabajos (Redis/RabbitMQ) | Alta | Alto | Procesamiento distribuido |
| Base de datos para resultados | Baja | Alto | Historial y auditoría |

### 8.4 Arquitectura Futura Sugerida

```
                    ┌─────────────────────────────────────────┐
                    │            BALANCEADOR DE CARGA          │
                    │           (Nginx / CloudFlare)           │
                    └─────────────────┬───────────────────────┘
                                      │
              ┌───────────────────────┼───────────────────────┐
              │                       │                       │
              ▼                       ▼                       ▼
    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
    │   Web Worker 1  │    │   Web Worker 2  │    │   Web Worker 3  │
    │   (Flask + OCR) │    │   (Flask + OCR) │    │   (Flask + OCR) │
    │     1 GB RAM    │    │     1 GB RAM    │    │     1 GB RAM    │
    └────────┬────────┘    └────────┬────────┘    └────────┬────────┘
              │                       │                       │
              └───────────────────────┼───────────────────────┘
                                      │
                    ┌─────────────────┴─────────────────┐
                    │         REDIS (Cola de Jobs)       │
                    │    (Celery / RQ / Dramatiq)        │
                    └─────────────────┬─────────────────┘
                                      │
                    ┌─────────────────┴─────────────────┐
                    │      WORKER PROCESAMIENTO          │
                    │  (Background, sin timeout web)     │
                    │                                     │
                    │  ┌─────────┐ ┌─────────┐ ┌─────────┐ │
                    │  │ Job 1  │ │ Job 2  │ │ Job 3  │ │
                    │  │ 5 PDFs │ │ 5 PDFs │ │ 5 PDFs │ │
                    │  └─────────┘ └─────────┘ └─────────┘ │
                    └─────────────────────────────────────┘
                                      │
                    ┌─────────────────┴─────────────────┐
                    │         PostgreSQL / SQLite        │
                    │    (Historial, resultados, KPIs)   │
                    └─────────────────────────────────────┘
```

---

## 9. INSTALACIÓN LOCAL

### 9.1 Requisitos Previos

```
- Python 3.11 o superior
- Tesseract OCR 5.x
- Paquete de idioma español para Tesseract (tesseract-ocr-spa)
- poppler-utils (para pdf2image)
```

### 9.2 Instalación de Dependencias del Sistema

**Windows:**
1. Descargar Tesseract desde: https://github.com/UB-Mannheim/tesseract/wiki
2. Instalar con idioma español seleccionado
3. Agregar al PATH de Windows

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install -y tesseract-ocr tesseract-ocr-spa poppler-utils
```

**macOS:**
```bash
brew install tesseract tesseract-lang poppler
```

### 9.3 Instalación del Proyecto

```bash
# Clonar el repositorio
git clone https://github.com/Jeisson172m/lector-polizas.git
cd lector-polizas

# Crear entorno virtual (recomendado)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate     # Windows

# Instalar dependencias Python
pip install -r requirements.txt
```

### 9.4 Archivo requirements.txt

```
Flask==3.0.0
flask-cors==4.0.0
pdf2image==1.17.0
pytesseract==0.3.10
openpyxl==3.1.2
Pillow>=10.0.0
pdfplumber>=0.10.0
gunicorn>=21.0.0
```

### 9.5 Ejecución

```bash
# Configurar variable de entorno (opcional)
export TESSERACT_CMD=/usr/bin/tesseract  # Linux
# Windows: set TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe

# Ejecutar servidor de desarrollo
python Lector_pdf.py

# O usando Flask CLI
export FLASK_APP=Lector_pdf.py
flask run --host=0.0.0.0 --port=5000
```

### 9.6 Acceso Local

Abrir en el navegador: **http://localhost:5000**

### 9.7 Ejecución en Producción Local

```bash
# Con Gunicorn
gunicorn Lector_pdf:app --bind 0.0.0.0:5000 --workers 2 --timeout 300
```

---

## 10. DESPLIEGUE EN RENDER

### 10.1 Configuración de render.yaml

```yaml
services:
  - type: web
    name: lector-polizas
    region: oregon
    plan: free
    runtime: python
    buildCommand: |
      apt-get update && apt-get install -y poppler-utils tesseract-ocr tesseract-ocr-spa && pip install --no-cache-dir -r requirements.txt
    startCommand: gunicorn Lector_pdf:app --bind 0.0.0.0:$PORT --timeout 300
    healthCheckPath: /
    envVars:
      - key: PYTHON_VERSION
        value: "3.11"
```

### 10.2 Pasos de Despliegue

1. **Crear cuenta en Render**
   - Ir a https://dashboard.render.com
   - Registrarse con GitHub (recomendado)

2. **Subir código a GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/TU_USUARIO/lector-polizas.git
   git push -u origin main
   ```

3. **Conectar Render con GitHub**
   - En Render Dashboard: "New +" → "Web Service"
   - Autorizar acceso a GitHub
   - Seleccionar repositorio `lector-polizas`

4. **Configurar el servicio**
   - **Name:** `lector-polizas`
   - **Region:** Oregon (más económico)
   - **Branch:** `main`
   - **Root Directory:** (dejar vacío)
   - **Runtime:** Python
   - **Build Command:** se lee de render.yaml
   - **Start Command:** se lee de render.yaml

5. **Desplegar**
   - Click "Create Web Service"
   - Esperar 3-5 minutos
   - URL disponible en: `https://lector-polizas.onrender.com`

### 10.3 Verificación del Despliegue

```bash
# Ver logs en tiempo real
render logs -s lector-polizas

# Probar endpoint
curl https://lector-polizas.onrender.com/
```

### 10.4 Actualización del Despliegue

```bash
# Hacer cambios y empujar
git add .
git commit -m "Descripción del cambio"
git push

# Render detecta el cambio y redeploy automáticamente
```

### 10.5 Monitoreo

- **Logs**: Render Dashboard → Servicio → Logs
- **Métricas**: Render Dashboard → Servicio → Insights
- **Health Check**: GET / devuelve 200 si todo está bien

---

## 11. ESTRUCTURA DEL PROYECTO

```
lector-polizas/
│
├── Lector_pdf.py              # Punto de entrada Flask
│                                # - Rutas de API: /upload, /get-kpis, /download*
│                                # - Configuración de CORS y uploads
│                                # - Cache de Excel de aseguradora en memoria
│
├── src/
│   │
│   ├── parsers/
│   │   └── bolivar_parser.py    # Parser específico para pólizas Bolívar
│   │                              - Extracción con regex de campos específicos
│   │                              - Manejo de formatos de fecha dd/mm/yyyy
│   │                              - Normalización de nombres y números
│   │
│   └── services/
│       ├── ocr_service.py       # Servicio OCR
│       │                          - Extracción primaria con pdfplumber
│       │                          - Fallback a Tesseract si pdfplumber falla
│       │                          - Limita a 3 páginas para optimizar memoria
│       │
│       └── excel_service.py      # Servicio Excel
│                                     - Carga de Excel aseguradora
│                                     - Normalización de headers
│                                     - Comparación inteligente de valores
│                                     - Cálculo de KPIs
│                                     - Generación de archivos Excel formateados
│
├── templates/
│   └── index.html               # Frontend single-page
│                                    - Diseño responsivo (mobile-friendly)
│                                    - Carga de archivos múltiples
│                                    - Procesamiento por lotes
│                                    - Visualización de resultados
│                                    - Dashboard de KPIs
│
├── uploads/                      # Archivos temporales (gitignored)
│
├── requirements.txt              # Dependencias Python
│
├── render.yaml                   # Configuración de despliegue Render
│
├── .gitignore                    # Archivos ignorados por git
│
└── README.md                     # Este archivo
```

### 11.1 Descripción de Archivos Clave

| Archivo | Líneas | Responsabilidad |
|---------|--------|-----------------|
| `Lector_pdf.py` | ~200 | Orquestación, rutas API, cache |
| `bolivar_parser.py` | ~190 | Extracción campos específicos |
| `ocr_service.py` | ~50 | Extracción texto con fallback |
| `excel_service.py` | ~450 | Comparación, KPIs, exportación |
| `index.html` | ~450 | Frontend completo |

---

## 12. USO DE LA APLICACIÓN

### 12.1 Flujo de Usuario

```
┌──────────────────────────────────────────────────────────────────────────┐
│                            INTERFAZ WEB                                  │
└──────────────────────────────────────────────────────────────────────────┘

1️⃣  CONFIGURACIÓN
    └─▶ Seleccionar aseguradora (por ahora solo Bolívar)
    
2️⃣  CARGAR PDFs
    └─▶ Click en "Seleccionar archivos PDF"
    └─▶ Seleccionar múltiples archivos (hasta 40-50 en plan free)
    └─▶ Se muestra lista con nombres y tamaños
    
3️⃣  CARGAR EXCEL ASEGURADORA (Opcional pero recomendado)
    └─▶ Click en "Cargar Excel de la aseguradora"
    └─▶ Seleccionar archivo .xlsx
    └─▶ Se muestra cantidad de registros cargados
    
4️⃣  PROCESAR
    └─▶ Click "Procesar Archivos"
    └─▶ Progreso visible (spinner)
    └─▶ Resultados aparecen en tabla
    └─▶ Botones adicionales se habilitan:
        • Ver KPIs
        • Descargar Excel
        • Descargar Comparativo
    
5️⃣  ANÁLISIS DE RESULTADOS
    └─▶ Revisar tabla de extracción
    └─▶ Click "Ver KPIs" para dashboard de calidad
    └─▶ Revisar campo por campo las coincidencias
```

### 12.2 Interpretación de Resultados

**Tabla de Resultados:**
- Muestra todos los campos extraídos de cada PDF
- Revisar visualmente valores correctos/incorrectos

**Dashboard KPIs:**
- **% Coincidencia Total**: General del proceso
- **Desglose por Campo**: Campo específico vs Excel aseguradora
- Verde (>80%): Aceptable
- Amarillo (50-80%): Revisar
- Rojo (<50%): Problemas significativos

**Archivo Comparativo:**
- Formato vertical: CAMPO | VALOR PDF | VALOR EXCEL | OK/✗/-
- Útil para auditoría detallada

### 12.3 Mejores Prácticas

| Situación | Recomendación |
|-----------|---------------|
| 30-40 PDFs | Cargar todos de una vez |
| 50+ PDFs | Procesar en sesiones separadas |
| PDFs escaneados | Asegurar buena calidad de imagen |
| Nombres con caracteres especiales | Verificar con Excel de aseguradora |
| Fechas inconsistentes | Indica problema en PDF o Excel |

---

## 13. MANTENIMIENTO Y SOPORTE

### 13.1 Mantenimiento Regular

| Tarea | Frecuencia | Responsabilidad |
|-------|------------|-----------------|
| Actualizar dependencias | Mensual | Ejecutar `pip list --outdated` |
| Revisar logs de errores | Semanal | Dashboard Render |
| Backup de configuración | Trimestral | Guardar render.yaml actualizado |
| Test con PDFs de muestra | Mensual | Verificar funcionamiento OCR |

### 13.2 Solución de Problemas Comunes

| Problema | Causa Posible | Solución |
|----------|---------------|----------|
| Error 500 al procesar | Timeout o memoria | Reducir batch de PDFs |
| OCR no extrae texto | PDF escaneado sin texto | Verificar Tesseract instalado |
| Fechas en formato raro | Formato no reconocido | Revisar regex en parser |
| Excel no carga | Formato incompatible | Verificar .xlsx (no .xls) |
| Worker timeout | Procesamiento largo | Reducir PDFs por request |

### 13.3 Agregar Nueva Aseguradora

Para añadir soporte a otra aseguradora:

1. **Crear nuevo parser** en `src/parsers/`:
   ```python
   # src/parsers/suramericana_parser.py
   class SuramericanaParser:
       def __init__(self, text):
           self.text = text
           self.data = {}
       
       def parse(self):
           # Implementar regex específicos
           # para los campos de Suramericana
           pass
   ```

2. **Actualizar frontend** en `templates/index.html`:
   ```html
   <select id="aseguradora">
       <option value="bolivar">Seguros Bolívar</option>
       <option value="suramericana">Suramericana</option>
   </select>
   ```

3. **Agregar ruta en Flask**:
   ```python
   from src.parsers.suramericana_parser import SuramericanaParser
   
   # En upload_files():
   if aseguradora == 'suramericana':
       parser = SuramericanaParser(text)
   ```

### 13.4 Contacto y Soporte

Para soporte técnico o reportes de bugs:
- Crear issue en el repositorio de GitHub
- Incluir: PDF de muestra, Excel de prueba, descripción del problema
- Logs del navegador (F12 → Console)

---

## LICENCIA

Este proyecto es propiedad de la organización. Todos los derechos reservados.

---

## CHANGELOG

### v1.0.0 (Mayo 2026)
- Primera versión funcional
- Extracción OCR para pólizas Bolívar
- Comparación con Excel aseguradora
- Dashboard de KPIs
- Despliegue en Render

### v1.1.0 (Próximo)
- [ ] Soporte para más aseguradoras
- [ ] Historial de procesamientos
- [ ] Exportación a PDF de reportes
- [ ] Autenticación de usuarios

---

*Documentación actualizada: Mayo 2026*