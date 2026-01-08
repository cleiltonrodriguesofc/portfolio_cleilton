import datetime
from endesive.pdf import cms
from ..certificate import CertificateManager


class PDFSigner:
    """
    Helper class to sign PDFs using an A1 Certificate.
    """

    @staticmethod
    def sign_pdf(pdf_bytes, certificate_config, y_position=None):
        """
        Signs a PDF file (bytes) using the provided CertificateConfig.

        Args:
            pdf_bytes (bytes): The raw content of the PDF to be signed.
            certificate_config (CertificateConfig): The configuration object for the A1 certificate.

        Returns:
            bytes: The signed PDF content.
        """
        # 1. Load Certificate and Key using CertificateManager
        manager = CertificateManager(certificate_config)

        # This returns cryptography objects
        private_key, certificate, ca_certs = manager.load_certificate()

        # 2. Prepare metadata for the signature
        # Brazilian time (UTC-3)
        tz = datetime.timezone(datetime.timedelta(hours=-3))
        date = datetime.datetime.now(tz)

        # Get Common Name (CN) for the label
        try:
            from cryptography import x509
            cn = certificate.subject.get_attributes_for_oid(x509.NameOID.COMMON_NAME)[0].value
        except Exception:
            cn = certificate.subject.rfc4514_string()

        # Dimensions for manual layout calculations
        if y_position is not None:
            # Captured Y is usually the baseline.
            # The signature box should start at this Y and go up?
            # Or start slightly below?
            # PositionReporter was placed BEFORE the line. So Y is the top of the line space.
            # The box should be placed AT that Y (bottom) up to Y+50.
            box_y = int(y_position)
        else:
            box_y = 110  # Default fallback

        box_x = 270
        box_w, box_h = 300, 50  # w=570-270, height reduced slightly

        # Custom text matching the user's example
        # Right side text
        right_text = f"Assinado de forma digital por\n{cn}\nDados: {date.strftime('%Y.%m.%d %H:%M:%S')} -03'00'"

        # Manual signature commands to replicate the "Adobe-style" split view
        # Commands: [cmd, arg1, arg2, ...]
        manual_cmds = [
            # Left Side: CN in larger font
            ['font', 'default', 10],
            ['text_box', cn, 'default', 0, 0, box_w * 0.45, box_h, 10, True, 'left', 'middle', 1.1],

            # Right Side: Details in smaller font
            ['font', 'default', 6],
            ['text_box', right_text, 'default', box_w * 0.48, 0, box_w * 0.52, box_h, 6, True, 'left', 'middle', 1.3],
        ]

        # Signature details
        dct = {
            'aligned': 0,
            'sigflags': 3,
            'sigflagsft': 132,
            'sigpage': 0,
            'sigbutton': True,
            'sigfield': 'Signature1',
            'auto_sigfield': True,
            'sigandcertify': True,  # Certify the document
            'signingdate': date.strftime("D:%Y%m%d%H%M%S-03'00'"),
            'signature_manual': manual_cmds,
            'signaturebox': (box_x, box_y, box_x + box_w, box_y + box_h),  # (270, 95, 570, 155)
        }

        # 3. Sign the PDF
        try:
            # endesive.pdf.cms.sign returns the incremental update (delta)
            # We must append it to the original PDF bytes
            datau = cms.sign(pdf_bytes, dct, private_key, certificate, [], 'sha256')
            return pdf_bytes + datau
        except Exception as e:
            # Log the error and re-raise so the caller knows signing failed
            # The caller (reports.py) catches this and serves the unsigned PDF
            raise ValueError(f"Endesive signing failed: {str(e)}")
