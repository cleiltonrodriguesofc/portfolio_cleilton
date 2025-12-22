# Brokerage Analyzer (Investment Tool)

## 🏢 Business Problem & Solution
**The Problem:** Manually calculating taxes for Brazilian investments (Stocks, FIIs, Futures) from PDF brokerage notes is error-prone, tedious, and can take hours per month.
**The Solution:** This application automates the extraction of financial data from C6 Bank PDF notes. It parses the complex layout of brokerage notes to calculate precise daily and monthly totals, reducing tax preparation time by ~90% and ensuring accuracy for "Imposto de Renda" declarations.

## 🚀 Key Features
- **Smart PDF Parsing**: Extracts transaction details (asset name, quantity, price, taxes) using `pdfminer`.
- **Automatic Classification**: Distinguishes between Normal Trade and Day Trade operations.
- **Futures Support**: Specifically handles WIN/WDO futures calculations with separate logic for liquid values.
- **Excel Reporting**: Generates a detailed `.xlsx` report with aggregated monthly data, ready for accountant review.

## 🛠️ Tech Stack
- **Core**: Django 5.2.5
- **PDF Processing**: `pdfminer.six`
- **Data Manipulation**: `pandas` (for aggregation logic)
- **Excel Generation**: `openpyxl`
- **Infrastructure**: Clean Architecture principles separating parsing logic from Django views.

## 📋 How to Use
1.  Navigate to the **Brokerage Analyzer** section in the portfolio.
2.  Upload your C6 Bank brokerage note (PDF format).
3.  Wait for the processing to complete.
4.  Download the generated Excel report containing:
    -   Detailed transaction list.
    -   Monthly summaries by asset type (Stocks, FIIs, Futures).

