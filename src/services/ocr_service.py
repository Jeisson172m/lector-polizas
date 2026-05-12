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
        
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    text_pages.append(text)
        
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
                fmt='png'
            )
            del pdf_bytes
            
            for i, img in enumerate(images):
                text = pytesseract.image_to_string(img, lang='spa')
                text_pages.append(text)
                del img
                gc.collect()
                
        finally:
            if images:
                del images
            gc.collect()
        
        return text_pages

    def extract_text_by_regions(self, pdf_path, regions):
        if not TESSERACT_AVAILABLE:
            return {}
        
        results = {}
        images = None
        
        try:
            with open(pdf_path, 'rb') as f:
                pdf_bytes = f.read()
            
            images = pdf2image.convert_from_bytes(
                pdf_bytes,
                dpi=self.dpi,
                fmt='png'
            )
            del pdf_bytes
            
            for region_name, coords in regions.items():
                page_idx = coords.get('page', 0)
                if page_idx < len(images):
                    x, y, w, h = coords['x'], coords['y'], coords['width'], coords['height']
                    img_region = images[page_idx].crop((x, y, x + w, y + h))
                    text = pytesseract.image_to_string(img_region, lang='spa')
                    results[region_name] = text
                    del img_region
                    gc.collect()
                    
        finally:
            if images:
                del images
            gc.collect()
        
        return results