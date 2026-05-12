from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import os
import uuid
import tempfile
import json
from src.services.ocr_service import OCRService
from src.services.excel_service import ExcelService
from src.parsers.bolivar_parser import BolívarParser

app = Flask(__name__)
CORS(app)

app.config['UPLOAD_FOLDER'] = os.environ.get('UPLOAD_FOLDER', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads'))
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

ocr_service = OCRService(dpi=300)
excel_service = ExcelService()
insurer_cache = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    if 'files' not in request.files:
        return jsonify({'error': 'No files provided'}), 400

    files = request.files.getlist('files')
    aseguradora = request.form.get('aseguradora', 'bolivar')

    if not files or all(f.filename == '' for f in files):
        return jsonify({'error': 'No files selected'}), 400

    results = []
    for file in files:
        if file.filename == '':
            continue

        filepath = os.path.join(app.config['UPLOAD_FOLDER'], f"{uuid.uuid4()}_{file.filename}")
        file.save(filepath)

        try:
            text = ocr_service.extract_text_from_pdf(filepath)
            parser = BolívarParser(text)
            data = parser.parse()
            data['ARCHIVO'] = file.filename
            results.append(data)
        except Exception as e:
            results.append({'ARCHIVO': file.filename, 'ERROR': str(e)})
        finally:
            if os.path.exists(filepath):
                os.remove(filepath)

    return jsonify({'success': True, 'results': results})

@app.route('/upload-insurer', methods=['POST'])
def upload_insurer_excel():
    if 'insurer_file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['insurer_file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    cache_key = str(uuid.uuid4())
    safe_filename = f"{cache_key}_{file.filename.replace(' ', '_').replace('-', '_')}"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], safe_filename)
    file.save(filepath)

    try:
        insurer_data = excel_service.load_insurer_excel(filepath)
        insurer_cache[cache_key] = filepath
        return jsonify({'success': True, 'count': len(insurer_data), 'cache_key': cache_key})
    except Exception as e:
        if os.path.exists(filepath):
            os.remove(filepath)
        insurer_cache.pop(cache_key, None)
        return jsonify({'error': str(e)}), 400

@app.route('/get-kpis', methods=['POST'])
def get_kpis():
    data = request.get_json()
    extracted_results = data.get('extracted_results', [])
    cache_key = data.get('cache_key', '')

    insurer_data = []
    if cache_key and cache_key in insurer_cache:
        filepath = insurer_cache[cache_key]
        if os.path.exists(filepath):
            insurer_data = excel_service.load_insurer_excel(filepath)

    kpis = excel_service.calculate_kpis(extracted_results, insurer_data)
    return jsonify({'success': True, 'kpis': kpis})

@app.route('/download', methods=['POST'])
def download_excel():
    data = request.get_json()
    results = data.get('results', [])

    if not results:
        return jsonify({'error': 'No data to export'}), 400

    wb = excel_service.create_workbook(results)

    output_path = os.path.join(tempfile.mkdtemp(), 'resultados_pólizas.xlsx')
    excel_service.save_workbook(wb, output_path)

    return send_file(output_path, as_attachment=True, download_name='resultados_pólizas.xlsx')

@app.route('/download-comparison', methods=['POST'])
def download_comparison():
    try:
        data = request.get_json()
        extracted_results = data.get('extracted_results', [])
        cache_key = data.get('cache_key', '')

        if not extracted_results:
            return jsonify({'error': 'No data to export'}), 400

        insurer_data = []
        if cache_key and cache_key in insurer_cache:
            filepath = insurer_cache[cache_key]
            if os.path.exists(filepath):
                insurer_data = excel_service.load_insurer_excel(filepath)
            else:
                return jsonify({'error': 'El archivo de la aseguradora expiró. Cargue el Excel nuevamente.'}), 400
        else:
            return jsonify({'error': 'Cargue el Excel de la aseguradora primero'}), 400

        wb = excel_service.create_comparison_workbook(extracted_data=extracted_results, insurer_data=insurer_data)

        output_path = os.path.join(tempfile.mkdtemp(), 'comparativo_pólizas.xlsx')
        excel_service.save_workbook(wb, output_path)

        return send_file(output_path, as_attachment=True, download_name='comparativo_pólizas.xlsx')

    except Exception as e:
        import traceback
        print(f'Error in download_comparison: {str(e)}')
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=int(os.environ.get('PORT', 5000)))
