"""
Certificate Manager for A1 Digital Certificates
Handles loading, validation, and providing certificates for NF-e signing
"""
from datetime import datetime
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.serialization import pkcs12
import logging

logger = logging.getLogger(__name__)


class CertificateManager:
    """
    Manages A1 digital certificates for NF-e signing
    """

    def __init__(self, certificate_config):
        """
        Initialize with a CertificateConfig model instance

        Args:
            certificate_config: CertificateConfig model instance
        """
        self.config = certificate_config
        self._private_key = None
        self._certificate = None
        self._loaded = False

    def load_certificate(self):
        """
        Load the A1 certificate from file

        Returns:
            tuple: (private_key, certificate, ca_certificates)

        Raises:
            ValueError: If certificate file is invalid or password is incorrect
            FileNotFoundError: If certificate file doesn't exist
        """
        if self._loaded:
            return self._private_key, self._certificate, []

        cert_path = self.config.certificate_file.path
        password = self.config.password.encode('utf-8')

        try:
            # Read the .pfx file
            with open(cert_path, 'rb') as f:
                pfx_data = f.read()

            # Load the certificate
            private_key, certificate, ca_certs = pkcs12.load_key_and_certificates(
                pfx_data,
                password,
                backend=default_backend()
            )

            self._private_key = private_key
            self._certificate = certificate
            self._loaded = True

            logger.info(f"Certificate loaded successfully: {self.config.name}")
            return private_key, certificate, ca_certs or []

        except Exception as e:
            logger.error(f"Failed to load certificate: {str(e)}")
            raise ValueError(f"Erro ao carregar certificado: {str(e)}")

    def validate_certificate(self):
        """
        Validate certificate expiration and activation dates

        Returns:
            tuple: (is_valid, error_message)
        """
        try:
            _, cert, _ = self.load_certificate()

            # Check if certificate is within validity period
            now = datetime.utcnow()
            not_before = cert.not_valid_before
            not_after = cert.not_valid_after

            if now < not_before:
                return False, f"Certificado ainda não está válido. Válido a partir de: {not_before}"

            if now > not_after:
                return False, f"Certificado expirado em: {not_after}"

            # Check if close to expiration (30 days)
            days_until_expiry = (not_after - now).days
            if days_until_expiry < 30:
                logger.warning(f"Certificate expires in {days_until_expiry} days")

            return True, None

        except Exception as e:
            return False, str(e)

    def get_certificate_info(self):
        """
        Get certificate information

        Returns:
            dict: Certificate details
        """
        try:
            _, cert, _ = self.load_certificate()

            subject = cert.subject
            issuer = cert.issuer

            return {
                'subject_cn': subject.get_attributes_for_oid(x509.NameOID.COMMON_NAME)[0].value,
                'issuer_cn': issuer.get_attributes_for_oid(x509.NameOID.COMMON_NAME)[0].value,
                'valid_from': cert.not_valid_before,
                'valid_to': cert.not_valid_after,
                'serial_number': cert.serial_number,
            }
        except Exception as e:
            logger.error(f"Failed to get certificate info: {str(e)}")
            return {}

    def get_cert_pem(self):
        """
        Get certificate in PEM format for signing

        Returns:
            bytes: Certificate in PEM format
        """
        from cryptography.hazmat.primitives import serialization

        _, cert, _ = self.load_certificate()
        return cert.public_bytes(serialization.Encoding.PEM)

    def get_key_pem(self):
        """
        Get private key in PEM format for signing

        Returns:
            bytes: Private key in PEM format
        """
        from cryptography.hazmat.primitives import serialization

        key, _, _ = self.load_certificate()
        return key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        )
