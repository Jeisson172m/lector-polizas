import os
import gc
import subprocess
import tempfile

try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False

class OCRService:
    def __init__(self, dpi=150):
        self.dpi = dpi

    def extract_text_from_pdf(self, pdf_path):
        if not TESSERACT_AVAILABLE:
            return ''
        
        text_pages = []
        
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                output_prefix = os.path.join(tmpdir, 'page')
                
                result = subprocess.run([
                    'pdftoppm',
                    '-r', str(self.dpi),
                    '-jpeg',
                    '-jpegopt', 'quality=70',
                    '-f', '1',
                    '-l', '10',
                    pdf_path,
                    output_prefix
                ], capture_output=True, text=True, timeout=60)
                
                if result.returncode != 0:
                    return ''
                
                pages = sorted([f for f in os.listdir(tmpdir) if f.startswith('page')])
                
                for page_file in pages:
                    page_path = os.path.join(tmpdir, page_file)
                    try:
                        text = pytesseract.image_to_string(page_path, lang='spa', config='--psm 1')
                        text_pages.append(text)
                    except:
                        pass
                    finally:
                        del page_path
                
                del pages
                gc.collect()
                
        except Exception as e:
            print(f'OCR error: {str(e)}')
            return ''
        
        result = '\n\n--- PAGE BREAK ---\n\n'.join(text_pages)
        del text_pages
        gc.collect()
        
        return result