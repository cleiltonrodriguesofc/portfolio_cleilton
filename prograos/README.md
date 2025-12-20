# ProGrãos (Grain Management System)

## Overview
ProGrãos is a system designed for the agro-industry to manage grain weighting and sampling in warehouses. It ensures data integrity and reduces fraud risks by integrating directly with weighing scales.

## Features
- **Scale Integration**: Captures real-time weight data via serial port.
- **Sample Management**: Tracks grain samples and quality metrics.
- **Reporting**: Generates reports for grain reception and inventory.

## Key Components
- `scale_integration.py`: Handles communication with weighing scales.
- `models.py`: Stores weight tickets, sample data, and transaction logs.
- `views.py`: Manages the web interface for operators.
