import os
import re
import pdf2image
import pytesseract
import pdfplumber
from PIL import Image

class OCRService:
    def __init__(self, dpi=300):
        self.dpi = dpi

    def extract_text_from_pdf(self, pdf_path):
        text_pages = []
        
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    text_pages.append(text)
        
        if not text_pages or all(page.strip() == '' for page in text_pages):
            text_pages = self._extract_with_tesseract(pdf_path)
        
        return '\n\n--- PAGE BREAK ---\n\n'.join(text_pages)

    def _extract_with_tesseract(self, pdf_path):
        text_pages = []
        images = pdf2image.convert_from_bytes(
            open(pdf_path, 'rb').read(),
            dpi=self.dpi
        )
        for img in images:
            text = pytesseract.image_to_string(img, lang='spa')
            text_pages.append(text)
        return text_pages

    def extract_text_by_regions(self, pdf_path, regions):
        images = pdf2image.convert_from_bytes(
            open(pdf_path, 'rb').read(),
            dpi=self.dpi
        )
        results = {}
        for region_name, coords in regions.items():
            page_idx = coords.get('page', 0)
            if page_idx < len(images):
                x, y, w, h = coords['x'], coords['y'], coords['width'], coords['height']
                img_region = images[page_idx].crop((x, y, x + w, y + h))
                text = pytesseract.image_to_string(img_region, lang='spa')
                results[region_name] = text
        return results
