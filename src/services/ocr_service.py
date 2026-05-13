import os
import gc
import re
import pdfplumber
from PIL import Image

try:
    import pytesseract
    import pdf2image
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False

class OCRService:
    def __init__(self, dpi=200):
        self.dpi = dpi

    def extract_text_from_pdf(self, pdf_path):
        text_pages = []
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                max_pages = min(len(pdf.pages), 3)
                for i in range(max_pages):
                    page = pdf.pages[i]
                    text = page.extract_text()
                    if text and len(text.strip()) > 50:
                        text_pages.append(text)
        except:
            pass
        
        if not text_pages or all(page.strip() == '' for page in text_pages):
            if TESSERACT_AVAILABLE:
                text_pages = self._extract_with_tesseract(pdf_path)
        
        result = '\n\n--- PAGE BREAK ---\n\n'.join(text_pages)
        del text_pages
        gc.collect()
        return result

    def _extract_with_tesseract(self, pdf_path):
        text_pages = []
        images = None
        
        try:
            with open(pdf_path, 'rb') as f:
                pdf_bytes = f.read()
            
            images = pdf2image.convert_from_bytes(
                pdf_bytes,
                dpi=self.dpi,
                fmt='png',
                thread_count=1,
                last_page=3
            )
            del pdf_bytes
            
            for img in images[:3]:
                text = pytesseract.image_to_string(img, lang='spa')
                text_pages.append(text)
                
        except Exception as e:
            print(f'Tesseract error: {str(e)}')
        finally:
            if images:
                del images
            gc.collect()
        
        return text_pages