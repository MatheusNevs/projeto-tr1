"""
Detectores de erro: Paridade, Checksum, CRC-32
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

    def adicionar(self, bits: list) -> list:
        """Adiciona 1 bit de paridade a cada 8 bits"""
        bits_com_paridade = []
        for i in range(0, len(bits), 8):
            bloco = bits[i:i+8]
            if len(bloco) == 8:
                paridade = sum(bloco) % 2
                bits_com_paridade.extend(bloco)
                bits_com_paridade.append(paridade)
        return bits_com_paridade

    def verificar(self, bits_com_paridade: list) -> tuple:
        """Verifica paridade e remove bits de paridade"""
        bits = []
        tem_erro = False
        for i in range(0, len(bits_com_paridade), 9):
            if i + 8 < len(bits_com_paridade):
                bloco = bits_com_paridade[i:i+8]
                paridade_recebida = bits_com_paridade[i+8]
                paridade_calculada = sum(bloco) % 2
                if paridade_recebida != paridade_calculada:
                    tem_erro = True
                bits.extend(bloco)
        return bits, tem_erro


class DetectorChecksum(DetectorErros):
    """Detector por checksum"""

    def adicionar(self, bits: list) -> list:
        """Adiciona checksum (8 bits) aos bits"""
        if len(bits) == 0:
            return [0] * 8
        
        # Agrupa bits em bytes para calcular checksum
        soma = 0
        for i in range(0, len(bits), 8):
            byte_bits = bits[i:i+8]
            if len(byte_bits) == 8:
                byte_val = int(''.join(map(str, byte_bits)), 2)
                soma += byte_val
        
        soma = soma % 256
        checksum = (255 - soma) % 256
        checksum_bits = [int(b) for b in format(checksum, '08b')]
        
        return bits + checksum_bits

    def verificar(self, bits_com_checksum: list) -> tuple:
        """Verifica checksum e remove os 8 bits de checksum"""
        if len(bits_com_checksum) < 8:
            return [], True
        
        bits = bits_com_checksum[:-8]
        checksum_bits = bits_com_checksum[-8:]
        checksum_recebido = int(''.join(map(str, checksum_bits)), 2)
        
        # Calcula checksum dos bits
        soma = 0
        for i in range(0, len(bits), 8):
            byte_bits = bits[i:i+8]
            if len(byte_bits) == 8:
                byte_val = int(''.join(map(str, byte_bits)), 2)
                soma += byte_val
        
        soma = soma % 256
        checksum_calculado = (255 - soma) % 256
        tem_erro = (checksum_recebido != checksum_calculado)
        
        return bits, tem_erro


class DetectorCRC32(DetectorErros):
    """Detector CRC-32 (IEEE 802)"""

    def __init__(self):
        config = Config()
        self.polinomio = config.CRC32_POLYNOMIAL
        self.tabela = [
            0x00000000, 0x77073096, 0xEE0E612C, 0x990951BA,
            0x076DC419, 0x706AF48F, 0xE963A535, 0x9E6495A3,
            0x0EDB8832, 0x79DCB8A4, 0xE0D5E91E, 0x97D2D988,
            0x09B64C2B, 0x7EB17CBD, 0xE7B82D07, 0x90BF1D91
        ]

    def calcular_crc_bits(self, bits: list) -> int:
        """Calcula CRC-32 de uma lista de bits"""
        # Converte bits para bytes temporariamente
        bytes_dados = []
        for i in range(0, len(bits), 8):
            byte_bits = bits[i:i+8]
            if len(byte_bits) == 8:
                byte_val = int(''.join(map(str, byte_bits)), 2)
                bytes_dados.append(byte_val)
        
        # Calcula CRC
        crc = 0xFFFFFFFF
        for byte in bytes_dados:
            indice = (crc ^ byte) & 0xFF
            if indice < len(self.tabela):
                crc = (crc >> 8) ^ self.tabela[indice]
            else:
                crc = (crc >> 8) ^ (byte & 0xFF)
        return crc ^ 0xFFFFFFFF

    def adicionar(self, bits: list) -> list:
        """Adiciona CRC-32 (32 bits) aos bits"""
        crc = self.calcular_crc_bits(bits)
        crc_bits = [int(b) for b in format(crc, '032b')]
        return bits + crc_bits

    def verificar(self, bits_com_crc: list) -> tuple:
        """Verifica CRC-32 e remove os 32 bits de CRC"""
        if len(bits_com_crc) < 32:
            return [], True
        
        bits = bits_com_crc[:-32]
        crc_bits = bits_com_crc[-32:]
        crc_recebido = int(''.join(map(str, crc_bits)), 2)
        crc_calculado = self.calcular_crc_bits(bits)
        tem_erro = (crc_recebido != crc_calculado)
        return bits, tem_erro

# ==============================================================
# TESTES - Detecção de Erros
# ==============================================================

if __name__ == "__main__":
    from utils.conversor import Conversor
    
    print("\n" + "="*70)
    print("TESTANDO DETECÇÃO DE ERROS")
    print("="*70)

    # Converter texto para bits para testar
    texto = "Hi"
    bits_dados = Conversor.texto_para_bits(texto)
    print(f"\nTexto: '{texto}'")
    print(f"Bits ({len(bits_dados)}): {bits_dados}")

    # Teste Paridade
    print("\n--- Paridade ---")
    det1 = DetectorParidade()
    com_par = det1.adicionar(bits_dados)
    print(f"Com paridade ({len(com_par)} bits): {com_par}")
    rec, erro = det1.verificar(com_par)
    print(f"Recuperados ({len(rec)} bits): {rec}")
    print(f"Erro detectado? {erro}")
    texto_rec = Conversor.bits_para_texto(rec)
    print(f"Texto recuperado: '{texto_rec}'")
    print(f"✓ OK" if not erro and rec == bits_dados and texto_rec == texto else "✗ ERRO")

    # Teste Checksum
    print("\n--- Checksum ---")
    det2 = DetectorChecksum()
    com_check = det2.adicionar(bits_dados)
    print(f"Com checksum ({len(com_check)} bits): {com_check}")
    rec, erro = det2.verificar(com_check)
    print(f"Recuperados ({len(rec)} bits): {rec}")
    print(f"Erro detectado? {erro}")
    texto_rec = Conversor.bits_para_texto(rec)
    print(f"Texto recuperado: '{texto_rec}'")
    print(f"✓ OK" if not erro and rec == bits_dados and texto_rec == texto else "✗ ERRO")

    # Teste CRC-32
    print("\n--- CRC-32 ---")
    det3 = DetectorCRC32()
    com_crc = det3.adicionar(bits_dados)
    print(f"Com CRC ({len(com_crc)} bits): {com_crc}")
    rec, erro = det3.verificar(com_crc)
    print(f"Recuperados ({len(rec)} bits): {rec}")
    print(f"Erro detectado? {erro}")
    texto_rec = Conversor.bits_para_texto(rec)
    print(f"Texto recuperado: '{texto_rec}'")
    print(f"✓ OK" if not erro and rec == bits_dados and texto_rec == texto else "✗ ERRO")
    
    # Teste simulando erro
    print("\n" + "="*70)
    print("TESTANDO DETECÇÃO COM ERRO SIMULADO")
    print("="*70)
    
    print("\n--- CRC-32 com erro ---")
    com_crc = det3.adicionar(bits_dados)
    # Inverte um bit no meio
    com_crc_erro = com_crc.copy()
    com_crc_erro[len(com_crc_erro)//2] = 1 - com_crc_erro[len(com_crc_erro)//2]
    print(f"Bit invertido na posição {len(com_crc_erro)//2}")
    rec, erro = det3.verificar(com_crc_erro)
    print(f"Erro detectado? {erro}")
    print(f"✓ OK" if erro else "✗ ERRO - Deveria detectar erro!")