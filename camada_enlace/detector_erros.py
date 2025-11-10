"""
Detectores de erro: Paridade, Checksum, CRC-32
Pessoa 3: Implementar estas classes
"""
from abc import ABC, abstractmethod
from config import Config

class DetectorErros(ABC):
    """Classe abstrata para detectores de erro"""

    @abstractmethod
    def adicionar(self, dados: list) -> list:
        """Adiciona bits/bytes de verificação"""
        pass

    @abstractmethod
    def verificar(self, dados_com_verificacao: list) -> tuple:
        """Retorna (dados_originais, tem_erro: bool)"""
        pass


class DetectorParidade(DetectorErros):
    """Detector de paridade par"""

    def adicionar(self, dados: list) -> list:
        """
        TODO Pessoa 3: Implementar
        Adiciona bit de paridade a cada byte
        """
        dados_com_paridade = []
        for byte in dados:
            bits = [int(b) for b in format(byte, '08b')]
            paridade = sum(bits) % 2
            dados_com_paridade.extend([byte, paridade])
        return dados_com_paridade

    def verificar(self, dados_com_paridade: list) -> tuple:
        """TODO Pessoa 3: Implementar verificação"""
        dados = []
        tem_erro = False
        for i in range(0, len(dados_com_paridade), 2):
            if i + 1 < len(dados_com_paridade):
                byte = dados_com_paridade[i]
                paridade_recebida = dados_com_paridade[i + 1]
                bits = [int(b) for b in format(byte, '08b')]
                paridade_calculada = sum(bits) % 2
                if paridade_recebida != paridade_calculada:
                    tem_erro = True
                dados.append(byte)
        return dados, tem_erro


class DetectorChecksum(DetectorErros):
    """Detector por checksum"""

    def adicionar(self, dados: list) -> list:
        """
        TODO Pessoa 3: Implementar
        Adiciona checksum ao final dos dados
        """
        if len(dados) == 0:
            return [0]
        soma = sum(dados) % 256
        checksum = (255 - soma) % 256
        return dados + [checksum]

    def verificar(self, dados_com_checksum: list) -> tuple:
        """TODO Pessoa 3: Implementar verificação"""
        if len(dados_com_checksum) < 1:
            return [], True
        dados = dados_com_checksum[:-1]
        checksum_recebido = dados_com_checksum[-1]
        soma = sum(dados) % 256
        checksum_calculado = (255 - soma) % 256
        tem_erro = (checksum_recebido != checksum_calculado)
        return dados, tem_erro


class DetectorCRC32(DetectorErros):
    """Detector CRC-32 (IEEE 802)"""

    def __init__(self):
        config = Config()
        self.polinomio = config.CRC32_POLYNOMIAL
        # Tabela CRC-32 simplificada (primeiros valores)
        self.tabela = [
            0x00000000, 0x77073096, 0xEE0E612C, 0x990951BA,
            0x076DC419, 0x706AF48F, 0xE963A535, 0x9E6495A3,
            0x0EDB8832, 0x79DCB8A4, 0xE0D5E91E, 0x97D2D988,
            0x09B64C2B, 0x7EB17CBD, 0xE7B82D07, 0x90BF1D91
        ]

    def calcular_crc(self, dados: list) -> int:
        """
        TODO Pessoa 3: Implementar cálculo CRC-32
        """
        crc = 0xFFFFFFFF
        for byte in dados:
            indice = (crc ^ byte) & 0xFF
            if indice < len(self.tabela):
                crc = (crc >> 8) ^ self.tabela[indice]
            else:
                crc = (crc >> 8) ^ (byte & 0xFF)
        return crc ^ 0xFFFFFFFF

    def adicionar(self, dados: list) -> list:
        """Adiciona CRC-32 (4 bytes) aos dados"""
        crc = self.calcular_crc(dados)
        crc_bytes = [
            (crc >> 24) & 0xFF,
            (crc >> 16) & 0xFF,
            (crc >> 8) & 0xFF,
            crc & 0xFF
        ]
        return dados + crc_bytes

    def verificar(self, dados_com_crc: list) -> tuple:
        """Verifica CRC-32"""
        if len(dados_com_crc) < 4:
            return [], True
        dados = dados_com_crc[:-4]
        crc_recebido_bytes = dados_com_crc[-4:]
        crc_recebido = (crc_recebido_bytes[0] << 24) | \
                       (crc_recebido_bytes[1] << 16) | \
                       (crc_recebido_bytes[2] << 8) | \
                       crc_recebido_bytes[3]
        crc_calculado = self.calcular_crc(dados)
        tem_erro = (crc_recebido != crc_calculado)
        return dados, tem_erro