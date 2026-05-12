# Lector de Pólizas PDF

Aplicación web para extraer datos de pólizas de seguros Bolívar mediante OCR y comparar con el Excel de la aseguradora.

## Requisitos Previos

- Python 3.11+
- Tesseract OCR instalado en el sistema
- Para desarrollo: `pip install -r requirements.txt`

## Instalación Local

```bash
# Clonar o descargar el proyecto
cd Lector_pdf

# Instalar dependencias
pip install -r requirements.txt

# Asegúrate de tener Tesseract OCR instalado
# En Windows: https://github.com/UB-Mannheim/tesseract/wiki
# En Ubuntu: sudo apt-get install tesseract-ocr tesseract-ocr-spa
# En Mac: brew install tesseract tesseract-lang

# Ejecutar
python Lector_pdf.py
```

Abrir en el navegador: http://localhost:5000

## Despliegue en Render (Gratis)

### Pasos:

1. **Crear cuenta en [Render.com](https://render.com)** (gratis con email)

2. **Subir proyecto a GitHub:**
   ```bash
   # Crea repositorio en GitHub y sube el código
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/TU_USUARIO/Lector_polizas.git
   git push -u origin main
   ```

3. **Conectar en Render:**
   - Ve a https://dashboard.render.com
   - Click "New +" → "Web Service"
   - Conecta tu cuenta de GitHub
   - Selecciona el repositorio
   - Configura:
     - **Name:** lector-polizas
     - **Region:** Oregon (más económico)
     - **Branch:** main
     - **Build Command:** `pip install -r requirements.txt`
     - **Start Command:** `gunicorn Lector_pdf:app --bind 0.0.0.0:$PORT`

4. **Desplegar:**
   - Click "Create Web Service"
   - Espera (~3-5 minutos)
   - Obtén la URL: `https://lector-polizas.onrender.com`

### Limitaciones de Render (Plan Free):
- El servicio "duerme" después de 15 min de inactividad
- 750 horas/mes gratis
- 512 MB RAM máximo

### Para mejorar rendimiento:
- En Render Dashboard → tu servicio → Environment
- Agregar variable: `GUNICORN_WORKERS=2`

## Estructura del Proyecto

```
Lector_pdf/
├── Lector_pdf.py          # Aplicación Flask principal
├── templates/
│   └── index.html         # Interfaz web
├── src/
│   ├── parsers/
│   │   └── bolivar_parser.py  # Lógica de extracción OCR
│   └── services/
│       ├── ocr_service.py     # Servicio OCR
│       └── excel_service.py   # Generación de Excel
├── requirements.txt       # Dependencias Python
├── Procfile              # Para despliegue (opcional)
└── render.yaml           # Configuración Render
```

## Uso

1. Seleccionar aseguradora (Bolívar)
2. Cargar PDFs de pólizas
3. Cargar Excel de la aseguradora (opcional)
4. Procesar archivos
5. Descargar resultados o comparativo

## Notas Importantes

- La extracción de datos depende de la calidad del OCR
- Algunos campos pueden no estar en todos los PDFs
- Compatible principalmente con pólizas de Seguros Bolívar
