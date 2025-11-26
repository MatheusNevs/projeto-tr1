"""
Módulo de Configurações Globais do Simulador TR1.

Este módulo implementa um Singleton para gerenciar todas as configurações
do simulador de comunicação digital, incluindo parâmetros das camadas física
e de enlace, além de configurações do canal de comunicação.

Classes:
    Config: Singleton que armazena e gerencia todas as configurações globais.

Exemplos:
    >>> config = Config()
    >>> config.set_taxa_amostragem(5000)
    >>> config.set_taxa_bits(100)
    >>> print(f"Amostras por bit: {config.TAXA_AMOSTRAGEM / config.TAXA_BITS}")
"""

class Config:
    """
    Singleton para gerenciamento de configurações globais do simulador.
    
    Esta classe implementa o padrão Singleton para garantir que apenas uma
    instância das configurações exista durante toda a execução do programa.
    Gerencia parâmetros críticos das camadas física e de enlace.
    
    Attributes:
        TAXA_AMOSTRAGEM (int): Taxa de amostragem do sinal em Hz (100-10000 Hz).
        TAXA_BITS (int): Taxa de transmissão em bits por segundo (1-1000 bps).
        FREQUENCIA_PORTADORA (int): Frequência da portadora em Hz (10-1000 Hz).
        AMPLITUDE (float): Amplitude do sinal em Volts.
        TAMANHO_MAX_QUADRO (int): Tamanho máximo do quadro em bytes (64-1024).
        BYTE_FLAG (int): Byte delimitador de quadro (0x7E).
        BYTE_ESC (int): Byte de escape para byte stuffing (0x7D).
        RUIDO_MEDIA (float): Média do ruído gaussiano adicionado ao sinal.
        RUIDO_DESVIO (float): Desvio padrão do ruído gaussiano.
        CRC32_POLYNOMIAL (int): Polinômio para cálculo de CRC-32.
    
    Notas:
        - A relação Taxa_Amostragem/Taxa_Bits determina amostras por bit
        - Freq_Portadora deve ser < Taxa_Amostragem/2 (Teorema de Nyquist)
        - Para modulações por portadora, recomenda-se Freq_Portadora/Taxa_Bits >= 3
    """
    _instance = None

    def __new__(cls):
        """
        Implementa o padrão Singleton.
        
        Garante que apenas uma instância da classe Config seja criada.
        Na primeira chamada, cria e inicializa a instância. Nas chamadas
        subsequentes, retorna a instância já existente.
        
        Returns:
            Config: A única instância da classe Config.
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._inicializar()
        return cls._instance

    def _inicializar(self):
        """
        Inicializa os valores padrão de todas as configurações.
        
        Este método é chamado apenas uma vez, quando a instância Singleton
        é criada pela primeira vez. Define valores padrão seguros para
        todos os parâmetros do sistema.
        """
        # Camada Física
        self.TAXA_AMOSTRAGEM = 1000  # Hz - amostras por segundo
        self.TAXA_BITS = 10  # bits por segundo
        self.FREQUENCIA_PORTADORA = 100  # Hz - frequência da onda portadora
        self.AMPLITUDE = 5.0  # Volts - amplitude do sinal

        # Camada de Enlace
        self.TAMANHO_MAX_QUADRO = 256  # bytes - tamanho máximo do quadro
        self.BYTE_FLAG = 0x7E  # 01111110 - delimitador de quadro
        self.BYTE_ESC = 0x7D   # 01111101 - byte de escape

        # Canal de Comunicação
        self.RUIDO_MEDIA = 0.0  # média do ruído gaussiano
        self.RUIDO_DESVIO = 0.5  # desvio padrão do ruído

        # Algoritmos de Detecção
        self.CRC32_POLYNOMIAL = 0x04C11DB7  # polinômio CRC-32 padrão

    def set_tamanho_max_quadro(self, tamanho: int):
        """
        Atualiza o tamanho máximo do quadro de dados.
        
        Define o limite superior para o tamanho dos quadros transmitidos.
        Quadros maiores podem ser mais eficientes, mas são mais susceptíveis
        a erros. O valor deve estar entre 64 e 1024 bytes.
        
        Args:
            tamanho (int): Novo tamanho máximo em bytes (64-1024).
            
        Raises:
            ValueError: Se tamanho < 64 ou tamanho > 1024.
            
        Exemplos:
            >>> config = Config()
            >>> config.set_tamanho_max_quadro(512)
            >>> print(config.TAMANHO_MAX_QUADRO)
            512
        """
        if tamanho < 64:
            raise ValueError("Tamanho mínimo do quadro é 64 bytes")
        if tamanho > 1024:
            raise ValueError("Tamanho máximo do quadro é 1024 bytes")
        self.TAMANHO_MAX_QUADRO = tamanho

    def set_taxa_amostragem(self, taxa: int):
        """
        Atualiza a taxa de amostragem do sinal.
        
        Define quantas amostras por segundo serão usadas para representar
        o sinal digital. Taxas maiores permitem representar frequências mais
        altas (Teorema de Nyquist: f_max = taxa/2), mas geram mais dados.
        
        Args:
            taxa (int): Nova taxa em Hz (100-10000).
            
        Raises:
            ValueError: Se taxa < 100 ou taxa > 10000.
            
        Notas:
            - Taxa maior = melhor resolução temporal, mais dados
            - Deve ser pelo menos 2x a maior frequência do sinal
            - amostras_por_bit = TAXA_AMOSTRAGEM / TAXA_BITS
            
        Exemplos:
            >>> config = Config()
            >>> config.set_taxa_amostragem(5000)
            >>> config.set_taxa_bits(100)
            >>> print(f"Amostras/bit: {config.TAXA_AMOSTRAGEM/config.TAXA_BITS}")
            Amostras/bit: 50.0
        """
        if taxa < 100:
            raise ValueError("Taxa de amostragem mínima é 100 Hz")
        if taxa > 10000:
            raise ValueError("Taxa de amostragem máxima é 10000 Hz")
        self.TAXA_AMOSTRAGEM = taxa

    def set_taxa_bits(self, taxa: int):
        """
        Atualiza a taxa de transmissão de bits.
        
        Define quantos bits por segundo serão transmitidos. Taxas maiores
        permitem transmissão mais rápida, mas requerem mais amostras por bit
        ou reduzem a resolução temporal de cada bit.
        
        Args:
            taxa (int): Nova taxa em bits por segundo (1-1000).
            
        Raises:
            ValueError: Se taxa < 1 ou taxa > 1000.
            
        Notas:
            - Taxa maior = transmissão mais rápida, menos amostras por bit
            - amostras_por_bit = TAXA_AMOSTRAGEM / TAXA_BITS
            - Recomendado: amostras_por_bit >= 10 para boa qualidade
            
        Exemplos:
            >>> config = Config()
            >>> config.set_taxa_bits(50)
            >>> print(f"Amostras/bit: {config.TAXA_AMOSTRAGEM/config.TAXA_BITS}")
            Amostras/bit: 20.0
        """
        if taxa < 1:
            raise ValueError("Taxa de bits mínima é 1 bps")
        if taxa > 1000:
            raise ValueError("Taxa de bits máxima é 1000 bps")
        self.TAXA_BITS = taxa

    def set_frequencia_portadora(self, frequencia: int):
        """
        Atualiza a frequência da onda portadora.
        
        Define a frequência da senoide usada nas modulações por portadora
        (ASK, FSK, QPSK, QAM). Afeta apenas modulações analógicas, não
        impacta modulações digitais (NRZ, Manchester, Bipolar).
        
        Args:
            frequencia (int): Nova frequência em Hz (10-1000).
            
        Raises:
            ValueError: Se frequencia < 10 ou frequencia > 1000.
            
        Notas:
            - Deve ser < TAXA_AMOSTRAGEM/2 (Teorema de Nyquist)
            - Recomendado: FREQUENCIA_PORTADORA/TAXA_BITS >= 3
            - Frequência maior = mais ciclos por bit, melhor modulação
            
        Exemplos:
            >>> config = Config()
            >>> config.set_frequencia_portadora(200)
            >>> config.set_taxa_bits(50)
            >>> print(f"Ciclos/bit: {config.FREQUENCIA_PORTADORA/config.TAXA_BITS}")
            Ciclos/bit: 4.0
        """
        if frequencia < 10:
            raise ValueError("Frequência mínima da portadora é 10 Hz")
        if frequencia > 1000:
            raise ValueError("Frequência máxima da portadora é 1000 Hz")
        self.FREQUENCIA_PORTADORA = frequencia
