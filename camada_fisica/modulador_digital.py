"""
Moduladores digitais: NRZ-Polar, Manchester, Bipolar
"""

from abc import ABC, abstractmethod
import numpy as np
from config import Config

class ModuladorDigital(ABC):
    """Classe abstrata para moduladores digitais"""

    def __init__(self, amplitude=None, taxa=None):
        config = Config()
        self.amplitude = amplitude or config.AMPLITUDE
        self.taxa_amostragem = taxa or config.TAXA_AMOSTRAGEM
        self.amostras_por_bit = self.taxa_amostragem // 10  # 100 amostras por bit

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
                # Repete amplitude positiva por todas as amostras do bit
                sinal.extend([self.amplitude] * self.amostras_por_bit)
            else:
                # Repete amplitude negativa por todas as amostras do bit
                sinal.extend([-self.amplitude] * self.amostras_por_bit)
        return np.array(sinal)

    def decodificar(self, sinal: np.ndarray) -> list:
        bits = []
        # Agrupa amostras por bit e decide baseado na média
        for i in range(0, len(sinal), self.amostras_por_bit):
            segmento = sinal[i:i + self.amostras_por_bit]
            media = np.mean(segmento)
            bits.append(1 if media > 0 else 0)
        return bits


class Manchester(ModuladorDigital):
    """Modulação Manchester: transição no meio do bit"""

    def codificar(self, bits: list) -> np.ndarray:
        sinal = []
        metade = self.amostras_por_bit // 2
        
        for bit in bits:
            if bit == 1:
                # Bit 1: primeira metade negativa, segunda metade positiva
                sinal.extend([-self.amplitude] * metade)
                sinal.extend([self.amplitude] * metade)
            else:
                # Bit 0: primeira metade positiva, segunda metade negativa
                sinal.extend([self.amplitude] * metade)
                sinal.extend([-self.amplitude] * metade)
        return np.array(sinal)

    def decodificar(self, sinal: np.ndarray) -> list:
        bits = []
        metade = self.amostras_por_bit // 2
        
        # Agrupa amostras por bit
        for i in range(0, len(sinal), self.amostras_por_bit):
            primeira_metade = sinal[i:i + metade]
            segunda_metade = sinal[i + metade:i + self.amostras_por_bit]
            
            if len(primeira_metade) > 0 and len(segunda_metade) > 0:
                media1 = np.mean(primeira_metade)
                media2 = np.mean(segunda_metade)
                
                # Bit 1: primeira negativa, segunda positiva
                if media1 < 0 and media2 > 0:
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
                # Bit 0: amplitude zero por todas as amostras
                sinal.extend([0] * self.amostras_por_bit)
            else:
                # Bit 1: alterna entre +V e -V
                sinal.extend([ultimo_valor] * self.amostras_por_bit)
                ultimo_valor = -ultimo_valor
        return np.array(sinal)

    def decodificar(self, sinal: np.ndarray) -> list:
        bits = []
        # Agrupa amostras por bit e decide baseado na média do valor absoluto
        # Limiar em metade da amplitude para robustez contra ruído
        limiar = self.amplitude / 2.0  # 2.5V para amplitude de 5V
        
        for i in range(0, len(sinal), self.amostras_por_bit):
            segmento = sinal[i:i + self.amostras_por_bit]
            media_abs = np.mean(np.abs(segmento))
            # Se média absoluta é próxima de zero, é bit 0, caso contrário é bit 1
            bits.append(0 if media_abs < limiar else 1)
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
