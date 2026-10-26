# Analizador OCR y NLP de comprobantes peruanos

Aplicación académica en Streamlit para extraer texto de facturas, boletas y recibos peruanos, limpiar el resultado, identificar campos relevantes y almacenar cada procesamiento en SQLite.

## Funcionalidades

- Carga múltiple de JPG, JPEG, PNG y PDF.
- Preprocesamiento: redimensionamiento, escala de grises, reducción de ruido, contraste y binarización adaptativa.
- OCR con Tesseract en español, con respaldo automático al idioma disponible.
- Clasificación del comprobante y extracción de RUC, fecha, serie, moneda, subtotal, IGV y total.
- Palabras clave, resumen extractivo y entidades detectadas.
- Persistencia en SQLite, historial consultable y descarga en CSV, JSON o TXT.
- Registros de demostración marcados explícitamente como sintéticos.

## Estructura

```text
app.py                         Aplicación Streamlit
core/                          Lógica de OCR, NLP, imágenes y base de datos
data/facturas_peru.db          Base SQLite inicial
data/sample_facturas.csv       Datos sintéticos de demostración
notebooks/                     Notebook para Google Colab
scripts/init_db.py             Inicialización reproducible de la base
tests/                         Pruebas unitarias
requirements.txt               Dependencias Python
packages.txt                   Dependencias del sistema para Streamlit Cloud
```

## Ejecución local

1. Instalar Python 3.10 o superior y Tesseract OCR con el idioma español.
2. Crear un entorno virtual.
3. Ejecutar `pip install -r requirements.txt`.
4. Ejecutar `python scripts/init_db.py`.
5. Ejecutar `streamlit run app.py`.
6. Abrir `http://localhost:8501`.

### Windows

Instalar Tesseract y, si no queda en el PATH, definir `TESSERACT_CMD` con la ruta completa del ejecutable. Para PDF, instalar Poppler y agregar su carpeta `bin` al PATH.

```powershell
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
$env:TESSERACT_CMD="C:\Program Files\Tesseract-OCR\tesseract.exe"
python scripts\init_db.py
streamlit run app.py
```

### macOS

```bash
brew install tesseract tesseract-lang poppler
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/init_db.py
streamlit run app.py
```

### Ubuntu o Debian

```bash
sudo apt update
sudo apt install tesseract-ocr tesseract-ocr-spa poppler-utils
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/init_db.py
streamlit run app.py
```

## Despliegue en Streamlit Community Cloud

1. Crear un repositorio en GitHub y subir esta carpeta.
2. Entrar a Streamlit Community Cloud y seleccionar el repositorio.
3. Indicar `app.py` como archivo principal.
4. Desplegar. `requirements.txt` instalará Python y `packages.txt` instalará Tesseract y Poppler.
5. Realizar una prueba con comprobantes anonimizados.

SQLite en Streamlit Cloud es apropiado para demostración, pero el disco puede reiniciarse. Para producción se recomienda PostgreSQL y almacenamiento privado de archivos.

## Uso con facturas reales

1. Omitir o cubrir datos personales que no sean necesarios.
2. Subir archivos legibles, rectos y con buena iluminación.
3. Revisar visualmente los campos extraídos.
4. Corregir los campos desde la aplicación antes de guardar.
5. Exportar el historial para comparar con una ficha de verdad terreno.

## Pruebas

```bash
python -m unittest discover -s tests -v
```

## Consideraciones éticas

No se deben publicar comprobantes reales con nombres, direcciones, firmas, tarjetas u otros datos personales. El proyecto guarda texto y resultados; no conserva la imagen original. Para un uso empresarial se debe añadir autenticación, cifrado, control de acceso, copias de seguridad y política de retención.

