import os
from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from .forms import UploadNotesForm
from .models import Transaction
from brokerage_analyzer.src.use_cases.data_aggregator import DataAggregator

from django.http import HttpResponse
from brokerage_analyzer.src.infrastructure.excel_exporter import ExcelExporter
from io import BytesIO

from django.db.models import Sum


def dashboard(request):
    # Statistics
    total_transactions = Transaction.objects.count()
    total_liquid = Transaction.objects.aggregate(Sum('liquid_value'))['liquid_value__sum'] or 0

    # Aggregation by Category
    category_stats = Transaction.objects.values('category').annotate(total=Sum('liquid_value')).order_by('category')

    # Recent Transactions
    transactions = Transaction.objects.all().order_by('-date')[:50]

    context = {
        'total_transactions': total_transactions,
        'total_liquid': total_liquid,
        'category_stats': category_stats,
        'transactions': transactions,
        'form': UploadNotesForm()  # For the modal/upload section
    }
    return render(request, 'brokerage_analyzer/dashboard.html', context)


def upload_notes(request):
    if request.method == 'POST':
        # print(f"DEBUG: FILES keys: {request.FILES.keys()}")
        form = UploadNotesForm(request.POST, request.FILES)
        if form.is_valid():
            asset_type = form.cleaned_data['asset_type']
            uploaded_files = request.FILES.getlist('files')

            # 1. Setup Temporary Directory
            temp_dir = os.path.join(settings.BASE_DIR, 'media', 'temp')
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)

            # 2. Process Files
            aggregator = DataAggregator()
            count = 0

            for f in uploaded_files:
                # Save to disk temporarily
                fs = FileSystemStorage(location=temp_dir)
                filename = fs.save(f.name, f)
                file_path = os.path.join(temp_dir, filename)

                try:
                    # Parse the file
                    aggregator.process_single_pdf(file_path, asset_type)

                except Exception as e:
                    messages.error(request, f"Error processing {f.name}: {e}")
                finally:
                    # Delete file immediately
                    if os.path.exists(file_path):
                        os.remove(file_path)

            # 3. Save to Database
            # Retrieve aggregated records
            # get_records() aggregates by Day/Ticker
            final_records = aggregator.get_records()

            objs = []
            for r in final_records:
                # Map dictionary to Model
                t = Transaction(
                    date=r['Date'],
                    category=r['Category'],
                    asset_class=r['AssetClass'],
                    ticker=r.get('Ticker', r['AssetClass'].split(' - ')[0]),
                    liquid_value=r['LiquidValue'],
                    buy_value=r['BuyValue'],
                    sell_value=r['SellValue'],
                    filename=r['Filename']
                )
                objs.append(t)

            Transaction.objects.bulk_create(objs)
            count = len(objs)

            messages.success(request, f"{count} records imported successfully!")

            # Cleanup temp dir if empty
            try:
                os.rmdir(temp_dir)
            except BaseException:
                pass

            return redirect('dashboard')
    else:
        form = UploadNotesForm()

    return render(request, 'brokerage_analyzer/upload.html', {'form': form})


def download_report(request):
    # 1. Fetch Data
    transactions = Transaction.objects.all().order_by('date')

    if not transactions.exists():
        messages.warning(request, "No data available to generate report.")
        return redirect('dashboard')

    # 2. Format for ExcelExporter
    # Exporter expects: {'Date', 'Category', 'AssetClass', 'Ticker', 'LiquidValue', 'BuyValue', 'SellValue', 'Filename'}
    records = []
    for t in transactions:
        records.append({
            'Date': t.date,
            'Category': t.category,
            'AssetClass': t.asset_class,
            'Ticker': t.ticker,
            'LiquidValue': float(t.liquid_value),
            'BuyValue': float(t.buy_value),
            'SellValue': float(t.sell_value),
            'Filename': t.filename
        })

    # 3. Generate Excel in Memory
    exporter = ExcelExporter(records)

    # Use BytesIO buffer to capture the file content
    buffer = BytesIO()

    try:
        exporter.to_excel(buffer)
    except Exception as e:
        print(f"Export Error: {e}")
        messages.error(request, "Error generating Excel report.")
        return redirect('dashboard')

    buffer.seek(0)

    # 4. Return Response
    response = HttpResponse(
        buffer.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="Relatorio_Notas_Corretagem.xlsx"'
    return response
