
import io
import logging
import re
import os
from datetime import datetime, date
from decimal import Decimal

# Try to import correpy but be robust
try:
    from correpy.parsers.brokerage_notes.parser_factory import ParserFactory
    from correpy.domain.entities.brokerage_note import BrokerageNote
    # Mock classes if we need to return compatible objects
except ImportError:
    # If correpy missing, define mocks
    ParserFactory = None
    BrokerageNote = None

# Try to import pdfminer
try:
    from pdfminer.high_level import extract_text
    from pdfminer.layout import LAParams
except ImportError:
    extract_text = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MockFinancialSummary:
    def __init__(self, val):
        self.net_settlement_value = val


class MockNote:
    def __init__(self, ref_date: date, val: float, observation: str = ""):
        self.reference_date = ref_date
        self.financial_summary = MockFinancialSummary(val)
        self.observation = observation


class PdfParser:
    def parse_file(self, file_path: str):
        """
        Parses a brokerage note PDF file and returns a list of BrokerageNote-like objects.
        Returns empty list if parsing fails.
        """
        notes = []

        # 1. Try CorrePy (only if likely standard Note, skip if specific known failure cases? No, try generally)
        if ParserFactory:
            try:
                # Capture stderr to avoid noise if it fails
                with open(file_path, 'rb') as f:
                    content = io.BytesIO(f.read())

                parser = ParserFactory(brokerage_note=content)
                notes = parser.parse()
                if notes:
                    logger.info(f"Parsed {len(notes)} notes from {file_path} using CorrePy")
                    return notes
            except Exception:
                pass

        # 2. Fallback
        return self._parse_fallback(file_path)

    def _parse_fallback(self, file_path: str):
        if not extract_text:
            logger.warning("pdfminer not available for fallback parsing.")
            return []

        try:
            # Extract text
            text = extract_text(file_path, laparams=LAParams())

            # Method A: Specific "LÍQUIDO PARA" Extraction (Futures & Stocks)
            # 1. Clean Text
            clean_text = text.replace('□', '.')

            # 2. Try strict regex
            # Captures date (optional) and value based on "Líquido para" pattern
            liquid_regex = re.search(
                r'L[IÍ\.]?.?QUIDO\s*PARA.*?(\d{2}/\d{2}/\d{4})?.*?([\d\.,]+)\s*([CD])',
                clean_text,
                re.IGNORECASE | re.DOTALL)

            val = Decimal(0)
            ref_date = None
            observation = ""

            # Data Extraction
            if liquid_regex:
                date_str = liquid_regex.group(1)
                val_str = liquid_regex.group(2)
                sign = liquid_regex.group(3)

                if date_str:
                    try:
                        ref_date = datetime.strptime(date_str, '%d/%m/%Y').date()
                    except ValueError:
                        pass

                try:
                    clean_val = val_str.replace('.', '').replace(',', '.')
                    val = Decimal(clean_val)
                    if sign == 'D':
                        val = -val
                except BaseException:
                    pass

            # Fallback for Value: Largest X,XX [CD] found in text
            if val == 0:
                # Look for all "Number + C/D"
                # Exclude 0,00
                matches = re.findall(r'(\d{1,3}(?:\.\d{3})*,\d{2})\s*([CD])', clean_text)
                max_abs_val = Decimal(0)

                for v_str, s_char in matches:
                    if v_str == "0,00":
                        continue
                    try:
                        c_val = Decimal(v_str.replace('.', '').replace(',', '.'))
                        if c_val > max_abs_val:
                            max_abs_val = c_val
                            val = -c_val if s_char == 'D' else c_val
                    except BaseException:
                        pass

            # Fallback for Date: Filename
            if not ref_date:
                filename = os.path.basename(file_path)
                date_match = re.search(r'(\d{2}-\d{2}-\d{4})', filename)
                if date_match:
                    try:
                        ref_date = datetime.strptime(date_match.group(1), '%d-%m-%Y').date()
                    except BaseException:
                        ref_date = date.today()
                else:
                    ref_date = date.today()

            # Asset Identification
            # 1. Futures (WIN/WDO)
            asset_match = re.search(r'(WIN|WDO)[A-Z]\d{2}', clean_text)
            if asset_match:
                code_type = asset_match.group(1)
                observation = f"{code_type}"

            # 2. Stocks/Options (Ticker heuristic)
            else:
                # Look for Ticker: 4 letters + alphanumeric suffixes
                # Ignored common words
                ignored = {'PARA', 'DATA', 'NOTA', 'PAGTO', 'VALOR', 'TOTAL', 'LOCAL', 'PRAZO', 'PRECO', 'FOLHA'}

                # Regex for potential tickers
                ticker_candidates = re.findall(r'\b([A-Z]{4}[A-Z0-9]{1,4})\b', clean_text)

                found_ticker = ""
                for cand in ticker_candidates:
                    if cand not in ignored and not re.match(r'^[A-Z]+$', cand):
                        # Require at least one digit to distinguish from words
                        if any(c.isdigit() for c in cand):
                            found_ticker = cand
                            break

                if found_ticker:
                    # Look for Operation (C/V)
                    op = "?"
                    if re.search(r'\bC\b', clean_text) and not re.search(r'\bV\b', clean_text):
                        op = "C"
                    elif re.search(r'\bV\b', clean_text) and not re.search(r'\bC\b', clean_text):
                        op = "V"
                    else:
                        # Scan common lines
                        if "BOVESPA C" in clean_text or "BOVESPA 1 C" in clean_text or "1-BOVESPA C" in clean_text:
                            op = "C"
                        elif "BOVESPA V" in clean_text or "BOVESPA 1 V" in clean_text or "1-BOVESPA V" in clean_text:
                            op = "V"

                    # Last Resort: Infer from Value Sign (Net Settlement)
                    # Debit (Negative) -> Purchase (C)
                    # Credit (Positive) -> Sale (V)
                    if op == "?":
                        if val < 0:
                            op = "C"
                        elif val > 0:
                            op = "V"

                    observation = f"{found_ticker} - {op}"

            if val != 0:
                logger.info(
                    f"Parsed via Heuristic: Date={ref_date}, Value={val}, Obs={observation} from {
                        os.path.basename(file_path)}")
                return [MockNote(ref_date, float(val), observation)]

            # Method B: Generic Currency Extraction (Legacy)
            # ... (Existing logic) ...
            matches = re.findall(r'R\$\s*([\d\.,]+)', text)

            max_val = Decimal(0)
            for m in matches:
                clean_m = m.strip()
                if clean_m and clean_m[-1] in '.,':
                    clean_m = clean_m[:-1]

                try:
                    if ',' in clean_m:
                        val_str = clean_m.replace('.', '').replace(',', '.')
                    else:
                        val_str = clean_m

                    current_val = Decimal(val_str)
                    if abs(current_val) > abs(max_val):
                        max_val = current_val
                except BaseException:
                    continue

            # Extract Date from Filename
            filename = os.path.basename(file_path)
            date_match = re.search(r'(\d{2}-\d{2}-\d{4})', filename)

            if date_match:
                try:
                    # filename often uses dash
                    dt = datetime.strptime(date_match.group(1), '%d-%m-%Y')
                    ref_date = dt.date()
                except BaseException:
                    pass

            if max_val == 0:
                # logger.warning(f"Could not extract value from {filename}")
                return []

            # logger.info(f"Fallback extracted: Date={ref_date}, Value={max_val} from {filename}")
            return [MockNote(ref_date, float(max_val))]

        except Exception as e:
            logger.error(f"Fallback parsing error for {file_path}: {e}")
            return []
