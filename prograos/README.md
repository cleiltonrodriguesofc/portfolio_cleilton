# ProGrãos (Grain Management System)

## 🏢 Business Problem & Solution
**The Problem:** Grain weighting and sampling in warehouses is often a manual process involving paper tickets and manual data entry, which leads to high risks of data inconsistency and potential fraud during the weighing process.
**The Solution:** ProGrãos integrates directly with the weighing scales via serial port to capture real-time weight data. It enforces a strict digital workflow for grain reception, sampling, and classification, ensuring 100% data integrity and traceability.

## 🚀 Key Features
- **Serial Port Integration**: Automatically reads weight from digital scales (mocked for demo/web environment) using `pyserial`.
- **Digital Weight Ticket**: Generates tamper-proof digital tickets for every weighing operation.
- **Quality Control**: Manages sampling results (humidity, impurities) associated with each load.
- **Inventory Management**: Real-time tracking of warehouse stock levels.

## 🛠️ Tech Stack
- **Backend**: Django 5.2.5
- **Hardware Integration**: `pyserial` (for RS-232 communication)
- **Frontend**: Bootstrap 5, JavaScript (for real-time scale polling)
- **Database**: SQLite (Dev) / PostgreSQL (Prod)

## 📋 How to Use
1.  Access the **ProGrãos** system from the project list.
2.  **Weighing**: On the dashboard, select "Nova Pesagem". The system will auto-read the scale value (simulated in this web demo).
3.  **Classification**: Enter the sample data (humidity, grains quality).
4.  **Reports**: View the "Relatórios" section for daily reception summaries.

