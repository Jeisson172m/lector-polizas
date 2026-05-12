from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import os
import uuid
import tempfile
import json
import traceback
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
    print('[UPLOAD] Starting file processing...')
    if 'files' not in request.files:
        print('[UPLOAD] No files in request')
        return jsonify({'error': 'No files provided'}), 400

    files = request.files.getlist('files')
    aseguradora = request.form.get('aseguradora', 'bolivar')
    print(f'[UPLOAD] files: {len(files)}, aseguradora: {aseguradora}')

    if not files or all(f.filename == '' for f in files):
        print('[UPLOAD] No files selected')
        return jsonify({'error': 'No files selected'}), 400

    results = []
    for file in files:
        if file.filename == '':
            continue

        filepath = os.path.join(app.config['UPLOAD_FOLDER'], f"{uuid.uuid4()}_{file.filename}")
        file.save(filepath)
        print(f'[UPLOAD] Processing: {file.filename}')

        try:
            text = ocr_service.extract_text_from_pdf(filepath)
            print(f'[UPLOAD] OCR extracted {len(text)} chars from {file.filename}')
            parser = BolívarParser(text)
            data = parser.parse()
            data['ARCHIVO'] = file.filename
            results.append(data)
            print(f'[UPLOAD] Parsed {file.filename}: POLIZA={data.get("POLIZA", "N/A")}')
        except Exception as e:
            print(f'[UPLOAD] ERROR processing {file.filename}: {str(e)}')
            print(traceback.format_exc())
            results.append({'ARCHIVO': file.filename, 'ERROR': str(e)})
        finally:
            if os.path.exists(filepath):
                os.remove(filepath)

    print(f'[UPLOAD] Done. {len(results)} results')
    return jsonify({'success': True, 'results': results})

@app.route('/upload-insurer', methods=['POST'])
def upload_insurer_excel():
    print('[UPLOAD-INSURER] Starting...')
    if 'insurer_file' not in request.files:
        print('[UPLOAD-INSURER] No file in request')
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['insurer_file']
    if file.filename == '':
        print('[UPLOAD-INSURER] Empty filename')
        return jsonify({'error': 'No file selected'}), 400

    cache_key = str(uuid.uuid4())
    safe_filename = f"{cache_key}_{file.filename.replace(' ', '_').replace('-', '_')}"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], safe_filename)
    file.save(filepath)
    print(f'[UPLOAD-INSURER] Saved: {safe_filename}')

    try:
        insurer_data = excel_service.load_insurer_excel(filepath)
        insurer_cache[cache_key] = filepath
        print(f'[UPLOAD-INSURER] Loaded {len(insurer_data)} rows, cache_key={cache_key}')
        return jsonify({'success': True, 'count': len(insurer_data), 'cache_key': cache_key})
    except Exception as e:
        print(f'[UPLOAD-INSURER] ERROR: {str(e)}')
        print(traceback.format_exc())
        if os.path.exists(filepath):
            os.remove(filepath)
        insurer_cache.pop(cache_key, None)
        return jsonify({'error': str(e)}), 400

@app.route('/get-kpis', methods=['POST'])
def get_kpis():
    print('[GET-KPIS] Starting...')
    data = request.get_json()
    extracted_results = data.get('extracted_results', [])
    cache_key = data.get('cache_key', '')
    print(f'[GET-KPIS] extracted: {len(extracted_results)}, cache_key: {cache_key[:8] if cache_key else "None"}...')

    insurer_data = []
    if cache_key and cache_key in insurer_cache:
        filepath = insurer_cache[cache_key]
        print(f'[GET-KPIS] Cache hit: {filepath}')
        if os.path.exists(filepath):
            insurer_data = excel_service.load_insurer_excel(filepath)
            print(f'[GET-KPIS] Loaded {len(insurer_data)} insurer rows')
        else:
            print('[GET-KPIS] File expired from cache')
    else:
        print(f'[GET-KPIS] Cache miss. Available keys: {list(insurer_cache.keys())}')

    try:
        kpis = excel_service.calculate_kpis(extracted_results, insurer_data)
        print(f'[GET-KPIS] KPIs calculated')
        return jsonify({'success': True, 'kpis': kpis})
    except Exception as e:
        print(f'[GET-KPIS] ERROR: {str(e)}')
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@app.route('/download', methods=['POST'])
def download_excel():
    print('[DOWNLOAD] Starting...')
    data = request.get_json()
    results = data.get('results', [])

    if not results:
        print('[DOWNLOAD] No data')
        return jsonify({'error': 'No data to export'}), 400

    print(f'[DOWNLOAD] Creating workbook with {len(results)} rows')
    wb = excel_service.create_workbook(results)

    output_path = os.path.join(tempfile.mkdtemp(), 'resultados_pólizas.xlsx')
    excel_service.save_workbook(wb, output_path)
    print(f'[DOWNLOAD] Saved to {output_path}')

    return send_file(output_path, as_attachment=True, download_name='resultados_pólizas.xlsx')

@app.route('/download-comparison', methods=['POST'])
def download_comparison():
    print('[DOWNLOAD-COMPARISON] Starting...')
    try:
        data = request.get_json()
        extracted_results = data.get('extracted_results', [])
        cache_key = data.get('cache_key', '')
        print(f'[DOWNLOAD-COMPARISON] extracted: {len(extracted_results)}, cache_key: {cache_key[:8] if cache_key else "None"}')

        if not extracted_results:
            print('[DOWNLOAD-COMPARISON] No data')
            return jsonify({'error': 'No data to export'}), 400

        insurer_data = []
        if cache_key and cache_key in insurer_cache:
            filepath = insurer_cache[cache_key]
            if os.path.exists(filepath):
                insurer_data = excel_service.load_insurer_excel(filepath)
                print(f'[DOWNLOAD-COMPARISON] Loaded {len(insurer_data)} insurer rows')
            else:
                print('[DOWNLOAD-COMPARISON] File expired')
                return jsonify({'error': 'El archivo de la aseguradora expiró. Cargue el Excel nuevamente.'}), 400
        else:
            print('[DOWNLOAD-COMPARISON] No cache key')
            return jsonify({'error': 'Cargue el Excel de la aseguradora primero'}), 400

        print('[DOWNLOAD-COMPARISON] Creating comparison workbook...')
        wb = excel_service.create_comparison_workbook(extracted_data=extracted_results, insurer_data=insurer_data)

        output_path = os.path.join(tempfile.mkdtemp(), 'comparativo_pólizas.xlsx')
        excel_service.save_workbook(wb, output_path)
        print(f'[DOWNLOAD-COMPARISON] Saved to {output_path}')

        return send_file(output_path, as_attachment=True, download_name='comparativo_pólizas.xlsx')

    except Exception as e:
        print(f'[DOWNLOAD-COMPARISON] ERROR: {str(e)}')
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=int(os.environ.get('PORT', 5000)))