"""
Módulo de Enquadramento de Quadros.

Implementa dois protocolos de enquadramento para delimitar quadros no
fluxo de bits transmitido:

1. Contagem de Bytes: Usa campo de tamanho no cabeçalho
2. Bit Stuffing: Usa delimitadores FLAG (01111110) com inserção de bits

O enquadramento é essencial para separar mensagens individuais em um
fluxo contínuo de bits, permitindo ao receptor identificar onde cada
mensagem começa e termina.

Classes:
    Enquadrador: Classe abstrata base.
    EnquadradorContagem: Enquadramento por campo de tamanho.
    EnquadradorFlagsBits: Enquadramento com FLAGS e bit stuffing.

Problema do Enquadramento:
    Como saber onde cada mensagem começa e termina no fluxo de bits?
    Solução 1: Adicionar campo "tamanho" no início
    Solução 2: Usar delimitadores especiais (FLAGS)

Aplicações:
    - Ethernet: Usa preâmbulo + delimitador
    - HDLC/PPP: Usa FLAGS (01111110) com bit stuffing
    - ATM: Células de tamanho fixo (53 bytes)
    - USB: Pacotes com delimitadores

Exemplos:
    >>> # Contagem
    >>> enq = EnquadradorContagem()
    >>> dados = [1, 0, 1, 1, 0]
    >>> quadro = enq.enquadrar(dados)
    >>> # quadro = [16 bits tamanho] + dados
    >>> 
    >>> # Bit Stuffing
    >>> enq = EnquadradorFlagsBits()
    >>> quadro = enq.enquadrar(dados)
    >>> # quadro = [FLAG] + dados_stuffed + [FLAG]
"""

from abc import ABC, abstractmethod
from config import Config

class Enquadrador(ABC):
    """
    Classe abstrata base para enquadradores.
    
    Define a interface comum para todos os protocolos de enquadramento.
    Subclasses implementam diferentes técnicas: contagem, flags, etc.
    
    Conceito:
        Enquadramento é o processo de adicionar informação de controle
        aos dados para delimitar início e fim de cada quadro, permitindo
        ao receptor separar mensagens no fluxo de bits.
    
    Métodos Abstratos:
        enquadrar: Adiciona delimitadores/controle aos dados.
        desenquadrar: Remove delimitadores e extrai dados originais.
    
    Desafios:
        - Detectar início e fim de quadro sem ambiguidade
        - Lidar com dados que contêm padrões de delimitador
        - Minimizar overhead de enquadramento
        - Sincronização entre transmissor e receptor
    """

    @abstractmethod
    def enquadrar(self, dados: list) -> list:
        """
        Adiciona delimitadores/controle aos dados.
        
        Args:
            dados (list): Bits de dados a enquadrar.
            
        Returns:
            list: Quadro completo com delimitadores.
        """
        pass

    @abstractmethod
    def desenquadrar(self, quadro: list) -> list:
        """
        Remove delimitadores e extrai dados originais.
        
        Args:
            quadro (list): Quadro completo com delimitadores.
            
        Returns:
            list: Dados originais sem delimitadores.
        """
        pass


class EnquadradorContagem(Enquadrador):
    """
    Enquadramento por Contagem de Bytes.
    
    Adiciona um campo de tamanho (16 bits) no início do quadro indicando
    quantos bits de dados seguem. O receptor usa esse campo para saber
    exatamente quantos bits ler para o quadro completo.
    
    Formato do Quadro:
        [16 bits tamanho][dados...]
    
    Funcionamento:
        - Transmissor: calcula len(dados), converte para 16 bits, prepend
        - Receptor: lê 16 bits, interpreta como tamanho, lê tamanho bits
    
    Vantagens:
        - Simples e direto
        - Overhead fixo (16 bits = 2 bytes)
        - Não requer escape de dados
        - Eficiente para quadros grandes
    
    Desvantagens:
        - Vulnerável a erro no campo tamanho (dessincronia total)
        - Se campo tamanho corromper, todos os quadros seguintes são perdidos
        - Não detecta automaticamente limites de quadro
        - Requer sincronização inicial perfeita
    
    Tamanho Máximo:
        - 16 bits permitem até 65535 bits = 8191 bytes
        - Limitado por TAMANHO_MAX_QUADRO da configuração
    
    Overhead:
        - Fixo: 16 bits (2 bytes) por quadro
        - Para 256 bytes de dados: overhead = 0.8%
        - Para 64 bytes de dados: overhead = 3.1%
    
    Aplicações:
        - Protocolos ponto-a-ponto confiáveis
        - Redes de baixo ruído
        - Comunicação síncrona
    
    Exemplos:
        >>> enq = EnquadradorContagem()
        >>> dados = [1, 0, 1, 1, 0, 0, 1, 0]  # 8 bits
        >>> quadro = enq.enquadrar(dados)
        >>> print(len(quadro))
        24  # 16 bits tamanho + 8 bits dados
        >>> print(quadro[:16])  # Campo tamanho = 8
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0]
    """

    def __init__(self):
        """
        Inicializa enquadrador por contagem.
        
        Attributes:
            tamanho_max_quadro (int): Tamanho máximo do quadro em bits.
        """
        config = Config()
        self.tamanho_max_quadro = config.TAMANHO_MAX_QUADRO * 8  # converter bytes para bits

    def enquadrar(self, bits: list) -> list:
        """
        Adiciona campo de tamanho (16 bits) no início dos dados.
        
        Args:
            bits (list): Dados a enquadrar.
            
        Returns:
            list: [16 bits tamanho] + dados
            
        Raises:
            ValueError: Se dados excedem tamanho máximo configurado.
        
        Algoritmo:
            1. Verifica se len(dados) <= tamanho_max_quadro
            2. Converte len(dados) para 16 bits binário
            3. Retorna tamanho_bits + dados
        """
        tamanho = len(bits)
        
        # Verificar se excede tamanho máximo
        if tamanho > self.tamanho_max_quadro:
            raise ValueError(f"Quadro muito grande: {tamanho} bits > {self.tamanho_max_quadro} bits (máx: {self.tamanho_max_quadro//8} bytes)")
        
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
    """
    Enquadramento com FLAGS e Bit Stuffing.
    
    Usa padrão FLAG (01111110) para delimitar início e fim do quadro.
    Aplica bit stuffing nos dados para evitar que o padrão FLAG apareça
    acidentalmente nos dados: após 5 bits '1' consecutivos, insere um '0'.
    
    Formato do Quadro:
        [FLAG][dados com stuffing][FLAG]
        FLAG = 01111110 (0x7E)
    
    Funcionamento:
        - Transmissor:
          1. Envia FLAG de abertura
          2. Para cada bit de dados:
             - Se já enviou 5 bits '1': insere '0' (stuffing)
             - Envia o bit normal
          3. Envia FLAG de fechamento
        
        - Receptor:
          1. Procura FLAG de abertura
          2. Lê dados até próximo FLAG
          3. Remove bits stuffed (após 5 '1's, remove o '0')
    
    Vantagens:
        - Robusta contra perda de sincronização
        - Detecta automaticamente limites de quadro
        - Recupera de erros no meio do quadro
        - Não precisa conhecer tamanho antecipadamente
        - Usado em padrões reais (HDLC, PPP)
    
    Desvantagens:
        - Overhead variável (depende dos dados)
        - Pior caso: dados com muitos '1's
        - Requer processamento bit a bit
        - Overhead mínimo: 16 bits (2 FLAGS)
    
    Overhead:
        - Mínimo: 16 bits (2 FLAGS) se dados não têm sequências longas de '1'
        - Máximo: teórico infinito, prático ~20% para dados binários aleatórios
        - Típico: ~2-5% para dados normais
    
    Aplicações:
        - HDLC (High-Level Data Link Control)
        - PPP (Point-to-Point Protocol)
        - Frame Relay
        - SDLC (Synchronous Data Link Control)
    
    Regra de Stuffing:
        - TX: Após enviar 5 bits '1', insere '0'
        - RX: Após receber 5 bits '1', remove próximo '0'
        - FLAG: Único padrão permitido com 6 bits '1'
    
    Exemplos:
        >>> enq = EnquadradorFlagsBits()
        >>> dados = [1, 1, 1, 1, 1, 1]  # 6 uns consecutivos
        >>> quadro = enq.enquadrar(dados)
        >>> # quadro = [FLAG] + [1,1,1,1,1,0,1] + [FLAG]
        >>> #                     ↑ bit stuffed
        >>> print(len(quadro))
        23  # 8 (FLAG) + 7 (dados+stuff) + 8 (FLAG)
    """

    def __init__(self):
        """
        Inicializa enquadrador com FLAGS.
        
        Attributes:
            flag (list): Padrão FLAG = [0,1,1,1,1,1,1,0] (01111110).
            tamanho_max_quadro (int): Tamanho máximo antes do stuffing.
        """
        config = Config()
        self.flag = [0, 1, 1, 1, 1, 1, 1, 0]  # 01111110 (0x7E)
        self.tamanho_max_quadro = config.TAMANHO_MAX_QUADRO * 8  # converter bytes para bits

    def enquadrar(self, bits: list) -> list:
        # Verificar se excede tamanho máximo (antes do bit stuffing)
        if len(bits) > self.tamanho_max_quadro:
            raise ValueError(f"Quadro muito grande: {len(bits)} bits > {self.tamanho_max_quadro} bits (máx: {self.tamanho_max_quadro//8} bytes)")
        
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


