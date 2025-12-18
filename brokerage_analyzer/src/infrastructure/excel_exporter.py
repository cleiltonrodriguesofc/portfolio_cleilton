
import pandas as pd
from typing import List, Dict

class ExcelExporter:
    def __init__(self, records: List[Dict]):
        self.records = records

    def to_excel(self, file_path: str):
        if not self.records:
            print("No data to export.")
            return

        df = pd.DataFrame(self.records)
        df['Date'] = pd.to_datetime(df['Date'])
        
        # 1. Detailed Report
        # Ensure we have all columns
        cols = ['Date', 'Category', 'AssetClass', 'LiquidValue', 'BuyValue', 'SellValue', 'Filename']
        for c in cols:
            if c not in df.columns:
                df[c] = None

        # 2. Monthly Summary Preparation
        df['Year'] = df['Date'].dt.year
        df['Month'] = df['Date'].dt.month
        
        # Formatting Helpers
        currency_format = 'R$ #,##0.00'
        
        def apply_format(worksheet, col_idx, format_str):
            for row in worksheet.iter_rows(min_row=2, max_col=col_idx, min_col=col_idx):
                for cell in row:
                    cell.number_format = format_str

        # Write to Excel
        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            
            # --- SEPARATE SHEETS PER CATEGORY ---
            categories = sorted(df['Category'].unique())
            
            # Helper to apply currency format
            # Order: Stocks, FIIs, ETFs, Futures, Others
            
            for cat in categories:
                # Sanitize sheet name
                sheet_name = str(cat).replace('/', '-').replace('\\', '-')[:30]
                
                # Filter for this category
                cat_df = df[df['Category'] == cat].copy()
                
                if str(cat).startswith('Futuros') or str(cat).startswith('Futures'):
                    # Futures logic: Display simpler columns
                    display_cols = ['Date', 'AssetClass', 'LiquidValue', 'Filename']
                    cat_df = cat_df[display_cols]
                    cat_df.to_excel(writer, index=False, sheet_name=sheet_name)
                    
                    ws = writer.sheets[sheet_name]
                    apply_format(ws, 3, currency_format) # Column 3 = LiquidValue
                    
                    ws.column_dimensions['A'].width = 15
                    ws.column_dimensions['B'].width = 25
                    ws.column_dimensions['C'].width = 18
                    ws.column_dimensions['D'].width = 30
                    
                else:
                    # Stocks/FIIs/ETFs
                    display_cols = ['Date', 'AssetClass', 'BuyValue', 'SellValue', 'LiquidValue', 'Filename']
                    cat_df = cat_df[display_cols]
                    
                    cat_df.to_excel(writer, index=False, sheet_name=sheet_name)
                    
                    # Format this sheet
                    ws = writer.sheets[sheet_name]
                    # Cols: A=Date, B=Asset, C=Buy, D=Sell, E=Liquid, F=File
                    apply_format(ws, 3, currency_format) # BuyValue  (C)
                    apply_format(ws, 4, currency_format) # SellValue (D)
                    apply_format(ws, 5, currency_format) # LiquidValue (E)
                    
                    # Resize
                    ws.column_dimensions['A'].width = 15
                    ws.column_dimensions['B'].width = 25
                    ws.column_dimensions['C'].width = 15
                    ws.column_dimensions['D'].width = 15
                    ws.column_dimensions['E'].width = 15
                    ws.column_dimensions['F'].width = 30


            # --- SUMMARY SHEET (TAX) ---
            # Exclude Futures for typical Taxable Assets summary
            
            tax_df = df[~df['Category'].str.startswith('Futuros', na=False) & ~df['Category'].str.startswith('Futures', na=False)].copy()
            
            if not tax_df.empty:
                # Aggregate by Year, Month, Category
                tax_summary = tax_df.groupby(['Year', 'Month', 'Category'])[['BuyValue', 'SellValue', 'LiquidValue']].sum().reset_index()
                
                # Add explicit columns for Tax Report context:
                # 1. Total Sold (Sales)
                # 2. Total Bought (Purchases)
                # 3. Net Result (Cash Flow)
                
                tax_summary.rename(columns={'SellValue': 'Total Vendas', 'BuyValue': 'Total Compras', 'LiquidValue': 'Resultado Líquido'}, inplace=True)
                
                sheet_name_tax = 'Resumo IR'
                tax_summary.to_excel(writer, index=False, sheet_name=sheet_name_tax)
                
                ws_tax = writer.sheets[sheet_name_tax]
                # Columns: Year, Month, Category, Total Compras, Total Vendas, Resultado Líquido
                
                apply_format(ws_tax, 4, currency_format) # Compras
                apply_format(ws_tax, 5, currency_format) # Vendas
                apply_format(ws_tax, 6, currency_format) # Resultado
                
                ws_tax.column_dimensions['C'].width = 20
                ws_tax.column_dimensions['D'].width = 18
                ws_tax.column_dimensions['E'].width = 18
                ws_tax.column_dimensions['F'].width = 18
            
            # --- SUMMARY SHEET (FUTURES) ---
            fut_df = df[df['Category'].str.startswith('Futuros', na=False) | df['Category'].str.startswith('Futures', na=False)].copy()
            if not fut_df.empty:
                fut_summary = fut_df.groupby(['Category', 'Year', 'Month'])['LiquidValue'].sum().reset_index()
                fut_summary.sort_values(by=['Category', 'Year', 'Month'], inplace=True)
                
                sheet_name_fut = 'Resumo Futuros'
                fut_summary.to_excel(writer, index=False, sheet_name=sheet_name_fut)
                
                ws_fut = writer.sheets[sheet_name_fut]
                apply_format(ws_fut, 4, currency_format) # LiquidValue (D)
                ws_fut.column_dimensions['A'].width = 25
                ws_fut.column_dimensions['D'].width = 18

        print(f"Data exported to {file_path}")
