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


class DetectorChecksumVariavel(DetectorErros):
    """Detector por checksum com tamanho variável"""

    def __init__(self, tamanho_bits: int = 8):
        """
        Args:
            tamanho_bits: Tamanho do checksum em bits (8, 16, 24 ou 32)
        """
        if tamanho_bits not in [8, 16, 24, 32]:
            raise ValueError("Tamanho do checksum deve ser 8, 16, 24 ou 32 bits")
        self.tamanho_bits = tamanho_bits
        self.max_valor = (1 << tamanho_bits) - 1  # 2^n - 1

    def adicionar(self, bits: list) -> list:
        """Adiciona checksum aos bits"""
        if len(bits) == 0:
            return [0] * self.tamanho_bits
        
        # Agrupa bits em bytes para calcular checksum
        soma = 0
        for i in range(0, len(bits), 8):
            byte_bits = bits[i:i+8]
            if len(byte_bits) == 8:
                byte_val = int(''.join(map(str, byte_bits)), 2)
                soma += byte_val
        
        soma = soma % (self.max_valor + 1)
        checksum = (self.max_valor - soma) % (self.max_valor + 1)
        checksum_bits = [int(b) for b in format(checksum, f'0{self.tamanho_bits}b')]
        
        return bits + checksum_bits

    def verificar(self, bits_com_checksum: list) -> tuple:
        """Verifica checksum e remove os bits de checksum"""
        if len(bits_com_checksum) < self.tamanho_bits:
            return [], True
        
        bits = bits_com_checksum[:-self.tamanho_bits]
        checksum_bits = bits_com_checksum[-self.tamanho_bits:]
        checksum_recebido = int(''.join(map(str, checksum_bits)), 2)
        
        # Calcula checksum dos bits
        soma = 0
        for i in range(0, len(bits), 8):
            byte_bits = bits[i:i+8]
            if len(byte_bits) == 8:
                byte_val = int(''.join(map(str, byte_bits)), 2)
                soma += byte_val
        
        soma = soma % (self.max_valor + 1)
        checksum_calculado = (self.max_valor - soma) % (self.max_valor + 1)
        tem_erro = (checksum_recebido != checksum_calculado)
        
        return bits, tem_erro


class DetectorCRCVariavel(DetectorErros):
    """Detector CRC com tamanho variável"""

    def __init__(self, tamanho_bits: int = 32):
        """
        Args:
            tamanho_bits: Tamanho do CRC em bits (8, 16, 24 ou 32)
        """
        if tamanho_bits not in [8, 16, 24, 32]:
            raise ValueError("Tamanho do CRC deve ser 8, 16, 24 ou 32 bits")
        self.tamanho_bits = tamanho_bits
        
        # Polinômios padrão para cada tamanho
        polinomios = {
            8: 0xD5,        # CRC-8 (0x1D5 >> 1)
            16: 0x8005,     # CRC-16-IBM
            24: 0x864CFB,   # CRC-24 (OpenPGP)
            32: 0x04C11DB7  # CRC-32 (IEEE 802.3)
        }
        self.polinomio = polinomios[tamanho_bits]
        self._gerar_tabela()

    def _gerar_tabela(self):
        """Gera tabela de lookup para CRC"""
        self.tabela = []
        for i in range(256):
            crc = i
            if self.tamanho_bits == 8:
                for _ in range(8):
                    if crc & 0x80:
                        crc = (crc << 1) ^ self.polinomio
                    else:
                        crc = crc << 1
                    crc &= 0xFF
            elif self.tamanho_bits == 16:
                for _ in range(8):
                    if crc & 0x8000:
                        crc = (crc << 1) ^ self.polinomio
                    else:
                        crc = crc << 1
                    crc &= 0xFFFF
            elif self.tamanho_bits == 24:
                for _ in range(8):
                    if crc & 0x800000:
                        crc = (crc << 1) ^ self.polinomio
                    else:
                        crc = crc << 1
                    crc &= 0xFFFFFF
            else:  # 32 bits
                crc = i << 24
                for _ in range(8):
                    if crc & 0x80000000:
                        crc = (crc << 1) ^ self.polinomio
                    else:
                        crc = crc << 1
                    crc &= 0xFFFFFFFF
            self.tabela.append(crc)

    def calcular_crc_bits(self, bits: list) -> int:
        """Calcula CRC de uma lista de bits"""
        # Converte bits para bytes
        bytes_dados = []
        for i in range(0, len(bits), 8):
            byte_bits = bits[i:i+8]
            if len(byte_bits) == 8:
                byte_val = int(''.join(map(str, byte_bits)), 2)
                bytes_dados.append(byte_val)
        
        # Calcula CRC
        max_val = (1 << self.tamanho_bits) - 1
        crc = max_val
        
        for byte in bytes_dados:
            if self.tamanho_bits <= 16:
                indice = (crc ^ byte) & 0xFF
                if indice < len(self.tabela):
                    crc = (crc >> 8) ^ self.tabela[indice]
            else:
                indice = ((crc >> (self.tamanho_bits - 8)) ^ byte) & 0xFF
                if indice < len(self.tabela):
                    crc = ((crc << 8) ^ self.tabela[indice]) & max_val
        
        return crc ^ max_val

    def adicionar(self, bits: list) -> list:
        """Adiciona CRC aos bits"""
        crc = self.calcular_crc_bits(bits)
        crc_bits = [int(b) for b in format(crc, f'0{self.tamanho_bits}b')]
        return bits + crc_bits

    def verificar(self, bits_com_crc: list) -> tuple:
        """Verifica CRC e remove os bits de CRC"""
        if len(bits_com_crc) < self.tamanho_bits:
            return [], True
        
        bits = bits_com_crc[:-self.tamanho_bits]
        crc_bits = bits_com_crc[-self.tamanho_bits:]
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

    # Teste Checksum Variável (8 bits)
    print("\n--- Checksum (8 bits) ---")
    det2 = DetectorChecksumVariavel(8)
    com_check = det2.adicionar(bits_dados)
    print(f"Com checksum ({len(com_check)} bits): {com_check}")
    rec, erro = det2.verificar(com_check)
    print(f"Recuperados ({len(rec)} bits): {rec}")
    print(f"Erro detectado? {erro}")
    texto_rec = Conversor.bits_para_texto(rec)
    print(f"Texto recuperado: '{texto_rec}'")
    print(f"✓ OK" if not erro and rec == bits_dados and texto_rec == texto else "✗ ERRO")

    # Teste CRC Variável (32 bits)
    print("\n--- CRC (32 bits) ---")
    det3 = DetectorCRCVariavel(32)
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
    
    print("\n--- CRC (32 bits) com erro ---")
    com_crc = det3.adicionar(bits_dados)
    # Inverte um bit no meio
    com_crc_erro = com_crc.copy()
    com_crc_erro[len(com_crc_erro)//2] = 1 - com_crc_erro[len(com_crc_erro)//2]
    print(f"Bit invertido na posição {len(com_crc_erro)//2}")
    rec, erro = det3.verificar(com_crc_erro)
    print(f"Erro detectado? {erro}")
    print(f"✓ OK" if erro else "✗ ERRO - Deveria detectar erro!")