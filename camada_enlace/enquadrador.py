"""
Protocolos de enquadramento
"""

from abc import ABC, abstractmethod
from config import Config

class Enquadrador(ABC):
    """Classe abstrata para enquadradores"""

    @abstractmethod
    def enquadrar(self, dados: list) -> list:
        """Adiciona delimitadores aos dados"""
        pass

    @abstractmethod
    def desenquadrar(self, quadro: list) -> list:
        """Remove delimitadores e retorna dados"""
        pass


class EnquadradorContagem(Enquadrador):
    """Enquadramento por contagem"""

    def enquadrar(self, bits: list) -> list:
        """Adiciona tamanho (16 bits) no início"""
        tamanho = len(bits)
        # Tamanho em 16 bits (permite até 65535 bits)
        tamanho_bits = [int(b) for b in format(tamanho, '016b')]
        return tamanho_bits + bits

    def desenquadrar(self, quadro: list) -> list:
        """Remove tamanho do início"""
        if len(quadro) < 16:
            return []
        tamanho_bits = quadro[:16]
        tamanho = int(''.join(map(str, tamanho_bits)), 2)
        return quadro[16:16+tamanho]


class EnquadradorFlagsBits(Enquadrador):
    """Enquadramento com FLAGS e inserção de bits (bit stuffing)"""

    def __init__(self):
        self.flag = [0, 1, 1, 1, 1, 1, 1, 0]  # 01111110

    def enquadrar(self, bits: list) -> list:
        quadro = self.flag.copy()
        contador_uns = 0
        for bit in bits:
            quadro.append(bit)
            if bit == 1:
                contador_uns += 1
                if contador_uns == 5:
                    quadro.append(0)
                    contador_uns = 0
            else:
                contador_uns = 0
        quadro.extend(self.flag)
        return quadro

    def desenquadrar(self, quadro: list) -> list:
        tam_flag = len(self.flag)
        if len(quadro) <= 2 * tam_flag:
            return []
        bits = quadro[tam_flag:-tam_flag]
        dados = []
        contador_uns = 0
        i = 0
        while i < len(bits):
            bit = bits[i]
            dados.append(bit)
            if bit == 1:
                contador_uns += 1
                if contador_uns == 5:
                    i += 1  # Pula o 0 inserido
                    contador_uns = 0
            else:
                contador_uns = 0
            i += 1
        return dados


