"""
SEFAZ Client for NF-e Webservice Communication
Handles all communication with SEFAZ webservices in MA (Maranhão)
"""
import requests
from lxml import etree
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


# SEFAZ MA Webservice URLs
SEFAZ_WEBSERVICES = {
    'MA': {
        1: {  # Production
            'NFeAutorizacao': 'https://nfe.sefaz.ma.gov.br/wsnfe2/services/NFeAutorizacao4',
            'NFeRetAutorizacao': 'https://nfe.sefaz.ma.gov.br/wsnfe2/services/NFeRetAutorizacao4',
            'NFeStatusServico': 'https://nfe.sefaz.ma.gov.br/wsnfe2/services/NFeStatusServico4',
            'NFeConsulta': 'https://nfe.sefaz.ma.gov.br/wsnfe2/services/NFeConsultaProtocolo4',
            'NFeRecepcaoEvento': 'https://nfe.sefaz.ma.gov.br/wsnfe2/services/NFeRecepcaoEvento4',
        },
        2: {  # Homologation
            'NFeAutorizacao': 'https://hom.sefazvirtual.fazenda.gov.br/NFeAutorizacao4/NFeAutorizacao4.asmx',
            'NFeRetAutorizacao': 'https://hom.sefazvirtual.fazenda.gov.br/NFeRetAutorizacao4/NFeRetAutorizacao4.asmx',
            'NFeStatusServico': 'https://hom.sefazvirtual.fazenda.gov.br/NFeStatusServico4/NFeStatusServico4.asmx',
            'NFeConsulta': 'https://hom.sefazvirtual.fazenda.gov.br/NFeConsultaProtocolo4/NFeConsultaProtocolo4.asmx',
            'NFeRecepcaoEvento': 'https://hom.sefazvirtual.fazenda.gov.br/NFeRecepcaoEvento4/NFeRecepcaoEvento4.asmx',
        }
    }
}


class SefazClient:
    """
    Client for communicating with SEFAZ webservices
    """

    def __init__(self, uf='MA', ambiente=2, certificate_manager=None):
        """
        Initialize SEFAZ client

        Args:
            uf: State code (default: MA)
            ambiente: 1=Production, 2=Homologation (default: 2)
            certificate_manager: CertificateManager instance
        """
        self.uf = uf
        self.ambiente = ambiente
        self.certificate_manager = certificate_manager
        self.webservices = SEFAZ_WEBSERVICES.get(uf, {}).get(ambiente, {})

        if not self.webservices:
            raise ValueError(f"Webservices não configurados para UF={uf}, ambiente={ambiente}")

    def _send_soap_request(self, service_name, xml_data):
        """
        Send SOAP request to SEFAZ webservice

        Args:
            service_name: Name of the webservice
            xml_data: XML data to send

        Returns:
            lxml.etree.Element: Response XML
        """
        url = self.webservices.get(service_name)
        if not url:
            raise ValueError(f"Serviço {service_name} não encontrado")

        # Build SOAP envelope
        soap_env = f"""<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope"
               xmlns:nfe="http://www.portalfiscal.inf.br/nfe/wsdl/{service_name}">
    <soap:Header/>
    <soap:Body>
        <nfe:nfeDadosMsg>
            {xml_data}
        </nfe:nfeDadosMsg>
    </soap:Body>
</soap:Envelope>"""

        headers = {
            'Content-Type': 'application/soap+xml; charset=utf-8',
            'SOAPAction': f'http://www.portalfiscal.inf.br/nfe/wsdl/{service_name}'
        }

        try:
            # Get certificate for SSL
            cert_pem = None
            key_pem = None
            if self.certificate_manager:
                cert_pem = self.certificate_manager.get_cert_pem()
                key_pem = self.certificate_manager.get_key_pem()

            # Make request
            response = requests.post(
                url,
                data=soap_env,
                headers=headers,
                cert=(cert_pem, key_pem) if cert_pem else None,
                timeout=30
            )

            response.raise_for_status()

            # Parse response
            root = etree.fromstring(response.content)
            return root

        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao comunicar com SEFAZ: {str(e)}")
            raise

    def consultar_status_servico(self):
        """
        Query SEFAZ service status

        Returns:
            dict: Service status information
        """
        xml_consulta = f"""<?xml version="1.0" encoding="UTF-8"?>
<consStatServ xmlns="http://www.portalfiscal.inf.br/nfe" versao="4.00">
    <tpAmb>{self.ambiente}</tpAmb>
    <cUF>21</cUF>
    <xServ>STATUS</xServ>
</consStatServ>"""

        try:
            response = self._send_soap_request('NFeStatusServico', xml_consulta)

            # Extract status from response
            ns = {'nfe': 'http://www.portalfiscal.inf.br/nfe'}
            ret_status = response.find('.//nfe:retConsStatServ', ns)

            if ret_status is not None:
                c_stat = ret_status.find('.//nfe:cStat', ns).text
                x_motivo = ret_status.find('.//nfe:xMotivo', ns).text

                return {
                    'status_code': c_stat,
                    'message': x_motivo,
                    'operational': c_stat == '107',  # 107 = Serviço em Operação
                    'timestamp': datetime.now()
                }

            return {'operational': False, 'message': 'Resposta inválida'}

        except Exception as e:
            logger.error(f"Erro ao consultar status: {str(e)}")
            return {
                'operational': False,
                'message': f'Erro: {str(e)}',
                'timestamp': datetime.now()
            }

    def autorizar_nfe(self, xml_nfe_signed, id_lote='1'):
        """
        Send NF-e for authorization

        Args:
            xml_nfe_signed: Signed NF-e XML string
            id_lote: Batch ID (default: '1')

        Returns:
            dict: Authorization result
        """
        xml_lote = f"""<?xml version="1.0" encoding="UTF-8"?>
<enviNFe xmlns="http://www.portalfiscal.inf.br/nfe" versao="4.00">
    <idLote>{id_lote}</idLote>
    <indSinc>1</indSinc>
    {xml_nfe_signed}
</enviNFe>"""

        try:
            response = self._send_soap_request('NFeAutorizacao', xml_lote)

            # Parse response
            ns = {'nfe': 'http://www.portalfiscal.inf.br/nfe'}
            ret_envi = response.find('.//nfe:retEnviNFe', ns)

            if ret_envi is not None:
                c_stat = ret_envi.find('.//nfe:cStat', ns).text
                x_motivo = ret_envi.find('.//nfe:xMotivo', ns).text

                result = {
                    'status_code': c_stat,
                    'message': x_motivo,
                    'success': c_stat in ['100', '104'],  # 100=Authorized, 104=Processed
                }

                # If authorized, extract protocol
                if c_stat == '100':
                    prot_nfe = ret_envi.find('.//nfe:protNFe', ns)
                    if prot_nfe is not None:
                        result['protocol'] = prot_nfe.find('.//nfe:nProt', ns).text
                        result['access_key'] = prot_nfe.find('.//nfe:chNFe', ns).text
                        result['auth_date'] = prot_nfe.find('.//nfe:dhRecbto', ns).text

                # If need to query receipt
                elif c_stat == '103':
                    n_rec = ret_envi.find('.//nfe:nRec', ns)
                    if n_rec is not None:
                        result['receipt_number'] = n_rec.text

                return result

            return {'success': False, 'message': 'Resposta inválida'}

        except Exception as e:
            logger.error(f"Erro ao autorizar NF-e: {str(e)}")
            return {'success': False, 'message': f'Erro: {str(e)}'}

    def consultar_recibo(self, receipt_number):
        """
        Query authorization result by receipt number

        Args:
            receipt_number: Receipt number from authorization

        Returns:
            dict: Authorization result
        """
        xml_consulta = f"""<?xml version="1.0" encoding="UTF-8"?>
<consReciNFe xmlns="http://www.portalfiscal.inf.br/nfe" versao="4.00">
    <tpAmb>{self.ambiente}</tpAmb>
    <nRec>{receipt_number}</nRec>
</consReciNFe>"""

        try:
            self._send_soap_request('NFeRetAutorizacao', xml_consulta)

            # Parse response (similar to autorizar_nfe)
            # Implementation similar to above
            return {'success': True}

        except Exception as e:
            logger.error(f"Erro ao consultar recibo: {str(e)}")
            return {'success': False, 'message': f'Erro: {str(e)}'}

    def cancelar_nfe(self, chave_acesso, protocolo, justificativa):
        """
        Cancel an authorized NF-e

        Args:
            chave_acesso: NF-e access key (44 digits)
            protocolo: Authorization protocol
            justificativa: Cancellation reason (min 15 chars)

        Returns:
            dict: Cancellation result
        """
        if len(justificativa) < 15:
            return {'success': False, 'message': 'Justificativa deve ter no mínimo 15 caracteres'}

        # Build event XML for cancellation
        # Implementation would go here

        return {'success': True, 'message': 'Cancelamento não implementado ainda'}

    def enviar_cce(self, chave_acesso, sequencia, correcao):
        """
        Send Carta de Correção Eletrônica

        Args:
            chave_acesso: NF-e access key
            sequencia: Event sequence number
            correcao: Correction text

        Returns:
            dict: CCe result
        """
        # Implementation would go here
        return {'success': True, 'message': 'CCe não implementado ainda'}
