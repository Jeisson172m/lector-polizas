import os
import gc
import io
from PIL import Image

try:
    import pytesseract
    import pdf2image
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
        images = None
        
        try:
            with open(pdf_path, 'rb') as f:
                pdf_bytes = f.read()
            
            images = pdf2image.convert_from_bytes(
                pdf_bytes,
                dpi=self.dpi,
                fmt='jpeg',
                thread_count=1
            )
            del pdf_bytes
            
            for img in images:
                text = pytesseract.image_to_string(img, lang='spa', config='--psm 1')
                text_pages.append(text)
                
        finally:
            if images:
                del images
            gc.collect()
        
        result = '\n\n--- PAGE BREAK ---\n\n'.join(text_pages)
        del text_pages
        gc.collect()
        
        return result