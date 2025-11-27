"""
Módulo de Enquadramento de Quadros.

Implementa três protocolos de enquadramento para delimitar quadros no
fluxo de bits transmitido:

1. Contagem de Bytes: Usa campo de tamanho no cabeçalho
2. Bit Stuffing: Usa delimitadores FLAG (01111110) com inserção de bits
3. Byte Stuffing: Usa delimitadores FLAG com escape de bytes (ESC)

O enquadramento é essencial para separar mensagens individuais em um
fluxo contínuo de bits, permitindo ao receptor identificar onde cada
mensagem começa e termina.

Classes:
    Enquadrador: Classe abstrata base.
    EnquadradorContagem: Enquadramento por campo de tamanho.
    EnquadradorFlagsBytes: Enquadramento com FLAGS e byte stuffing (opera em bits).
    EnquadradorFlagsBits: Enquadramento com FLAGS e bit stuffing.

Problema do Enquadramento:
    Como saber onde cada mensagem começa e termina no fluxo de bits?
    Solução 1: Adicionar campo "tamanho" no início
    Solução 2: Usar delimitadores especiais (FLAGS)
    Solução 3: Usar delimitadores + escape de caracteres especiais

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
    >>> # Byte Stuffing
    >>> enq = EnquadradorFlagsBytes()
    >>> dados = [0,1,0,0,0,0,0,1, 0,1,1,1,1,1,1,0]  # 'A' + FLAG
    >>> quadro = enq.enquadrar(dados)
    >>> # quadro = [FLAG] + [0x41] + [ESC] + [0x5E] + [FLAG]
    >>> 
    >>> # Bit Stuffing
    >>> enq = EnquadradorFlagsBits()
    >>> dados = [1, 0, 1, 1, 0]
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


class EnquadradorFlagsBytes(Enquadrador):
    """
    Enquadramento com FLAGS e Byte Stuffing (operando em bits).
    
    Usa byte FLAG (0x7E = 01111110) e byte ESC (0x7D = 01111101) para
    delimitar quadros. Quando FLAG ou ESC aparecem nos dados, são escapados
    com ESC seguido do byte XOR 0x20.
    
    IMPORTANTE: Opera em listas de BITS (não bytes), mantendo compatibilidade
    com o resto do sistema, mas implementa lógica de byte stuffing.
    
    Formato do Quadro:
        [FLAG byte][dados com byte stuffing][FLAG byte]
        FLAG = 0x7E = 01111110
        ESC  = 0x7D = 01111101
    
    Funcionamento:
        - Transmissor:
          1. Envia FLAG de abertura (8 bits)
          2. Processa dados byte a byte (grupos de 8 bits):
             - Se byte == FLAG (0x7E): envia ESC + (FLAG XOR 0x20)
             - Se byte == ESC (0x7D): envia ESC + (ESC XOR 0x20)
             - Senão: envia byte normal
          3. Envia FLAG de fechamento (8 bits)
        
        - Receptor:
          1. Procura FLAG de abertura
          2. Lê dados até próximo FLAG
          3. Remove bytes escapados:
             - Se encontrar ESC: próximo byte = byte XOR 0x20
    
    Vantagens:
        - Simples de implementar
        - Mantém alinhamento de byte (blocos de 8 bits)
        - Processamento rápido (byte a byte)
        - Usado em PPP assíncrono
    
    Desvantagens:
        - Overhead maior que bit stuffing (mínimo 16 bits, pode chegar a 100%)
        - Pior caso: dados cheios de 0x7E e 0x7D (dobra o tamanho)
        - Menos eficiente que bit stuffing para dados aleatórios
    
    Overhead:
        - Mínimo: 16 bits (2 FLAGS)
        - Médio: ~5-10% para dados normais
        - Máximo: 100% (dados = todos FLAG/ESC)
    
    Aplicações:
        - PPP (Point-to-Point Protocol) modo assíncrono
        - SLIP (Serial Line Internet Protocol)
        - Comunicação serial com escape
    
    Diferença de Bit Stuffing:
        - Bit stuffing: insere 1 BIT após 5 uns
        - Byte stuffing: insere 2 BYTES (16 bits) quando encontra FLAG/ESC
    
    Exemplos:
        >>> enq = EnquadradorFlagsBytes()
        >>> # Dados contêm FLAG (0x7E)
        >>> dados = [0,1,0,0,0,0,0,1, 0,1,1,1,1,1,1,0]  # 'A' + FLAG
        >>> quadro = enq.enquadrar(dados)
        >>> # Resultado: [FLAG][0x41][ESC][0x5E][FLAG]
        >>> #             8bits + 8bits + 8bits + 8bits + 8bits = 40 bits
    """

    def __init__(self):
        """
        Inicializa enquadrador com FLAGS e ESC para byte stuffing.
        
        Attributes:
            flag (list): Byte FLAG = [0,1,1,1,1,1,1,0] (0x7E).
            esc (list): Byte ESC = [0,1,1,1,1,1,0,1] (0x7D).
            xor_byte (list): Byte XOR = [0,0,1,0,0,0,0,0] (0x20) para modificar.
            tamanho_max_quadro (int): Tamanho máximo antes do stuffing.
        """
        config = Config()
        self.flag = [0, 1, 1, 1, 1, 1, 1, 0]  # 0x7E = 01111110
        self.esc = [0, 1, 1, 1, 1, 1, 0, 1]   # 0x7D = 01111101
        self.xor_byte = [0, 0, 1, 0, 0, 0, 0, 0]  # 0x20 = 00100000
        self.tamanho_max_quadro = config.TAMANHO_MAX_QUADRO * 8

    def _xor_bits(self, bits: list, mask: list) -> list:
        """
        Faz XOR bit a bit entre duas listas de 8 bits.
        
        Args:
            bits (list): 8 bits originais
            mask (list): 8 bits da máscara
            
        Returns:
            list: 8 bits resultantes do XOR
        """
        return [b ^ m for b, m in zip(bits, mask)]

    def enquadrar(self, bits: list) -> list:
        """
        Adiciona FLAGS e aplica byte stuffing nos dados.
        
        Args:
            bits (list): Dados em bits.
            
        Returns:
            list: Quadro com FLAGS e bytes escapados.
            
        Raises:
            ValueError: Se dados excedem tamanho máximo.
        
        Algoritmo:
            1. Verifica tamanho e alinhamento de byte
            2. Adiciona FLAG inicial
            3. Para cada byte (8 bits) dos dados:
               - Se byte == FLAG: adiciona ESC + (FLAG XOR 0x20)
               - Se byte == ESC: adiciona ESC + (ESC XOR 0x20)
               - Senão: adiciona byte normal
            4. Adiciona FLAG final
        """
        # Verificar tamanho
        if len(bits) > self.tamanho_max_quadro:
            raise ValueError(f"Quadro muito grande: {len(bits)} bits > {self.tamanho_max_quadro} bits")
        
        # Iniciar quadro com FLAG
        quadro = self.flag.copy()
        
        # Calcular bytes completos e bits restantes
        num_bytes_completos = len(bits) // 8
        bits_restantes = len(bits) % 8
        
        # Processar bytes completos (grupos de 8 bits)
        for i in range(num_bytes_completos):
            byte_bits = bits[i*8:(i+1)*8]
            
            # Verificar se precisa escapar (comparação de LISTAS de bits)
            # Apenas bytes completos (8 bits) podem ser FLAG ou ESC
            if byte_bits == self.flag:  # Byte é FLAG?
                # Adicionar ESC + (FLAG XOR 0x20)
                quadro.extend(self.esc)
                byte_escapado = self._xor_bits(byte_bits, self.xor_byte)
                quadro.extend(byte_escapado)
            elif byte_bits == self.esc:  # Byte é ESC?
                # Adicionar ESC + (ESC XOR 0x20)
                quadro.extend(self.esc)
                byte_escapado = self._xor_bits(byte_bits, self.xor_byte)
                quadro.extend(byte_escapado)
            else:
                # Byte normal, adicionar sem modificação
                quadro.extend(byte_bits)
        
        # Se houver bits restantes (< 8 bits), adicionar diretamente
        # Bits parciais não podem ser FLAG nem ESC, então não precisam de escape
        if bits_restantes > 0:
            quadro.extend(bits[num_bytes_completos * 8:])
        
        # Adicionar FLAG final
        quadro.extend(self.flag)
        
        return quadro

    def desenquadrar(self, quadro: list) -> list:
        """
        Remove FLAGS e desfaz byte stuffing.
        
        Args:
            quadro (list): Quadro completo com FLAGS.
            
        Returns:
            list: Dados originais sem FLAGS e com bytes desescapados.
        
        Algoritmo:
            1. Remove FLAGS inicial e final
            2. Processa bytes:
               - Se encontrar ESC: próximo byte XOR 0x20
               - Senão: byte normal
        """
        tam_flag = len(self.flag)
        
        # Verificar tamanho mínimo (2 FLAGS)
        if len(quadro) <= 2 * tam_flag:
            return []
        
        # Remover FLAGS inicial e final
        bits = quadro[tam_flag:-tam_flag]
        
        # Calcular bytes completos e bits restantes
        num_bytes_completos = len(bits) // 8
        bits_restantes = len(bits) % 8
        
        dados = []
        i = 0
        
        # Processar bytes completos (trabalhando apenas com listas de bits)
        while i < num_bytes_completos * 8:
            byte_bits = bits[i:i+8]
            
            # Se é ESC, próximo byte está escapado
            if byte_bits == self.esc:
                i += 8  # Pula o ESC
                if i >= num_bytes_completos * 8:
                    break  # ESC sem byte seguinte (erro)
                
                byte_bits = bits[i:i+8]
                byte_original = self._xor_bits(byte_bits, self.xor_byte)  # Desfaz XOR
                dados.extend(byte_original)
            else:
                # Byte normal
                dados.extend(byte_bits)
            
            i += 8
        
        # Se houver bits restantes, adicionar diretamente
        if bits_restantes > 0:
            dados.extend(bits[num_bytes_completos * 8:])
        
        return dados


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


