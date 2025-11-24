"""
Moduladores digitais: NRZ-Polar, Manchester, Bipolar
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
        sinal = []
        for bit in bits:
            if bit == 1:
                sinal.append(self.amplitude)
            else:
                sinal.append(-self.amplitude)
        return np.array(sinal)

    def decodificar(self, sinal: np.ndarray) -> list:
        bits = []
        for valor in sinal:
            bits.append(1 if valor > 0 else 0)
        return bits


class Manchester(ModuladorDigital):
    """Modulação Manchester: transição no meio do bit"""

    def codificar(self, bits: list) -> np.ndarray:
        sinal = []
        for bit in bits:
            if bit == 1:
                sinal.extend([-self.amplitude, self.amplitude])
            else:
                sinal.extend([self.amplitude, -self.amplitude])
        return np.array(sinal)

    def decodificar(self, sinal: np.ndarray) -> list:
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
        bits = []
        for valor in sinal:
            bits.append(0 if valor == 0 else 1)
        return bits

# ==============================================================
# TESTES DE MODULAÇÃO DIGITAL
# ==============================================================

if __name__ == "__main__":
    print("="*70)
    print("TESTANDO MODULAÇÕES DIGITAIS - PESSOA 1")
    print("="*70)

    # Bits de teste
    bits_teste = [1, 0, 1, 1, 0, 0, 1, 0]
    print(f"\nBits originais: {bits_teste}")

    # Teste NRZ-Polar
    print("\n--- NRZ-Polar ---")
    nrz = NRZPolar()
    sinal_nrz = nrz.codificar(bits_teste)
    print(f"Sinal: {sinal_nrz}")
    bits_nrz = nrz.decodificar(sinal_nrz)
    print(f"Bits recuperados: {bits_nrz}")
    print(f"✓ Correto!" if bits_nrz == bits_teste else "✗ ERRO!")

    # Teste Manchester
    print("\n--- Manchester ---")
    manch = Manchester()
    sinal_manch = manch.codificar(bits_teste)
    print(f"Sinal (tamanho {len(sinal_manch)}): {sinal_manch[:16]}...")
    bits_manch = manch.decodificar(sinal_manch)
    print(f"Bits recuperados: {bits_manch}")
    print(f"✓ Correto!" if bits_manch == bits_teste else "✗ ERRO!")

    # Teste Bipolar
    print("\n--- Bipolar ---")
    bip = Bipolar()
    sinal_bip = bip.codificar(bits_teste)
    print(f"Sinal: {sinal_bip}")
    bits_bip = bip.decodificar(sinal_bip)
    print(f"Bits recuperados: {bits_bip}")
    print(f"✓ Correto!" if bits_bip == bits_teste else "✗ ERRO!")

    print("\n" + "="*70)
