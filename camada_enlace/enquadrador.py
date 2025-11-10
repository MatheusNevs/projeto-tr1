"""
Protocolos de enquadramento
Pessoa 3: Implementar estas classes
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
    """Enquadramento por contagem de caracteres"""

    def enquadrar(self, dados: list) -> list:
        """
        TODO Pessoa 3: Implementar
        Formato: [tamanho][dados...]
        """
        tamanho = len(dados)
        return [tamanho] + dados

    def desenquadrar(self, quadro: list) -> list:
        """TODO Pessoa 3: Implementar desenquadramento"""
        if len(quadro) < 1:
            return []
        tamanho = quadro[0]
        return quadro[1:tamanho+1]


class EnquadradorFlagsBytes(Enquadrador):
    """Enquadramento com FLAGS e inserção de bytes"""

    def __init__(self):
        config = Config()
        self.flag = config.BYTE_FLAG
        self.esc = config.BYTE_ESC

    def enquadrar(self, dados: list) -> list:
        """
        TODO Pessoa 3: Implementar
        Formato: [FLAG][dados com escape][FLAG]
        Se dados contêm FLAG ou ESC, inserir ESC antes
        """
        quadro = [self.flag]
        for byte in dados:
            if byte == self.flag or byte == self.esc:
                quadro.append(self.esc)
            quadro.append(byte)
        quadro.append(self.flag)
        return quadro

    def desenquadrar(self, quadro: list) -> list:
        """TODO Pessoa 3: Implementar desenquadramento"""
        if len(quadro) < 2:
            return []
        dados = []
        i = 1  # Pula FLAG inicial
        while i < len(quadro) - 1:
            if quadro[i] == self.esc:
                i += 1
                if i < len(quadro) - 1:
                    dados.append(quadro[i])
            else:
                dados.append(quadro[i])
            i += 1
        return dados


class EnquadradorFlagsBits(Enquadrador):
    """Enquadramento com FLAGS e inserção de bits (bit stuffing)"""

    def __init__(self):
        self.flag = [0, 1, 1, 1, 1, 1, 1, 0]  # 01111110

    def enquadrar(self, bits: list) -> list:
        """
        TODO Pessoa 3: Implementar bit stuffing
        Se aparecem 5 uns consecutivos, inserir um 0
        """
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
        """TODO Pessoa 3: Implementar destuffing"""
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