"""
Moduladores digitais: NRZ-Polar, Manchester, Bipolar
Pessoa 1: Implementar estas classes
"""
from abc import ABC, abstractmethod
import numpy as np
from config import Config

class ModuladorDigital(ABC):
    """Classe abstrata para moduladores digitais"""

    def __init__(self, amplitude=None):
        config = Config()
        self.amplitude = amplitude or config.AMPLITUDE

    @abstractmethod
    def codificar(self, bits: list) -> np.ndarray:
        """Codifica bits em sinal"""
        pass

    @abstractmethod
    def decodificar(self, sinal: np.ndarray) -> list:
        """Decodifica sinal em bits"""
        pass


class NRZPolar(ModuladorDigital):
    """Modulação NRZ-Polar: 1→+V, 0→-V"""

    def codificar(self, bits: list) -> np.ndarray:
        """
        TODO Pessoa 1: Implementar codificação NRZ-Polar
        Regra: bit 1 → +amplitude, bit 0 → -amplitude
        """
        sinal = []
        for bit in bits:
            if bit == 1:
                sinal.append(self.amplitude)
            else:
                sinal.append(-self.amplitude)
        return np.array(sinal)

    def decodificar(self, sinal: np.ndarray) -> list:
        """
        TODO Pessoa 1: Implementar decodificação NRZ-Polar
        Regra: valor > 0 → bit 1, valor <= 0 → bit 0
        """
        bits = []
        for valor in sinal:
            bits.append(1 if valor > 0 else 0)
        return bits


class Manchester(ModuladorDigital):
    """Modulação Manchester: transição no meio do bit"""

    def codificar(self, bits: list) -> np.ndarray:
        """
        TODO Pessoa 1: Implementar codificação Manchester
        Regra: bit 1 → (-V, +V), bit 0 → (+V, -V)
        """
        sinal = []
        for bit in bits:
            if bit == 1:
                sinal.extend([-self.amplitude, self.amplitude])
            else:
                sinal.extend([self.amplitude, -self.amplitude])
        return np.array(sinal)

    def decodificar(self, sinal: np.ndarray) -> list:
        """
        TODO Pessoa 1: Implementar decodificação Manchester
        """
        bits = []
        for i in range(0, len(sinal), 2):
            if i + 1 < len(sinal):
                if sinal[i] < 0 and sinal[i+1] > 0:
                    bits.append(1)
                else:
                    bits.append(0)
        return bits


class Bipolar(ModuladorDigital):
    """Modulação Bipolar (AMI): 0→0V, 1→alterna +V/-V"""

    def codificar(self, bits: list) -> np.ndarray:
        """
        TODO Pessoa 1: Implementar codificação Bipolar
        Regra: bit 0 → 0V, bit 1 → alterna entre +V e -V
        """
        sinal = []
        ultimo_valor = self.amplitude
        for bit in bits:
            if bit == 0:
                sinal.append(0)
            else:
                sinal.append(ultimo_valor)
                ultimo_valor = -ultimo_valor
        return np.array(sinal)

    def decodificar(self, sinal: np.ndarray) -> list:
        """
        TODO Pessoa 1: Implementar decodificação Bipolar
        """
        bits = []
        for valor in sinal:
            bits.append(0 if valor == 0 else 1)
        return bits