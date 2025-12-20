# Brokerage Analyzer

## Overview
This application automates the extraction and analysis of financial data from brokerage notes (C6 Bank PDF notes). It is designed to simplify tax calculations for Brazilian investments (Stocks, FIIs, Futures).

## Features
- **PDF Parsing**: Extracts text data from PDF brokerage notes.
- **Data Aggregation**: Summarizes financial data for tax reporting.
- **Excel Export**: Generates compliance-ready Excel reports.

## Key Components
- `forms.py`: Handles upload forms for PDF files.
- `models.py`: Defines data structures for parsed financial data.
- `views.py`: Controls the flow of data from upload to report generation.
- `src/infrastructure/pdf_parser.py`: Core logic for parsing PDFs.
