import re
from datetime import datetime

class BolívarParser:
    def __init__(self, text):
        self.text = text
        self.data = {}
        self._init_defaults()

    def _init_defaults(self):
        self.data = {
            'POLIZA': '', 'PLACA': '', 'MARCA': '', 'LÍNEA': '',
            'TOMADOR': '', 'NOMBRE TOMADOR': '', 'ASEGURADO': '',
            'NOMBRE ASEGURADO': '', 'CELULAR': '', 'CORREO': '',
            'NIT ONEROSO': '', 'BENEFICIARIO ONEROSO': '',
            'FECHA INICIO VIGE': '', 'FECHA VENC': '',
            'VALOR ASEGURADO 2024': '', 'VALOR ASEGURADO 2025': '',
            'SINIESTROS': 'NO', 'PRIMA NETA 2024': '', 'PRIMA TOTAL 2024': '',
            'PRIMA NETA 2025': '', 'PRIMA TOTAL 2025': '',
            'VARIACIÓN PRIMA NETA': '', 'VARIACIÓN PRIMA TOTAL': ''
        }

    def parse(self):
        self._extract_numero_poliza()
        self._extract_placa()
        self._extract_marca_linea()
        self._extract_tomador_asegurado()
        self._extract_fechas()
        self._extract_valor_asegurado()
        self._extract_primas()
        return self.data

    def _extract_numero_poliza(self):
        text_lower = self.text.lower()
        patterns = [
            r'poliza\s*no:\s*(\d+)',
            r'poliza\s*n[º\.]*\s*(\d+)',
            r'poliza\s*a\s+la\s+cual\s+accede\s*n[º\.]*\s*(\d+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, text_lower)
            if match:
                poliza_num = match.group(1).strip()
                if len(poliza_num) >= 10:
                    self.data['POLIZA'] = poliza_num
                    return

        nums = re.findall(r'(\d{10,13})', self.text)
        for num in nums:
            if num.startswith('1') and not num.startswith('31'):
                self.data['POLIZA'] = num
                return

    def _extract_placa(self):
        match = re.search(r'PLACA\s+([A-Z]{3}\d{3})', self.text, re.IGNORECASE)
        if match:
            self.data['PLACA'] = match.group(1).strip().upper()
            return

        match = re.search(r'\b([A-Z]{3}\d{3})\b', self.text)
        if match:
            self.data['PLACA'] = match.group(1).upper()

    def _extract_marca_linea(self):
        match = re.search(r'MARCA\s+([A-Z]+)\s+([^\n]+?)(?:\s*\d{4}\s|MODELO|TIPO|COLOR|$)', self.text, re.IGNORECASE)
        if match:
            self.data['MARCA'] = match.group(1).strip()
            self.data['LÍNEA'] = match.group(2).strip()
            return

        match = re.search(r'MARCA\s+([A-Z]+)\s+([^\n]+)', self.text, re.IGNORECASE)
        if match:
            self.data['MARCA'] = match.group(1).strip()
            self.data['LÍNEA'] = match.group(2).strip().split()[0]

    def _extract_tomador_asegurado(self):
        lines = self.text.split('\n')

        tomador_encontrado = False
        asegurado_encontrado = False

        for i, line in enumerate(lines):
            line_clean = line.strip()

            if not tomador_encontrado and re.search(r'datos\s*del\s*tomador', line_clean, re.IGNORECASE):
                for j in range(i, min(i + 6, len(lines))):
                    sig_line = lines[j].strip()

                    match = re.match(r'^NOMBRE:\s*([A-Z][A-Za-zÁÉÍÓÚÑ\s\.]+?)\s*$', sig_line)
                    if match:
                        nombre_tomador = match.group(1).strip()
                        if j + 1 < len(lines):
                            id_line = lines[j + 1].strip()
                            id_match = re.search(r'IDENTIFICACI[ÓO]N:\s*(\d{7,10})', id_line)
                            if id_match:
                                self.data['NOMBRE TOMADOR'] = nombre_tomador
                                self.data['TOMADOR'] = id_match.group(1).strip()
                                tomador_encontrado = True
                                break
                    elif re.search(r'^NOMBRE:', sig_line) and 'IDENTIFICACI' in sig_line:
                        full_match = re.match(r'^NOMBRE:\s*([A-Z][A-Za-zÁÉÍÓÚÑ\s\.]+)\s*IDENTIFICACI[ÓO]N:\s*(\d{7,10})', sig_line)
                        if full_match:
                            self.data['NOMBRE TOMADOR'] = full_match.group(1).strip()
                            self.data['TOMADOR'] = full_match.group(2).strip()
                            tomador_encontrado = True
                            break
                if tomador_encontrado:
                    continue

            if not asegurado_encontrado and re.search(r'asegurado\s+n\.?\s*1', line_clean, re.IGNORECASE):
                for j in range(i, min(i + 5, len(lines))):
                    sig_line = lines[j].strip()
                    name_id = re.match(r'^([A-Z][A-Za-zÁÉÍÓÚÑ\s]+?)\s+(\d{7,10})$', sig_line)
                    if name_id:
                        nombre = name_id.group(1).strip()
                        identificacion = name_id.group(2).strip()
                        if len(nombre) > 5 and nombre not in ['MODELO', 'TIPO', 'COLOR']:
                            self.data['NOMBRE ASEGURADO'] = nombre
                            self.data['ASEGURADO'] = identificacion
                            asegurado_encontrado = True
                            break

        if not tomador_encontrado:
            for i, line in enumerate(lines):
                if re.search(r'NOMBRE\s+IDENTIFICACI', line, re.IGNORECASE):
                    if i + 1 < len(lines):
                        next_line = lines[i + 1].strip()
                        name_id = re.match(r'^([A-Z][A-Za-zÁÉÍÓÚÑ\s]+?)\s+(\d{7,10})$', next_line)
                        if name_id:
                            nombre = name_id.group(1).strip()
                            identificacion = name_id.group(2).strip()
                            if len(nombre) > 5 and nombre not in ['MODELO', 'TIPO', 'COLOR']:
                                if not self.data['NOMBRE TOMADOR']:
                                    self.data['NOMBRE TOMADOR'] = nombre
                                    self.data['TOMADOR'] = identificacion
                                    tomador_encontrado = True
                                elif not self.data['NOMBRE ASEGURADO']:
                                    self.data['NOMBRE ASEGURADO'] = nombre
                                    self.data['ASEGURADO'] = identificacion
                                    break

    def _extract_fechas(self):
        patterns_inicio = [
            r'(?:DESDE|OBSERVACIONES:)\s*(\d{2}/\d{2}/\d{4})',
            r'(\d{2}/\d{2}/\d{4})\s*-?\s*HASTA',
            r'INICIO.*?(\d{2}/\d{2}/\d{4})',
        ]
        for pattern in patterns_inicio:
            inicio_match = re.search(pattern, self.text, re.IGNORECASE)
            if inicio_match:
                self.data['FECHA INICIO VIGE'] = self._parse_date(inicio_match.group(1))
                break

        patterns_fin = [
            r'HASTA\s+VIGENCIA\s*(\d{2}/\d{2}/\d{4})',
            r'Hasta.*?(\d{2}/\d{2}/\d{4})',
            r'FIN.*?(\d{2}/\d{2}/\d{4})',
        ]
        for pattern in patterns_fin:
            fin_match = re.search(pattern, self.text, re.IGNORECASE)
            if fin_match:
                self.data['FECHA VENC'] = self._parse_date(fin_match.group(1))
                break

    def _parse_date(self, date_str):
        for fmt in ['%d/%m/%Y', '%d-%m-%Y', '%Y-%m-%d']:
            try:
                dt = datetime.strptime(date_str.strip(), fmt)
                return dt.strftime('%d/%m/%Y')
            except:
                continue
        return date_str

    def _extract_valor_asegurado(self):
        valor_comercial = re.search(r'VALOR\s*COMERCIAL\*\s*\$\s*([\d,.]+)', self.text, re.IGNORECASE)
        if valor_comercial:
            valor_str = valor_comercial.group(1).replace('.', '').replace(',', '')
            try:
                self.data['VALOR ASEGURADO 2025'] = float(valor_str)
            except:
                self.data['VALOR ASEGURADO 2025'] = valor_str

    def _extract_primas(self):
        prima_neta_match = re.search(r'VALOR\s*DE\s*LA?\s*PRIMA[:\s]*\$\s*([\d,.]+)', self.text, re.IGNORECASE)
        if not prima_neta_match:
            prima_neta_match = re.search(r'VALOR\s*DE\s*LAPRIMA\s*\$\s*([\d,.]+)', self.text, re.IGNORECASE)

        total_pagar_match = re.search(r'TOTALAPAGAR\s*\$\s*([\d,.]+)', self.text, re.IGNORECASE)
        if not total_pagar_match:
            total_pagar_match = re.search(r'TOTAL\s*A\s*PAGAR\s*\$\s*([\d,.]+)', self.text, re.IGNORECASE)

        if prima_neta_match:
            valor_str = prima_neta_match.group(1).replace('.', '').replace(',', '')
            try:
                self.data['PRIMA NETA 2025'] = float(valor_str)
            except:
                pass

        if total_pagar_match:
            valor_str = total_pagar_match.group(1).replace('.', '').replace(',', '')
            try:
                self.data['PRIMA TOTAL 2025'] = float(valor_str)
            except:
                pass
