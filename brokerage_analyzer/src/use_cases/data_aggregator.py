

import os
from collections import defaultdict
from datetime import datetime
from tqdm import tqdm
from brokerage_analyzer.src.infrastructure.pdf_parser import PdfParser

class DataAggregator:
    def __init__(self):
        self.parser = PdfParser()
        self.records = []

    def process_directory(self, directory_path: str, asset_class: str):
        if not os.path.exists(directory_path):
            return

        files = [f for f in os.listdir(directory_path) if f.lower().endswith('.pdf')]
        
        for filename in tqdm(files, desc=f"Parsing {asset_class}"):
            file_path = os.path.join(directory_path, filename)
            self.process_single_pdf(file_path, asset_class)

    def process_single_pdf(self, file_path: str, asset_class: str):
        filename = os.path.basename(file_path)
        notes = self.parser.parse_file(file_path)
        
        for note in notes:
            try:
                # Access net value (try different possible attribute names from the mock or real object)
                liquid_value = note.financial_summary.net_settlement_value
                ref_date = note.reference_date
                
                # Refine Asset Class and determine Category
                current_asset_class = asset_class
                category = asset_class
                
                if hasattr(note, 'observation') and note.observation:
                    obs = note.observation
                    current_asset_class = f"{obs}" if asset_class == 'Fundos e Acoes' else f"{asset_class} - {obs}"
                    
                    # Categorization Logic
                    if asset_class == 'Fundos e Acoes':
                        # Extract potential ticker from observation (e.g. "PETR4 - V" -> "PETR4")
                        ticker_part = obs.split(' - ')[0].strip().upper()
                        
                        # List of common Brazilian ETFs (Expanded)
                        etf_list = {
                            'BOVA11', 'BOVV11', 'BOVB11', 'BBOV11', 'BOVX11', 'SMAL11', 'SMALL11', 
                            'IVVB11', 'SPXI11', 'ACWI11', 'NASD11', 'EWBZ11', 'BLOK11', 'BEST11', 
                            'BBOI11', 'BMMT11', 'BREW11', 'BCIC11', 'IMAB11', 'IB5M11', 'IRFM11', 
                            'FIXA11', 'LFTB11', 'LFTS11', 'DEBB11', 'NTNS11', 'BNDX11', 'XIFX11', 
                            'AGRI11', 'ALUG11', 'DIVO11', 'DIVD11', 'NDIV11', '5GTK11', 'ELAS11', 
                            'USTK11', 'TECK11', 'SPYI11', 'XINA11', 'DOLA11', 'HASH11', 'BITH11', 
                            'ETHE11', 'QBTC11', 'QETH11', 'QSOL11', 'SOLH11', 'CRPT11', 'COIN11', 
                            'GOLD11', 'GLDX11', 'BSLV39', 'EURP11', 'ASIA11', 'AURO11', 'AUVP11', 
                            'ARGE11', 'BDAP11', 'BDOM11', 'BDEF11', 'B5MB11', 'B5P211'
                        }

                        if ticker_part in etf_list:
                            category = 'ETFs'
                        elif ticker_part.endswith('11'):
                            category = 'FIIs' # Default assumption for 11 if not in ETF list
                        elif any(ticker_part.endswith(digit) for digit in ['3', '4', '5', '6']):
                            category = 'Ações'
                        else:
                            category = 'Outros' # Fallback -> "Fundos e Ações" original or just "Outros"

                    elif asset_class == 'Futuros':
                            # User wants separate sheets for WIN/WDO ("Original Futures")
                            category = f"Futuros - {obs}"
                            current_asset_class = obs 
                
                # Calculate Buy/Sell Values
                # Only for Stocks/FIIs/Etc. Futures use daily adjustment (LiquidValue).
                buy_value = 0.0
                sell_value = 0.0
                liq_float = float(liquid_value)
                
                # Logic: Futures keep Buy/Sell as 0 because it's not a gross trade.
                if not str(category).startswith('Futuros'):
                    if liq_float < 0:
                        buy_value = abs(liq_float)
                    else:
                        sell_value = abs(liq_float)

                self.records.append({
                    'Date': ref_date,
                    'Category': category,
                    'AssetClass': current_asset_class, # This is Ticker + Op for Stocks
                    'Ticker': current_asset_class.split(' - ')[0] if ' - ' in current_asset_class else current_asset_class,
                    'LiquidValue': liq_float,
                    'BuyValue': buy_value,
                    'SellValue': sell_value,
                    'Filename': filename
                })
                
            except AttributeError as e:
                print(f"Error accessing data in {filename}: {e}")

    def get_records(self):
        # Validation Step 1: Sorting
        sorted_records = sorted(self.records, key=lambda x: x['Date'])
        
        # Validation Step 2: Aggregation for "Fundos e Acoes"
        # We need to aggregate operations for the same Asset (Ticker) on the same Day.
        # This handles cases like: Buy 100 PETR4 (Morning) + Buy 100 PETR4 (Afternoon) in one day,
        # or distinct notes for the same day.
        
        aggregated_map = defaultdict(lambda: {
            'Date': None, 
            'Category': '', 
            'AssetClass': '', 
            'LiquidValue': 0.0, 
            'BuyValue': 0.0, 
            'SellValue': 0.0, 
            'Filename': set()
        })

        final_records = []

        for record in sorted_records:
            if str(record['Category']).startswith('Futuros'):
                # Futures: Keep separate, do not aggregate? 
                # User said "sometimes we have more operations for the same asset and I want an aggregate".
                # But for Futures, they usually come as one daily adjustment line per note. 
                # If there are multiple notes for same day? 
                # User instruction: "don't touch in futuros, it's good already."
                # So we pass them through directly.
                final_records.append(record)
            else:
                # Stocks/FIIs/ETFs: Aggregate by Date + Ticker
                key = (record['Date'], record['Ticker'])
                
                agg = aggregated_map[key]
                agg['Date'] = record['Date']
                agg['Ticker'] = record['Ticker']
                agg['Category'] = record['Category']
                # AssetClass might vary (e.g. PETR4 - C vs PETR4 - V). We'll reconstruct it.
                agg['LiquidValue'] += record['LiquidValue']
                agg['BuyValue'] += record['BuyValue']
                agg['SellValue'] += record['SellValue']
                agg['Filename'].add(record['Filename'])
        
        # Convert aggregated map back to list
        for key, agg in aggregated_map.items():
            # Reconstruction of AssetClass string based on net result or just Ticker?
            # User might want to see if it was a net Buy or Sell.
            # We can leave "AssetClass" as just the Ticker for the aggregated row, 
            # or Ticker - C/V based on net.
            
            ticker = agg['Ticker']
            net_val = agg['LiquidValue']
            op = "C" if net_val < 0 else "V"
            # If net is 0? Rare, but possible daytrade flat.
            
            final_asset_class = f"{ticker} - {op}"
            
            final_records.append({
                'Date': agg['Date'],
                'Category': agg['Category'],
                'AssetClass': final_asset_class,
                'LiquidValue': agg['LiquidValue'],
                'BuyValue': agg['BuyValue'],
                'SellValue': agg['SellValue'],
                'Filename': ", ".join(sorted(list(agg['Filename'])))
            })

        # Re-sort final
        return sorted(final_records, key=lambda x: x['Date'])

