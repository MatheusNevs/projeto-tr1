"""
Configurações globais do simulador TR1
"""

class Config:
    """Singleton para configurações globais"""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._inicializar()
        return cls._instance

    def _inicializar(self):
        # Camada Física
        self.TAXA_AMOSTRAGEM = 1000  # Hz
        self.FREQUENCIA_PORTADORA = 100  # Hz
        self.AMPLITUDE = 5.0  # Volts

        # Camada de Enlace
        self.TAMANHO_MAX_QUADRO = 256  # bytes
        self.BYTE_FLAG = 0x7E  # 01111110
        self.BYTE_ESC = 0x7D   # 01111101

        # Canal
        self.RUIDO_MEDIA = 0.0
        self.RUIDO_DESVIO = 0.5

        # CRC
        self.CRC32_POLYNOMIAL = 0x04C11DB7
