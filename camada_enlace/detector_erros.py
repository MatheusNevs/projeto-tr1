"""
Módulo de Detecção de Erros.

Implementa três técnicas fundamentais de detecção de erros de transmissão:
- Paridade: Simples, detecta erros ímpares
- Checksum: Soma de verificação com tamanho variável (8/16/24/32 bits)
- CRC: Código de Redundância Cíclica com tamanho variável (8/16/24/32 bits)

Classes:
    DetectorErros: Classe abstrata base para todos os detectores.
    DetectorParidade: Detecção por bit de paridade par.
    DetectorChecksumVariavel: Checksum configurável (8/16/24/32 bits).
    DetectorCRCVariavel: CRC configurável (8/16/24/32 bits).

Características:
    - EDC (Error Detection Code) adicionado aos dados
    - Detectam erros mas não corrigem automaticamente
    - Trade-off: overhead vs capacidade de detecção
    - CRC > Checksum > Paridade (em robustez)

Exemplos:
    >>> detector = DetectorParidade()
    >>> bits = [1, 0, 1, 1, 0, 0, 1, 0]
    >>> bits_com_edc = detector.adicionar(bits)
    >>> dados, tem_erro = detector.verificar(bits_com_edc)
"""

from abc import ABC, abstractmethod
from config import Config

class DetectorErros(ABC):
    """
    Classe abstrata base para detectores de erro.
    
    Define a interface comum para todos os detectores de erro.
    Subclasses implementam diferentes algoritmos de detecção:
    paridade, checksum, CRC, etc.
    
    Métodos Abstratos:
        adicionar: Adiciona código de detecção aos dados.
        verificar: Verifica presença de erros e remove código.
    
    Conceito de EDC (Error Detection Code):
        EDC são bits/bytes redundantes adicionados aos dados originais
        que permitem detectar se houve erro na transmissão. Não corrigem
        automaticamente, apenas detectam.
    
    Exemplos:
        Subclasses devem implementar:
        >>> class MeuDetector(DetectorErros):
        ...     def adicionar(self, dados):
        ...         # lógica de adicionar EDC
        ...     def verificar(self, dados_com_edc):
        ...         # lógica de verificar e remover EDC
    """

    @abstractmethod
    def adicionar(self, dados: list) -> list:
        """
        Adiciona código de detecção de erro aos dados.
        
        Args:
            dados (list): Dados originais (bits ou bytes).
            
        Returns:
            list: Dados com código de detecção adicionado.
        
        Notas:
            Método abstrato - deve ser implementado pelas subclasses.
        """
        pass

    @abstractmethod
    def verificar(self, dados_com_verificacao: list) -> tuple:
        """
        Verifica presença de erros e remove código de detecção.
        
        Args:
            dados_com_verificacao (list): Dados com código de detecção.
            
        Returns:
            tuple: (dados_originais: list, tem_erro: bool)
                  - dados_originais: Dados sem o código de detecção
                  - tem_erro: True se erro foi detectado
        
        Notas:
            Método abstrato - deve ser implementado pelas subclasses.
        """
        pass


class DetectorParidade(DetectorErros):
    """
    Detector de Paridade Par.
    
    Técnica mais simples de detecção de erros. Adiciona 1 bit de paridade
    a cada 8 bits de dados, garantindo que o número total de bits 1 seja par.
    
    Funcionamento:
        - Paridade par: soma dos bits deve ser par
        - Bit de paridade = (soma dos bits de dados) % 2
        - Se houver número ímpar de erros, detecta
        - Se houver número par de erros, NÃO detecta
    
    Vantagens:
        - Extremamente simples de implementar
        - Overhead mínimo (1 bit a cada 8 = 12.5%)
        - Rápido (apenas soma e módulo)
    
    Desvantagens:
        - Detecta apenas erros ímpares (1, 3, 5, ...)
        - Não detecta erros pares (2, 4, 6, ...)
        - Não indica posição do erro
        - Não corrige erros
    
    Aplicações:
        - Memória RAM (ECC básico)
        - Comunicação serial simples
        - Discos rígidos (parcialmente)
        - Ethernet (parcialmente)
    
    Taxa de Detecção:
        - 50% dos erros em geral
        - 100% dos erros de 1 bit
        - 0% dos erros de 2 bits
    
    Exemplos:
        >>> detector = DetectorParidade()
        >>> bits = [1, 0, 1, 1, 0, 0, 1, 0]  # soma = 4 (par)
        >>> bits_com_par = detector.adicionar(bits)
        >>> print(bits_com_par)
        [1, 0, 1, 1, 0, 0, 1, 0, 0]  # paridade = 0
        >>> 
        >>> # Simulando erro de 1 bit
        >>> bits_com_erro = bits_com_par.copy()
        >>> bits_com_erro[0] = 0  # Inverte bit
        >>> dados, erro = detector.verificar(bits_com_erro)
        >>> print(erro)
        True
    """

    def adicionar(self, bits: list) -> list:
        """
        Adiciona bit de paridade par a cada bloco de 8 bits.
        
        Para cada 8 bits consecutivos, calcula a paridade par
        (soma % 2) e adiciona como 9º bit.
        
        Args:
            bits (list): Sequência de bits a proteger.
            
        Returns:
            list: Bits com paridade adicionada (9 bits a cada 8 originais).
        
        Algoritmo:
            1. Divide bits em blocos de 8
            2. Para cada bloco completo (8 bits):
               a. Calcula paridade = sum(bloco) % 2
               b. Adiciona bloco + bit de paridade à saída
            3. Blocos incompletos (<8 bits) são ignorados
        
        Overhead:
            - 1 bit adicional a cada 8 bits
            - Overhead = 12.5%
            - Para 80 bits: resultado = 90 bits
        
        Exemplos:
            >>> detector = DetectorParidade()
            >>> bits = [1, 1, 0, 0, 1, 0, 1, 0]  # soma = 4
            >>> resultado = detector.adicionar(bits)
            >>> print(resultado)
            [1, 1, 0, 0, 1, 0, 1, 0, 0]  # paridade = 0 (soma par)
        """
        bits_com_paridade = []
        for i in range(0, len(bits), 8):
            bloco = bits[i:i+8]
            if len(bloco) == 8:
                paridade = sum(bloco) % 2
                bits_com_paridade.extend(bloco)
                bits_com_paridade.append(paridade)
        return bits_com_paridade

    def verificar(self, bits_com_paridade: list) -> tuple:
        """
        Verifica paridade e remove bits de paridade.
        
        Para cada bloco de 9 bits, verifica se a paridade está correta
        comparando paridade recebida com paridade calculada.
        
        Args:
            bits_com_paridade (list): Bits com paridade (9 bits por bloco).
            
        Returns:
            tuple: (bits_originais, tem_erro)
                  - bits_originais: Dados sem bits de paridade
                  - tem_erro: True se algum bloco tiver erro de paridade
        
        Algoritmo:
            1. Divide bits em blocos de 9
            2. Para cada bloco completo:
               a. Extrai 8 bits de dados
               b. Extrai bit de paridade (9º bit)
               c. Calcula paridade esperada
               d. Compara paridades
               e. Se diferentes → tem_erro = True
            3. Retorna dados originais e flag de erro
        
        Comportamento com Erros:
            - 1 bit errado: DETECTA (paridade muda)
            - 2 bits errados: NÃO DETECTA (paridade volta ao normal)
            - 3 bits errados: DETECTA
            - n ímpares: DETECTA
            - n pares: NÃO DETECTA
        
        Notas:
            - Flag tem_erro é global (qualquer bloco com erro)
            - Não indica qual bloco ou qual bit está errado
            - Dados são sempre retornados (com ou sem erro)
        
        Exemplos:
            >>> detector = DetectorParidade()
            >>> bits_ok = [1, 0, 1, 1, 0, 0, 1, 0, 0]
            >>> dados, erro = detector.verificar(bits_ok)
            >>> print(dados, erro)
            [1, 0, 1, 1, 0, 0, 1, 0] False
            >>>
            >>> # Com erro
            >>> bits_erro = [0, 0, 1, 1, 0, 0, 1, 0, 0]  # 1º bit errado
            >>> dados, erro = detector.verificar(bits_erro)
            >>> print(erro)
            True
        """
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
    """
    Detector por Checksum com Tamanho Variável.
    
    Implementa detecção por soma de verificação configurável (8, 16, 24 ou 32 bits).
    O checksum é calculado somando todos os bytes dos dados e usando apenas
    os bits menos significativos conforme o tamanho configurado.
    
    Funcionamento:
        1. Converte bits em bytes
        2. Soma todos os bytes
        3. Mantém apenas os N bits menos significativos (8/16/24/32)
        4. Adiciona checksum ao final dos dados
    
    Tamanhos Suportados:
        - 8 bits: 1 byte de checksum (overhead ~0.4%)
        - 16 bits: 2 bytes de checksum (overhead ~0.8%)
        - 24 bits: 3 bytes de checksum (overhead ~1.2%)
        - 32 bits: 4 bytes de checksum (overhead ~1.6%)
    
    Vantagens:
        - Simples de implementar
        - Baixo overhead
        - Detecta erros de múltiplos bits
        - Rápido de calcular
    
    Desvantagens:
        - Vulnerável a erros que se cancelam
        - Não detecta reordenação de bytes
        - Pode ter colisões (dois dados diferentes, mesmo checksum)
        - Menos robusto que CRC
    
    Aplicações:
        - Protocolo TCP/IP (checksum de 16 bits)
        - UDP (checksum de 16 bits)
        - Validação de arquivos
        - Verificação rápida de integridade
    
    Taxa de Detecção:
        - 8 bits: ~99.6% dos erros
        - 16 bits: ~99.998% dos erros
        - 32 bits: ~99.9999999% dos erros
    
    Exemplos:
        >>> detector = DetectorChecksumVariavel(tamanho_bits=16)
        >>> bits = [1, 0, 1, 1, 0, 0, 1, 0] * 10  # 80 bits
        >>> bits_com_checksum = detector.adicionar(bits)
        >>> # 80 bits originais + 16 bits de checksum = 96 bits
        >>> print(len(bits_com_checksum))
        96
    O checksum é calculado somando todos os bytes e aplicando complemento de 1.
    
    Funcionamento:
        1. Soma todos os bytes dos dados
        2. Aplica módulo (2^n) onde n = tamanho_bits
        3. Calcula complemento: checksum = (max_valor - soma) % (max_valor + 1)
        4. Adiciona checksum ao final dos dados
    
    Vantagens:
        - Mais robusto que paridade
        - Detecta erros múltiplos
        - Detecta bytes fora de ordem
        - Overhead configurável
    
    Desvantagens:
        - Não detecta alguns padrões de erro
        - Menos robusto que CRC
        - Não detecta inserção/remoção de zeros
    
    Aplicações:
        - TCP/IP (checksum de 16 bits)
        - UDP
        - IPv4 header
    
    Taxas de Detecção (16 bits):
        - ~99.998% dos erros aleatórios
        - 100% dos erros de 1 bit
        - 100% dos erros de 2 bits (geralmente)
    
    Exemplos:
        >>> detector = DetectorChecksumVariavel(16)  # Checksum de 16 bits
        >>> bits = [1]*80  # 10 bytes
        >>> bits_com_check = detector.adicionar(bits)
        >>> dados, erro = detector.verificar(bits_com_check)
    """

    def __init__(self, tamanho_bits: int = 8):
        """
        Inicializa detector de checksum com tamanho configurável.
        
        Args:
            tamanho_bits (int): Tamanho do checksum em bits.
                               Valores válidos: 8, 16, 24, 32.
        
        Raises:
            ValueError: Se tamanho_bits não for 8, 16, 24 ou 32.
        
        Atributos:
            tamanho_bits: Tamanho do checksum em bits.
            max_valor: Valor máximo representável (2^n - 1).
        
        Overhead:
            - 8 bits: +1 byte (mínimo)
            - 16 bits: +2 bytes (TCP/UDP)
            - 24 bits: +3 bytes (intermediário)
            - 32 bits: +4 bytes (maior robustez)
        """
        if tamanho_bits not in [8, 16, 24, 32]:
            raise ValueError("Tamanho do checksum deve ser 8, 16, 24 ou 32 bits")
        self.tamanho_bits = tamanho_bits
        self.max_valor = (1 << tamanho_bits) - 1  # 2^n - 1

    def adicionar(self, bits: list) -> list:
        """
        Adiciona checksum aos bits.
        
        Soma todos os bytes e calcula complemento de 1, adicionando
        o checksum ao final dos dados.
        
        Args:
            bits (list): Bits a proteger (múltiplo de 8).
            
        Returns:
            list: Bits originais + checksum (tamanho_bits adicionais).
        
        Algoritmo:
            1. Agrupa bits em bytes (8 bits)
            2. Converte cada byte para inteiro
            3. Soma todos os bytes: soma = Σ(bytes)
            4. Aplica módulo: soma = soma % (2^n)
            5. Calcula complemento: checksum = (2^n - 1 - soma) % 2^n
            6. Converte checksum para bits
            7. Retorna dados + checksum_bits
        """
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
    """
    Detector CRC (Cyclic Redundancy Check) com Tamanho Variável.
    
    Implementa CRC configurável (8, 16, 24 ou 32 bits) usando polinômios
    padrão da indústria. CRC é um código de detecção extremamente robusto
    baseado em aritmética polinomial sobre campos finitos.
    
    Funcionamento:
        1. Trata dados como polinômio binário
        2. Divide por polinômio gerador
        3. Resto da divisão = CRC
        4. Adiciona CRC ao final dos dados
        5. Na recepção, calcula CRC novamente e compara
    
    Polinômios Padrão:
        - CRC-8: 0xD5 (x^8 + x^7 + x^6 + x^4 + x^2 + 1)
        - CRC-16: 0x8005 (CRC-16-IBM, usado em USB)
        - CRC-24: 0x864CFB (OpenPGP)
        - CRC-32: 0x04C11DB7 (IEEE 802.3, Ethernet, ZIP)
    
    Vantagens:
        - Extremamente robusto
        - Detecta erros burst (rajadas)
        - Detecta 100% erros de 1 bit
        - Detecta 100% erros de 2 bits (polinômio adequado)
        - Detecta 100% burst errors ≤ tamanho do CRC
        - Usado em Ethernet, USB, discos, etc.
    
    Desvantagens:
        - Mais complexo que checksum
        - Requer tabela de lookup (otimização)
        - Overhead maior
        - Não corrige erros
    
    Taxa de Detecção:
        - CRC-8: 99.6% dos erros
        - CRC-16: 99.998% dos erros
        - CRC-32: 99.9999998% dos erros (1 em 4 bilhões)
    
    Aplicações:
        - Ethernet (CRC-32)
        - USB (CRC-16)
        - Discos rígidos (CRC-32)
        - Arquivos ZIP/PNG (CRC-32)
        - Bluetooth (CRC-16)
    
    Exemplos:
        >>> detector = DetectorCRCVariavel(tamanho_bits=32)
        >>> bits = [1, 0, 1, 1] * 20  # 80 bits
        >>> bits_com_crc = detector.adicionar(bits)
        >>> # 80 bits + 32 bits CRC = 112 bits
        >>> print(len(bits_com_crc))
        112
        >>> dados, erro = detector.verificar(bits_com_crc)
        >>> print(erro)
        False
    """

    def __init__(self, tamanho_bits: int = 32):
        """
        Inicializa detector CRC com tamanho configurável.
        
        Args:
            tamanho_bits (int): Tamanho do CRC em bits.
                               Valores válidos: 8, 16, 24, 32.
        
        Raises:
            ValueError: Se tamanho_bits não for 8, 16, 24 ou 32.
        
        Atributos:
            tamanho_bits: Tamanho do CRC em bits.
            polinomio: Polinômio gerador padrão para o tamanho.
            tabela: Tabela de lookup de 256 entradas para cálculo rápido.
        
        Polinômios Usados:
            - 8 bits: 0xD5
            - 16 bits: 0x8005 (CRC-16-IBM)
            - 24 bits: 0x864CFB (OpenPGP)
            - 32 bits: 0x04C11DB7 (IEEE 802.3)
        
        Notas:
            A tabela de lookup é pré-calculada na inicialização
            para acelerar o cálculo do CRC (256× mais rápido).
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