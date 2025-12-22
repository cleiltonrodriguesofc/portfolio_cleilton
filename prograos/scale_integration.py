import serial
import time
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status


class ScaleIntegration:
    """
    Class for digital scale integration via USB/Serial.
    """

    def __init__(self, port='/dev/ttyUSB0', baudrate=9600, timeout=5):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.connection = None

    def connect(self):
        """
        Establishes connection with the scale.

        Returns:
            bool: True if connected successfully, False otherwise
        """
        try:
            self.connection = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout
            )
            time.sleep(2)  # Wait for connection stability
            return True
        except Exception as e:
            print(f"Error connecting to scale: {e}")
            return False

    def disconnect(self):
        """
        Closes connection with the scale.
        """
        if self.connection and self.connection.is_open:
            self.connection.close()

    def read_weight(self):
        """
        Reads weight from the scale.

        Returns:
            float: Weight read from scale or None in case of error
        """
        if not self.connection or not self.connection.is_open:
            return None

        try:
            # Send command to request weight (may vary by scale model)
            self.connection.write(b'W\\r\\n')
            time.sleep(1)

            # Read response
            response = self.connection.readline().decode('utf-8').strip()

            # Process response (format may vary by model)
            # Example: "W 1.234 kg" -> extract 1.234
            if response:
                # Remove non-numeric characters except dot and comma
                weight_str = ''.join(c for c in response if c.isdigit() or c in '.,')
                weight_str = weight_str.replace(',', '.')

                if weight_str:
                    return float(weight_str)

            return None

        except Exception as e:
            print(f"Error reading weight from scale: {e}")
            return None

    def get_available_ports(self):
        """
        Lists available serial ports.

        Returns:
            list: List of available ports
        """
        try:
            import serial.tools.list_ports
            ports = serial.tools.list_ports.comports()
            return [port.device for port in ports]
        except Exception:
            # if pyserial is not installed, return common ports
            return ['/dev/ttyUSB0', '/dev/ttyUSB1', '/dev/ttyACM0', 'COM1', 'COM2', 'COM3']


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_scale_ports(request):
    """
    Lists available serial ports for scale connection.
    """
    scale = ScaleIntegration()
    ports = scale.get_available_ports()
    return Response({'available_ports': ports})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def read_scale_weight(request):
    """
    Reads weight from connected scale.

    Body:
    {
        "port": "/dev/ttyUSB0",  # optional, uses default if not provided
        "baudrate": 9600         # optional, uses default if not provided
    }
    """
    port = request.data.get('port', '/dev/ttyUSB0')
    baudrate = request.data.get('baudrate', 9600)

    scale = ScaleIntegration(port=port, baudrate=baudrate)

    if not scale.connect():
        return Response(
            {'error': f'Could not connect using port {port}'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        weight = scale.read_weight()

        if weight is not None:
            return Response({
                'weight': weight,
                'unit': 'kg',
                'port': port,
                'timestamp': time.time()
            })
        else:
            return Response(
                {'error': 'Could not read weight from scale'},
                status=status.HTTP_400_BAD_REQUEST
            )

    finally:
        scale.disconnect()


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def test_scale_connection(request):
    """
    Tests connection with the scale.

    Body:
    {
        "port": "/dev/ttyUSB0",  # optional
        "baudrate": 9600         # optional
    }
    """
    port = request.data.get('port', '/dev/ttyUSB0')
    baudrate = request.data.get('baudrate', 9600)

    scale = ScaleIntegration(port=port, baudrate=baudrate)

    if scale.connect():
        scale.disconnect()
        return Response({
            'success': True,
            'message': f'Connection established successfully on port {port}'
        })
    else:
        return Response({
            'success': False,
            'message': f'Failed to connect on port {port}'
        }, status=status.HTTP_400_BAD_REQUEST)
