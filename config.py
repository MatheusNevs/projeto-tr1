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
        self.TAXA_BITS = 10  # bits por segundo
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

    def set_tamanho_max_quadro(self, tamanho: int):
        """Atualiza o tamanho máximo do quadro (em bytes)"""
        if tamanho < 64:
            raise ValueError("Tamanho mínimo do quadro é 64 bytes")
        if tamanho > 1024:
            raise ValueError("Tamanho máximo do quadro é 1024 bytes")
        self.TAMANHO_MAX_QUADRO = tamanho

    def set_taxa_amostragem(self, taxa: int):
        """Atualiza a taxa de amostragem (em Hz)"""
        if taxa < 100:
            raise ValueError("Taxa de amostragem mínima é 100 Hz")
        if taxa > 10000:
            raise ValueError("Taxa de amostragem máxima é 10000 Hz")
        self.TAXA_AMOSTRAGEM = taxa

    def set_taxa_bits(self, taxa: int):
        """Atualiza a taxa de bits (bits por segundo)"""
        if taxa < 1:
            raise ValueError("Taxa de bits mínima é 1 bps")
        if taxa > 1000:
            raise ValueError("Taxa de bits máxima é 1000 bps")
        self.TAXA_BITS = taxa

    def set_frequencia_portadora(self, frequencia: int):
        """Atualiza a frequência da portadora (em Hz)"""
        if frequencia < 10:
            raise ValueError("Frequência mínima da portadora é 10 Hz")
        if frequencia > 1000:
            raise ValueError("Frequência máxima da portadora é 1000 Hz")
        self.FREQUENCIA_PORTADORA = frequencia
