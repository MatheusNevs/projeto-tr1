"""
Canal de comunicação com ruído gaussiano
"""
import numpy as np
from config import Config

class CanalComunicacao:
    """Simula canal de comunicação com ruído AWGN"""

    def __init__(self, nivel_ruido=None):
        config = Config()
        self.nivel_ruido = nivel_ruido or config.RUIDO_DESVIO
        self.ruido_media = config.RUIDO_MEDIA

    def transmitir(self, sinal: np.ndarray) -> np.ndarray:
        """
        Transmite sinal através do canal com ruído

        Args:
            sinal: Sinal de entrada

        Returns:
            Sinal com ruído gaussiano adicionado
        """
        ruido = np.random.normal(
            self.ruido_media, 
            self.nivel_ruido, 
            len(sinal)
        )
        return sinal + ruido

    def set_nivel_ruido(self, nivel: float):
        """Ajusta nível de ruído (desvio padrão)"""
        self.nivel_ruido = nivel
