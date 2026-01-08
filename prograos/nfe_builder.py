"""
NF-e XML Builder
Converts Invoice data to official NF-e 4.00 XML format
Optimized for Simples Nacional grain sales (primarily corn/milho)
"""
from lxml import etree
from datetime import datetime
from decimal import Decimal
from signxml import XMLSigner
import logging

logger = logging.getLogger(__name__)


class NFeBuilder:
    """
    Builds NF-e XML from Invoice model data
    """

    def __init__(self, emitter_config, certificate_manager):
        """
        Initialize builder with company and certificate config

        Args:
            emitter_config: EmitterConfig model instance
            certificate_ manager: CertificateManager instance
        """
        self.emitter = emitter_config
        self.cert_manager = certificate_manager

    def build_from_invoice(self, invoice):
        """
        Build complete NF-e XML from Invoice

        Args:
            invoice: Invoice model instance

        Returns:
            str: NF-e XML string
        """
        # Get next NF-e number
        nfe_number = self.emitter.get_next_nfe_number()
        serie = self.emitter.serie_nfe

        # Build XML structure
        nfe_root = self._build_nfe_structure(invoice, nfe_number, serie)

        # Generate access key
        access_key = self._generate_access_key(nfe_number, serie)

        # Add access key to XML
        ide = nfe_root.find('.//{http://www.portalfiscal.inf.br/nfe}ide')
        c_nf = etree.SubElement(ide, 'cNF')
        c_nf.text = access_key[-8:]  # Last 8 digits

        # Calculate and add check digit
        c_dv = etree.SubElement(ide, 'cDV')
        c_dv.text = self._calculate_check_digit(access_key[:-1])

        # Convert to string
        xml_string = etree.tostring(nfe_root, encoding='unicode', pretty_print=True)

        return xml_string, access_key, nfe_number

    def _build_nfe_structure(self, invoice, nfe_number, serie):
        """Build the main NF-e XML structure"""
        # Root element
        nfe = etree.Element(
            'NFe',
            xmlns='http://www.portalfiscal.inf.br/nfe'
        )

        inf_nfe = etree.SubElement(nfe, 'infNFe', versao='4.00')

        # ide - Identification
        ide = self._build_ide(invoice, nfe_number, serie)
        inf_nfe.append(ide)

        # emit - Emitter
        emit = self._build_emit()
        inf_nfe.append(emit)

        # dest - Customer
        dest = self._build_dest(invoice)
        inf_nfe.append(dest)

        # det - Items
        det = self._build_det(invoice)
        inf_nfe.append(det)

        # total - Totals
        total = self._build_total(invoice)
        inf_nfe.append(total)

        # transp - Transport
        trans = self._build_transp(invoice)
        inf_nfe.append(trans)

        # infAdic - Additional info
        inf_adic = self._build_inf_adic(invoice)
        if inf_adic is not None:
            inf_nfe.append(inf_adic)

        return nfe

    def _build_ide(self, invoice, nfe_number, serie):
        """Build ide (identification) section"""
        ide = etree.Element('ide')

        # UF code for MA = 21
        self._add_element(ide, 'cUF', '21')

        # Nature of operation
        self._add_element(ide, 'natOp', 'Venda de Mercadoria')

        # Model = 55 (NF-e)
        self._add_element(ide, 'mod', '55')

        # Serie
        self._add_element(ide, 'serie', str(serie))

        # Number
        self._add_element(ide, 'nNF', str(nfe_number))

        # Emission date/time
        dh_emi = invoice.issue_date.strftime('%Y-%m-%dT%H:%M:%S-03:00')
        self._add_element(ide, 'dhEmi', dh_emi)

        # Exit date/time (same as emission for simplicity)
        self._add_element(ide, 'dhSaiEnt', dh_emi)

        # Operation type: 1=Exit
        self._add_element(ide, 'tpNF', '1')

        # Destination: 1=Inside state, 2=Outside state, 3=Exterior
        dest_uf = '1'  # Default to inside state for now
        self._add_element(ide, 'idDest', dest_uf)

        # Municipality code
        self._add_element(ide, 'cMunFG', self.emitter.c_mun)

        # Print format: 1=Portrait DANFE
        self._add_element(ide, 'tpImp', '1')

        # Emission type: 1=Normal
        self._add_element(ide, 'tpEmis', '1')

        # Environment
        self._add_element(ide, 'tpAmb', str(self.emitter.ambiente))

        # Purpose: 1=Normal NF-e
        self._add_element(ide, 'finNFe', '1')

        # Consumer: 0=Normal, 1=Final consumer
        self._add_element(ide, 'indFinal', '1')

        # Presence: 1=Face-to-face operation
        self._add_element(ide, 'indPres', '1')

        # Process: 0=Own application
        self._add_element(ide, 'procEmi', '0')

        # Application version
        self._add_element(ide, 'verProc', 'ProGraos_1.0')

        return ide

    def _build_emit(self):
        """Build emit (emitter) section"""
        emit = etree.Element('emit')

        self._add_element(emit, 'CNPJ', self.emitter.cnpj)
        self._add_element(emit, 'xNome', self.emitter.razao_social)

        if self.emitter.nome_fantasia:
            self._add_element(emit, 'xFant', self.emitter.nome_fantasia)

        # Address
        ender_emit = etree.SubElement(emit, 'enderEmit')
        self._add_element(ender_emit, 'xLgr', self.emitter.logradouro)
        self._add_element(ender_emit, 'nro', self.emitter.numero)
        if self.emitter.complemento:
            self._add_element(ender_emit, 'xCpl', self.emitter.complemento)
        self._add_element(ender_emit, 'xBairro', self.emitter.bairro)
        self._add_element(ender_emit, 'cMun', self.emitter.c_mun)
        self._add_element(ender_emit, 'xMun', self.emitter.municipio)
        self._add_element(ender_emit, 'UF', self.emitter.uf)
        self._add_element(ender_emit, 'CEP', self.emitter.cep)
        self._add_element(ender_emit, 'cPais', '1058')  # Brazil
        self._add_element(ender_emit, 'xPais', 'BRASIL')

        self._add_element(emit, 'IE', self.emitter.ie)
        self._add_element(emit, 'CRT', self.emitter.regime_tributario)

        return emit

    def _build_dest(self, invoice):
        """Build dest (customer) section"""
        dest = etree.Element('dest')

        # Customer document (CNPJ or CPF)
        doc = invoice.customer_document.replace('.', '').replace('-', '').replace('/', '')
        if len(doc) == 14:
            self._add_element(dest, 'CNPJ', doc)
        else:
            self._add_element(dest, 'CPF', doc)

        self._add_element(dest, 'xNome', invoice.customer_name)

        # For simplicity, minimal address (can be expanded)
        ender_dest = etree.SubElement(dest, 'enderDest')
        self._add_element(ender_dest, 'xLgr', 'Endereço não informado')
        self._add_element(ender_dest, 'nro', 'S/N')
        self._add_element(ender_dest, 'xBairro', 'Centro')
        self._add_element(ender_dest, 'cMun', self.emitter.c_mun)
        self._add_element(ender_dest, 'xMun', self.emitter.municipio)
        self._add_element(ender_dest, 'UF', self.emitter.uf)
        self._add_element(ender_dest, 'CEP', self.emitter.cep)
        self._add_element(ender_dest, 'cPais', '1058')
        self._add_element(ender_dest, 'xPais', 'BRASIL')

        # Consumer indicator
        self._add_element(dest, 'indIEDest', '9')  # Non-contributor

        return dest

    def _build_det(self, invoice):
        """Build det (item) section - simplified for grain"""
        from prograos.models import TaxProfile

        det = etree.Element('det', nItem='1')

        # Get tax profile for grain type
        weighing = invoice.weighing_record
        grain_type = weighing.tipo_grao if weighing else 'MILHO'

        try:
            tax_profile = TaxProfile.objects.get(grain_type=grain_type)
        except TaxProfile.DoesNotExist:
            # Default to Milho if not found
            tax_profile = TaxProfile.objects.filter(grain_type='MILHO').first()

        # Product
        prod = etree.SubElement(det, 'prod')
        self._add_element(prod, 'cProd', '001')  # Internal code
        self._add_element(prod, 'cEAN', 'SEM GTIN')
        self._add_element(prod, 'xProd', tax_profile.description)
        self._add_element(prod, 'NCM', tax_profile.ncm)
        self._add_element(prod, 'CFOP', tax_profile.cfop_inside_state)
        self._add_element(prod, 'uCom', tax_profile.unit_com)

        # Quantity from weighing
        quantity = weighing.peso_liquido if weighing else Decimal('1000.00')
        self._add_element(prod, 'qCom', f'{quantity:.4f}')

        # Unit price
        unit_price = invoice.total_amount / quantity
        self._add_element(prod, 'vUnCom', f'{unit_price:.4f}')

        # Total
        self._add_element(prod, 'vProd', f'{invoice.total_amount:.2f}')

        self._add_element(prod, 'cEANTrib', 'SEM GTIN')
        self._add_element(prod, 'uTrib', tax_profile.unit_com)
        self._add_element(prod, 'qTrib', f'{quantity:.4f}')
        self._add_element(prod, 'vUnTrib', f'{unit_price:.4f}')

        # Tax: ICMS for Simples Nacional
        imposto = etree.SubElement(det, 'imposto')
        icms = etree.SubElement(imposto, 'ICMS')
        icmssn101 = etree.SubElement(icms, 'ICMSSN101')
        self._add_element(icmssn101, 'orig', '0')  # National origin
        self._add_element(icmssn101, 'CSOSN', tax_profile.cst_csosn)
        self._add_element(icmssn101, 'pCredSN', '0.00')  # Credit percentage
        self._add_element(icmssn101, 'vCredICMSSN', '0.00')

        # PIS/COFINS (exempt for Simples)
        pis = etree.SubElement(imposto, 'PIS')
        pis_nt = etree.SubElement(pis, 'PISNT')
        self._add_element(pis_nt, 'CST', '99')

        cofins = etree.SubElement(imposto, 'COFINS')
        cofins_nt = etree.SubElement(cofins, 'COFINSNT')
        self._add_element(cofins_nt, 'CST', '99')

        return det

    def _build_total(self, invoice):
        """Build total section"""
        total = etree.Element('total')

        icms_tot = etree.SubElement(total, 'ICMSTot')
        amount = invoice.total_amount

        self._add_element(icms_tot, 'vBC', '0.00')
        self._add_element(icms_tot, 'vICMS', '0.00')
        self._add_element(icms_tot, 'vICMSDeson', '0.00')
        self._add_element(icms_tot, 'vFCP', '0.00')
        self._add_element(icms_tot, 'vBCST', '0.00')
        self._add_element(icms_tot, 'vST', '0.00')
        self._add_element(icms_tot, 'vFCPST', '0.00')
        self._add_element(icms_tot, 'vFCPSTRet', '0.00')
        self._add_element(icms_tot, 'vProd', f'{amount:.2f}')
        self._add_element(icms_tot, 'vFrete', '0.00')
        self._add_element(icms_tot, 'vSeg', '0.00')
        self._add_element(icms_tot, 'vDesc', '0.00')
        self._add_element(icms_tot, 'vII', '0.00')
        self._add_element(icms_tot, 'vIPI', '0.00')
        self._add_element(icms_tot, 'vIPIDevol', '0.00')
        self._add_element(icms_tot, 'vPIS', '0.00')
        self._add_element(icms_tot, 'vCOFINS', '0.00')
        self._add_element(icms_tot, 'vOutro', '0.00')
        self._add_element(icms_tot, 'vNF', f'{amount:.2f}')

        return total

    def _build_transp(self, invoice):
        """Build transport section"""
        transp = etree.Element('transp')

        # Transport mode: 9=No transport
        self._add_element(transp, 'modFrete', '9')

        return transp

    def _build_inf_adic(self, invoice):
        """Build additional info section"""
        inf_adic = etree.Element('infAdic')

        # Tax info required for Simples
        info_text = "Documento emitido por ME/EPP optante pelo Simples Nacional. "
        info_text += "Não gera direito a crédito fiscal de IPI. "

        if invoice.weighing_record:
            info_text += f"Peso líquido: {invoice.weighing_record.peso_liquido} kg."

        self._add_element(inf_adic, 'infCpl', info_text)

        return inf_adic

    def _add_element(self, parent, tag, text):
        """Helper to add element with text"""
        elem = etree.SubElement(parent, tag)
        elem.text = str(text) if text is not None else ''
        return elem

    def _generate_access_key(self, nfe_number, serie):
        """Generate 44-digit NF-e access key"""
        # cUF (2) + AAMM (4) + CNPJ (14) + mod (2) + serie (3) + nNF (9) + tpEmis (1) + cNF (8) + cDV (1)

        c_uf = '21'  # MA
        aa_mm = datetime.now().strftime('%y%m')
        cnpj = self.emitter.cnpj.zfill(14)
        mod = '55'
        serie_str = str(serie).zfill(3)
        n_nf = str(nfe_number).zfill(9)
        tp_emis = '1'

        # Generate random cNF (8 digits)
        import random
        c_nf = str(random.randint(10000000, 99999999))

        # Build key without check digit
        key_without_dv = c_uf + aa_mm + cnpj + mod + serie_str + n_nf + tp_emis + c_nf

        # Calculate check digit
        c_dv = self._calculate_check_digit(key_without_dv)

        return key_without_dv + c_dv

    def _calculate_check_digit(self, key):
        """Calculate module 11 check digit"""
        weights = [2, 3, 4, 5, 6, 7, 8, 9]
        sum_total = 0

        for i, digit in enumerate(reversed(key)):
            weight = weights[i % len(weights)]
            sum_total += int(digit) * weight

        remainder = sum_total % 11

        if remainder == 0 or remainder == 1:
            return '0'
        else:
            return str(11 - remainder)

    def sign_xml(self, xml_string):
        """Sign the NF-e XML with A1 certificate"""
        try:
            # Load certificate
            key_pem = self.cert_manager.get_key_pem()
            cert_pem = self.cert_manager.get_cert_pem()

            # Parse XML
            root = etree.fromstring(xml_string.encode('utf-8'))

            # Sign
            signer = XMLSigner(
                method=XMLSigner.Methods.enveloped,
                signature_algorithm='rsa-sha1',
                digest_algorithm='sha1'
            )

            signed_root = signer.sign(root, key=key_pem, cert=cert_pem)

            # Return signed XML as string
            return etree.tostring(signed_root, encoding='unicode', pretty_print=True)

        except Exception as e:
            logger.error(f"Erro ao assinar XML: {str(e)}")
            raise
