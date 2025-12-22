import io
import pandas as pd
from datetime import datetime
from django.http import HttpResponse
from reportlab.lib import colors
from reportlab.lib.units import inch
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import Amostra


# ReportLab Imports
from reportlab.lib.pagesizes import landscape, A4

from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import mm
from reportlab.platypus.flowables import Flowable

# --- New Custom Class for Rounded Boxes ---


class RoundedBox(Flowable):
    """A custom Flowable that draws a box with rounded corners around a table."""

    def __init__(self, content_table, padding=5, radius=3 * mm):
        Flowable.__init__(self)
        self.table = content_table
        self.padding = padding
        self.radius = radius

        # Calculate width and height based on the table
        self.width = max(col for col in self.table._colWidths) + 2 * self.padding
        self.height = self.table._height + 2 * self.padding

    def draw(self):
        self.canv.saveState()
        # Draw the rounded rectangle
        self.canv.setFillColor(colors.white)  # Box background color
        self.canv.setStrokeColor(colors.grey)  # Border color
        self.canv.roundRect(0, 0, self.width, self.height, self.radius, stroke=1, fill=1)
        self.canv.restoreState()

        # Draw the table inside the box
        self.table.wrapOn(self.canv, self.width - 2 * self.padding, self.height)
        self.table.drawOn(self.canv, self.padding, self.padding)


class ReportGenerator:
    """
    Class for generating PDF and Excel reports.
    """

    @staticmethod
    def generate_amostras_pdf(queryset, title="Relatório de Amostras"):
        """
        Generates PDF report of samples.

        Args:
            queryset: QuerySet of samples
            title: Report title

        Returns:
            HttpResponse: HTTP response with the PDF
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        elements = []

        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=1  # Centered
        )

        # Title
        elements.append(Paragraph(title, title_style))
        elements.append(Spacer(1, 12))

        # Generation date
        data_geracao = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        elements.append(Paragraph(f"Generated at: {data_geracao}", styles['Normal']))
        elements.append(Spacer(1, 20))

        # Table data
        data = [['ID Amostra',
                 'Tipo Grão',
                 'Peso Bruto (kg)',
                 'Umidade (%)',
                 'Impurezas (%)',
                 'Peso Útil (kg)',
                 'Status',
                 'Data Criação']]

        for amostra in queryset:
            data.append([
                amostra.id_amostra or f"#{amostra.id}",
                amostra.get_tipo_grao_display(),
                str(amostra.peso_bruto),
                str(amostra.umidade) if amostra.umidade else '-',
                str(amostra.impurezas) if amostra.impurezas else '-',
                str(amostra.peso_util) if amostra.peso_util else '-',
                amostra.status,
                amostra.data_criacao.strftime("%d/%m/%Y %H:%M")
            ])

        # Create table
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))

        elements.append(table)

        # Statistics
        elements.append(Spacer(1, 20))
        total_amostras = queryset.count()
        aceitas = queryset.filter(status='ACEITA').count()
        rejeitadas = queryset.filter(status='REJEITADA').count()
        pendentes = queryset.filter(status='PENDENTE').count()

        stats_text = f"""
        <b>Estatísticas:</b><br/>
        Total de amostras: {total_amostras}<br/>
        Aceitas: {aceitas}<br/>
        Rejeitadas: {rejeitadas}<br/>
        Pendentes: {pendentes}
        """
        elements.append(Paragraph(stats_text, styles['Normal']))

        doc.build(elements)
        buffer.seek(0)

        response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = (
            f'attachment; filename="relatorio_amostras_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf"'
        )

        return response

    @staticmethod
    def generate_amostras_excel(queryset, title="Relatório de Amostras"):
        """
        Generates Excel report of samples.

        Args:
            queryset: QuerySet of samples
            title: Report title

        Returns:
            HttpResponse: HTTP response with the Excel
        """
        # Prepare data
        data = []
        for amostra in queryset:
            data.append({
                'ID Amostra': amostra.id_amostra or f"#{amostra.id}",
                'Tipo Grão': amostra.get_tipo_grao_display(),
                'Peso Bruto (kg)': float(amostra.peso_bruto),
                'Umidade (%)': float(amostra.umidade) if amostra.umidade else None,
                'Impurezas (%)': float(amostra.impurezas) if amostra.impurezas else None,
                'Peso Útil (kg)': float(amostra.peso_util) if amostra.peso_util else None,
                'Status': amostra.status,
                'Data Criação': amostra.data_criacao.replace(tzinfo=None) if amostra.data_criacao else None,
                'Criado Por': amostra.created_by.username if amostra.created_by else '-',
                'Última Atualização': amostra.ultima_atualizacao.replace(tzinfo=None) if amostra.ultima_atualizacao else None,
                'Atualizado Por': amostra.last_updated_by.username if amostra.last_updated_by else '-'
            })

        df = pd.DataFrame(data)

        # Create Excel file
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Samples', index=False)

            # Add statistics in a second sheet
            stats_data = {
                'Métrica': ['Total de Amostras', 'Aceitas', 'Rejeitadas', 'Pendentes'],
                'Valor': [
                    queryset.count(),
                    queryset.filter(status='ACEITA').count(),
                    queryset.filter(status='REJEITADA').count(),
                    queryset.filter(status='PENDENTE').count()
                ]
            }
            stats_df = pd.DataFrame(stats_data)
            stats_df.to_excel(writer, sheet_name='Estatísticas', index=False)

        buffer.seek(0)

        response = HttpResponse(
            buffer.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="relatorio_amostras_{
            datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx"'

        return response

    @staticmethod
    def generate_nota_pdf(nota):
        """
        Generates the Loading Order PDF for a single note.

        Args:
            nota: An instance of the NotaCarregamento model

        Returns:
            HttpResponse: HTTP response with the PDF
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5 * inch, bottomMargin=0.5 * inch)
        elements = []

        # Styles
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='RightAlign', alignment=2))
        styles.add(ParagraphStyle(name='BoldText', fontName='Helvetica-Bold'))

        # --- DATA (to fill fields) ---
        # Supplier Data (Embarkation) - Add your company data here
        fornecedor_data = {
            "nome": "NOME DA SUA EMPRESA",
            "endereco": "ENDEREÇO DA SUA EMPRESA",
            "municipio_uf": "SUA CIDADE/UF",
            "cpf_cnpj": "SEU CPF/CNPJ",
            "responsavel": nota.created_by.get_full_name() or nota.created_by.username
        }

        # --- FUNCTION TO CREATE A COPY OF THE NOTE ---
        def create_nota_copy():
            # Main Title
            title = Paragraph(
                "ORDEM DE CARREGAMENTO",
                ParagraphStyle(
                    'CustomTitle',
                    parent=styles['h1'],
                    alignment=1,
                    spaceAfter=10))
            via = Paragraph("Via: Motorista", styles['RightAlign'])

            # Table 1: Embarkation and Discharge (2 columns)
            header_data = [
                [Paragraph("<b>Embarque</b>", styles['Normal']), Paragraph("<b>Descarga</b>", styles['Normal'])]
            ]
            header_table = Table(header_data, colWidths=['50%', '50%'])
            header_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))

            # Nested table for Embarkation data
            embarque_details = [
                [Paragraph(f"<b>Fornecedor:</b> {fornecedor_data['nome']}", styles['Normal'])],
                [Paragraph(f"<b>Endereço:</b> {fornecedor_data['endereco']}", styles['Normal'])],
                [Paragraph(f"<b>Município/UF:</b> {fornecedor_data['municipio_uf']}", styles['Normal'])],
                [Paragraph(f"<b>CPF:</b> {fornecedor_data['cpf_cnpj']}", styles['Normal'])],
                [Paragraph(f"<b>Responsável:</b> {fornecedor_data['responsavel']}", styles['Normal'])],
            ]
            embarque_table = Table(embarque_details, colWidths='100%')
            embarque_table.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP')]))

            # Nested table for Discharge data
            descarga_details = [
                [Paragraph(f"<b>Fone:</b> {nota.telefone_recebedor or ''}", styles['Normal'])],
                [Paragraph("<b>CV:</b>", styles['Normal'])],
                [Paragraph("<b>CC:</b>", styles['Normal'])],
            ]
            descarga_table = Table(descarga_details, colWidths='100%')

            # Assembly of the main Embarkation/Discharge table
            main_details_data = [[embarque_table, descarga_table]]
            main_details_table = Table(main_details_data, colWidths=['50%', '50%'])
            main_details_table.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))

            # Table 2: Driver and Plate
            motorista_data = [[
                Paragraph("<b>Motorista:</b>", styles['Normal']),
                Paragraph(f"<b>Placa - Cavalo:</b> {nota.pesagem.placa if nota.pesagem else ''}", styles['Normal'])
            ]]
            motorista_table = Table(motorista_data, colWidths=['50%', '50%'])
            motorista_table.setStyle(TableStyle([('GRID', (0, 0), (-1, -1), 1, colors.black)]))

            # Table 3: Billing Data
            faturamento_data = [
                [Paragraph("<b>Dados Faturamento</b>", styles['Normal'])],
                [Paragraph(f"<b>Comprador:</b> {nota.nome_recebedor}", styles['Normal'])],
                [
                    Paragraph(f"<b>CPF/CNPJ:</b> {nota.cpf_cnpj_recebedor or ''}", styles['Normal']),
                    Paragraph("<b>Insc. Est.:</b>", styles['Normal'])
                ],
                [Paragraph(f"<b>Endereço:</b> {nota.endereco_recebedor or ''}", styles['Normal'])],
            ]
            faturamento_table = Table(faturamento_data, colWidths='100%')
            faturamento_table.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('BACKGROUND', (0, 0), (0, 0), colors.lightgrey),
                ('SPAN', (0, 0), (-1, 0)),  # Span title
                ('SPAN', (0, 1), (-1, 1)),  # Span buyer
                ('SPAN', (0, 3), (-1, 3)),  # Span address
                ('ALIGN', (0, 0), (0, 0), 'CENTER'),
            ]))

            # Table 4: Final Information
            final_data = [[
                Paragraph(f"<b>Produto:</b> {nota.get_tipo_grao_display()}", styles['Normal']),
                Paragraph(f"<b>Data:</b> {nota.data_criacao.strftime('%d/%m/%Y %H:%M')}", styles['Normal'])
            ], [
                Paragraph(f"<b>Balança total:</b> {nota.pesagem.peso_carregado if nota.pesagem else ''} kg", styles['Normal']),
                Paragraph(f"<b>Balança tara:</b> {nota.pesagem.tara if nota.pesagem else ''} kg", styles['Normal'])
            ], [
                Paragraph("<b>ANTT:</b>", styles['Normal']),
                Paragraph("<b>Obs:</b>", styles['Normal'])
            ]]
            final_table = Table(final_data, colWidths=['50%', '50%'])
            final_table.setStyle(TableStyle([('GRID', (0, 0), (-1, -1), 1, colors.black)]))

            return [
                title, via, header_table, main_details_table, Spacer(
                    1, 5), motorista_table, Spacer(
                    1, 5), faturamento_table, Spacer(
                    1, 5), final_table]

        # Add two note copies to PDF
        elements.extend(create_nota_copy())
        elements.append(Spacer(1, 20))  # Space between copies
        elements.extend(create_nota_copy())

        doc.build(elements)
        buffer.seek(0)

        response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="nota_carregamento_{nota.id}.pdf"'

        return response

    @staticmethod
    def generate_pesagem_ticket_pdf(pesagem):
        """
        Generates a Ticket de Pesagem in PDF, in LANDSCAPE mode, matching the desired layout.
        """
        buffer = io.BytesIO()

        # Use a landscape page size. A6 is a good size for a small ticket.
        A6_landscape = landscape(A4)[1], landscape(A4)[0]  # A6 is 1/4 of A4
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A6_landscape,
            leftMargin=8 * mm,
            rightMargin=8 * mm,
            topMargin=8 * mm,
            bottomMargin=5 * mm)

        elements = []
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='Header', fontSize=12, fontName='Helvetica-Bold'))
        styles.add(ParagraphStyle(name='Address', fontSize=9, leading=11))
        styles.add(
            ParagraphStyle(
                name='TicketTitle',
                fontSize=10,
                fontName='Helvetica-Bold',
                alignment=1,
                spaceAfter=4 * mm))
        styles.add(ParagraphStyle(name='FieldLabel', fontSize=9, fontName='Helvetica-Bold'))
        styles.add(ParagraphStyle(name='FieldValue', fontSize=9))
        styles.add(ParagraphStyle(name='BoxTitle', fontSize=9, fontName='Helvetica-Bold', spaceAfter=2 * mm))
        styles.add(ParagraphStyle(name='NetWeightLabel', fontSize=10, alignment=1))
        styles.add(ParagraphStyle(name='NetWeightValue', fontSize=14, fontName='Helvetica-Bold', alignment=1))

        # --- Header Section (Logo and Company Info) ---
        header_data = [[Paragraph("2 IRMÃOS", styles['Header']), Paragraph(
            "Auto Posto dois Irmãos Ltda<br/>Rodovia BR 222 S/N km 170 Buriticupu<br/>Fone: (98) 3664-0662", styles['Address'])]]
        header_table = Table(header_data, colWidths=['30%', '70%'])
        header_table.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP')]))

        # --- Left Column Content (Vehicle Info) ---
        vehicle_info_data = [
            [
                Paragraph(
                    "Carreta", styles['FieldLabel']), Paragraph(
                    pesagem.placa, styles['FieldValue'])], [
                Paragraph(
                    "Transportadora:", styles['FieldLabel']), ''], [
                Paragraph(
                    "Emissor:", styles['FieldLabel']), ''], [
                Paragraph(
                    "Produto:", styles['FieldLabel']), Paragraph(
                    pesagem.get_tipo_grao_display(), styles['FieldValue'])], ]
        vehicle_info_table = Table(vehicle_info_data, colWidths=['30%', '70%'])
        vehicle_info_table.setStyle(TableStyle([
            ('GRID', (1, 0), (1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3 * mm)
        ]))

        observation_data = [[Paragraph("Observação:", styles['FieldLabel'])]]
        observation_table = Table(observation_data)
        observation_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 15 * mm)  # Creates a large empty box
        ]))

        left_column_content = [vehicle_info_table, Spacer(1, 4 * mm), observation_table]

        # --- Right Column Content (Weight Info) ---
        pesagem_inicial_data = [
            [Paragraph("Pesagem Inicial", styles['BoxTitle'])],
            [Paragraph("Data/Hora:", styles['FieldValue'])],
            [Paragraph(f"Peso: {pesagem.tara or ''} kg", styles['FieldValue'])],
            [Paragraph("Operador:", styles['FieldValue'])]
        ]
        pesagem_inicial_table = Table(pesagem_inicial_data)
        pesagem_inicial_table.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('LEFTPADDING', (0, 0), (-1, -1), 2 * mm),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 1.5 * mm)
        ]))

        pesagem_final_data = [
            [Paragraph("Pesagem Final", styles['BoxTitle'])],
            [Paragraph(f"Data / Hora: {pesagem.data_criacao.strftime('%d/%m/%Y %H:%M')}", styles['FieldValue'])],
            [Paragraph(f"Peso: {pesagem.peso_carregado} kg", styles['FieldValue'])],
            [Paragraph(f"Operador: {pesagem.created_by.username}", styles['FieldValue'])]
        ]
        pesagem_final_table = Table(pesagem_final_data)
        pesagem_final_table.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('LEFTPADDING', (0, 0), (-1, -1), 2 * mm),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 1.5 * mm)
        ]))

        net_weight_data = [
            [Paragraph("Peso Líquido", styles['NetWeightLabel'])],
            [Paragraph(f"{pesagem.peso_liquido} kg", styles['NetWeightValue'])]
        ]
        net_weight_table = Table(net_weight_data)
        net_weight_table.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 1.5, colors.black),
            ('LEFTPADDING', (0, 0), (-1, -1), 2 * mm),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2 * mm)
        ]))

        right_column_content = [
            pesagem_inicial_table,
            Spacer(
                1,
                3 * mm),
            pesagem_final_table,
            Spacer(
                1,
                5 * mm),
            net_weight_table]

        # --- Assemble Final Layout ---
        main_layout_data = [
            # Row 1: Header spans both columns
            [header_table, ''],
            # Row 2: Title spans both columns
            [Paragraph(f"TICKET DE PESAGEM 0000{pesagem.id}", styles['TicketTitle']), ''],
            # Row 3: Left and Right content columns
            [left_column_content, right_column_content]
        ]
        final_table = Table(main_layout_data, colWidths=['55%', '45%'])
        final_table.setStyle(TableStyle([
            ('SPAN', (0, 0), (1, 0)),  # Span header
            ('SPAN', (0, 1), (1, 1)),  # Span title
            ('VALIGN', (0, 2), (-1, -1), 'TOP'),
        ]))

        elements.append(final_table)
        doc.build(elements)
        buffer.seek(0)

        response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="ticket_pesagem_{pesagem.id}.pdf"'

        return response


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_amostras_pdf(request):
    """
    Exports sample report to PDF.

    Query Parameters:
    - tipo_grao: SOJA or MILHO
    - status: ACEITA, REJEITADA, PENDENTE
    - data_inicio: YYYY-MM-DD
    - data_fim: YYYY-MM-DD
    """
    queryset = Amostra.objects.all()

    # Apply filters
    tipo_grao = request.GET.get('tipo_grao')
    if tipo_grao:
        queryset = queryset.filter(tipo_grao=tipo_grao)

    status_filter = request.GET.get('status')
    if status_filter:
        queryset = queryset.filter(status=status_filter)

    data_inicio = request.GET.get('data_inicio')
    if data_inicio:
        queryset = queryset.filter(data_criacao__date__gte=data_inicio)

    data_fim = request.GET.get('data_fim')
    if data_fim:
        queryset = queryset.filter(data_criacao__date__lte=data_fim)

    return ReportGenerator.generate_amostras_pdf(queryset)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_amostras_excel(request):
    """
    Exports sample report to Excel.

    Query Parameters:
    - tipo_grao: SOJA or MILHO
    - status: ACEITA, REJEITADA, PENDENTE
    - data_inicio: YYYY-MM-DD
    - data_fim: YYYY-MM-DD
    """
    queryset = Amostra.objects.all()

    # Apply filters
    tipo_grao = request.GET.get('tipo_grao')
    if tipo_grao:
        queryset = queryset.filter(tipo_grao=tipo_grao)

    status_filter = request.GET.get('status')
    if status_filter:
        queryset = queryset.filter(status=status_filter)

    data_inicio = request.GET.get('data_inicio')
    if data_inicio:
        queryset = queryset.filter(data_criacao__date__gte=data_inicio)

    data_fim = request.GET.get('data_fim')
    if data_fim:
        queryset = queryset.filter(data_criacao__date__lte=data_fim)

    return ReportGenerator.generate_amostras_excel(queryset)
