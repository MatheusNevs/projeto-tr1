"""
Moduladores por portadora: ASK, FSK, QPSK, 16-QAM
Pessoa 2: Implementar estas classes
"""
from abc import ABC, abstractmethod
import numpy as np
from config import Config

class ModuladorPortadora(ABC):
    """Classe abstrata para moduladores por portadora"""

    def __init__(self, amplitude=None, frequencia=None, taxa=None):
        config = Config()
        self.amplitude = amplitude or config.AMPLITUDE
        self.frequencia = frequencia or config.FREQUENCIA_PORTADORA
        self.taxa_amostragem = taxa or config.TAXA_AMOSTRAGEM

    @abstractmethod
    def codificar(self, bits: list) -> np.ndarray:
        """Codifica bits em sinal modulado"""
        pass

    @abstractmethod
    def decodificar(self, sinal: np.ndarray) -> list:
        """Decodifica sinal modulado em bits"""
        pass


class ASK(ModuladorPortadora):
    """Amplitude Shift Keying"""

    def codificar(self, bits: list) -> np.ndarray:
        """
        TODO Pessoa 2: Implementar ASK
        Bit 1 → portadora com amplitude A
        Bit 0 → sem sinal (amplitude 0)
        """
        pass

    def decodificar(self, sinal: np.ndarray) -> list:
        """TODO Pessoa 2: Implementar decodificação ASK"""
        pass


class FSK(ModuladorPortadora):
    """Frequency Shift Keying"""

    def codificar(self, bits: list) -> np.ndarray:
        """
        TODO Pessoa 2: Implementar FSK
        Bit 1 → frequência alta
        Bit 0 → frequência baixa
        """
        pass

    def decodificar(self, sinal: np.ndarray) -> list:
        """TODO Pessoa 2: Implementar decodificação FSK"""
        pass


class QPSK(ModuladorPortadora):
    """Quadrature Phase Shift Keying"""

    def codificar(self, bits: list) -> np.ndarray:
        """
        TODO Pessoa 2: Implementar QPSK
        Cada par de bits → uma fase específica
        """
        pass

    def decodificar(self, sinal: np.ndarray) -> list:
        """TODO Pessoa 2: Implementar decodificação QPSK"""
        pass


class QAM16(ModuladorPortadora):
    """16-QAM: Modulação de amplitude e fase"""

    def codificar(self, bits: list) -> np.ndarray:
        """
        TODO Pessoa 2: Implementar 16-QAM
        Cada 4 bits → uma combinação de amplitude e fase
        """
        pass

    def decodificar(self, sinal: np.ndarray) -> list:
        """TODO Pessoa 2: Implementar decodificação 16-QAM"""
        pass