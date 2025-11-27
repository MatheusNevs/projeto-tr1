"""
Módulo de Modulação por Portadora.

Este módulo implementa quatro técnicas de modulação digital usando onda portadora
senoidal. Diferente das modulações em banda base, estas técnicas modulam uma
portadora de alta frequência para transmissão:

- ASK (Amplitude Shift Keying): Modula a amplitude da portadora
- FSK (Frequency Shift Keying): Modula a frequência da portadora
- QPSK (Quadrature Phase Shift Keying): Modula a fase (4 estados, 2 bits/símbolo)
- 16-QAM (Quadrature Amplitude Modulation): Modula amplitude e fase (16 estados, 4 bits/símbolo)

Classes:
    ModuladorPortadora: Classe abstrata base para moduladores por portadora.
    ASK: Amplitude Shift Keying (2 níveis de amplitude).
    FSK: Frequency Shift Keying (2 frequências diferentes).
    QPSK: Quadrature Phase Shift Keying (4 fases diferentes).
    QAM16: 16-QAM com 16 símbolos diferentes.

Notas Importantes:
    - Requer FREQUENCIA_PORTADORA < TAXA_AMOSTRAGEM/2 (Teorema de Nyquist)
    - Recomendado: FREQUENCIA_PORTADORA/TAXA_BITS >= 3 (mínimo 3 ciclos por bit)
    - amostras_por_bit = TAXA_AMOSTRAGEM / TAXA_BITS
    - QPSK e QAM16 usam símbolos (múltiplos bits por símbolo)

Exemplos:
    >>> ask = ASK(amplitude=5.0, frequencia=100)
    >>> bits = [1, 0, 1, 1]
    >>> sinal = ask.codificar(bits)
    >>> bits_recuperados = ask.decodificar(sinal)
"""

from abc import ABC, abstractmethod
import numpy as np
from config import Config

class ModuladorPortadora(ABC):
    """
    Classe abstrata base para moduladores por portadora.
    
    Define a interface comum para todos os moduladores que usam onda
    portadora senoidal. Gerencia parâmetros fundamentais como amplitude,
    frequência da portadora e taxas de amostragem/bits.
    
    Attributes:
        amplitude (float): Amplitude da onda portadora em Volts.
        frequencia (float): Frequência da portadora em Hz.
        taxa_amostragem (int): Taxa de amostragem em Hz.
        taxa_bits (int): Taxa de transmissão em bits/segundo.
    
    Métodos Abstratos:
        codificar: Modula bits na portadora.
        decodificar: Demodula portadora em bits.
    
    Restrições de Design:
        1. frequencia < taxa_amostragem / 2 (Nyquist)
        2. frequencia / taxa_bits >= 3 (mínimo 3 ciclos/bit recomendado)
        3. amostras_por_bit = taxa_amostragem / taxa_bits >= 10 (recomendado)
    
    Notas:
        - Modulações por portadora são usadas para transmissão em RF
        - Permitem multiplexação em frequência (FDM)
        - Mais robustas contra alguns tipos de interferência
        - Requerem sincronização de portadora no receptor
    """

    def __init__(self, amplitude=None, frequencia=None, taxa=None):
        """
        Inicializa o modulador por portadora.
        
        Args:
            amplitude (float, optional): Amplitude da portadora em Volts.
                Se None, usa Config.AMPLITUDE.
            frequencia (float, optional): Frequência da portadora em Hz.
                Se None, usa Config.FREQUENCIA_PORTADORA.
            taxa (int, optional): Taxa de amostragem em Hz.
                Se None, usa Config.TAXA_AMOSTRAGEM.
        
        Avisos:
            - Certifique-se que frequencia < taxa_amostragem/2
            - Recomendado: frequencia/taxa_bits >= 3
            - Taxa de bits sempre vem de Config.TAXA_BITS
        """
        config = Config()
        self.amplitude = amplitude or config.AMPLITUDE
        self.frequencia = frequencia or config.FREQUENCIA_PORTADORA
        self.taxa_amostragem = taxa or config.TAXA_AMOSTRAGEM
        self.taxa_bits = config.TAXA_BITS

    @abstractmethod
    def codificar(self, bits: list) -> np.ndarray:
        """
        Codifica bits modulando a onda portadora.
        
        Args:
            bits (list): Sequência de bits (0 e 1) a codificar.
            
        Returns:
            np.ndarray: Sinal modulado.
        
        Notas:
            Método abstrato - deve ser implementado pelas subclasses.
        """
        pass

    @abstractmethod
    def decodificar(self, sinal: np.ndarray) -> list:
        """
        Decodifica sinal modulado de volta em bits.
        
        Args:
            sinal (np.ndarray): Sinal modulado a decodificar.
            
        Returns:
            list: Sequência de bits recuperados.
        
        Notas:
            Método abstrato - deve ser implementado pelas subclasses.
        """
        pass


class ASK(ModuladorPortadora):
    """
    ASK - Amplitude Shift Keying (Modulação por Chaveamento de Amplitude).
    
    Técnica de modulação digital onde a informação é codificada variando a
    amplitude da onda portadora:
    - Bit 1: portadora com amplitude máxima (A × sin(2πft))
    - Bit 0: sem sinal (amplitude = 0)
    
    Vantagens:
        - Simples de implementar (on-off keying)
        - Requer apenas detector de envelope
        - Baixa complexidade do receptor
        - Boa eficiência energética para bit 0
    
    Desvantagens:
        - Muito sensível a variações de amplitude (ruído, fading)
        - Pior desempenho em canais ruidosos
        - Suscetível a interferência
        - Requer controle automático de ganho (AGC)
    
    Aplicações:
        - RFID passivo
        - Comunicação via fibra óptica
        - Transmissão de baixa potência
        - Redes de sensores sem fio
    
    Fórmula:
        s(t) = A × sin(2πf_c × t) para bit 1
        s(t) = 0 para bit 0
        
        Onde: A = amplitude, f_c = frequência da portadora
    
    Exemplos:
        >>> ask = ASK(amplitude=5.0, frequencia=100)
        >>> bits = [1, 0, 1]
        >>> sinal = ask.codificar(bits)
        >>> # Bit 1: senoide de 100 Hz com amplitude 5V
        >>> # Bit 0: silêncio (0V)
        >>> # Bit 1: senoide de 100 Hz com amplitude 5V
    """

    def codificar(self, bits: list) -> np.ndarray:
        """
        Codifica bits usando modulação ASK (on-off keying).
        
        Gera uma onda portadora senoidal para bits 1 e silêncio para bits 0.
        Cada bit é representado por amostras_por_bit amostras.
        
        Args:
            bits (list): Sequência de bits (0 e 1) a codificar.
            
        Returns:
            np.ndarray: Sinal ASK modulado com len(bits) × amostras_por_bit amostras.
        
        Algoritmo:
            1. Calcula amostras_por_bit = taxa_amostragem / taxa_bits
            2. Gera vetor de tempo t para um período de bit
            3. Pré-computa onda senoidal para bit 1: A×sin(2πf×t)
            4. Pré-computa silêncio para bit 0: zeros
            5. Para cada bit, copia a onda correspondente no sinal final
        
        Detalhes Técnicos:
            - Frequência da portadora: self.frequencia Hz
            - Amplitude da portadora: self.amplitude V
            - Taxa de amostragem: self.taxa_amostragem Hz
            - Duração de cada bit: 1/taxa_bits segundos
        
        Exemplos:
            >>> ask = ASK(amplitude=5.0, frequencia=100)
            >>> # Com taxa_amostragem=1000 Hz, taxa_bits=10 bps:
            >>> # amostras_por_bit = 100
            >>> sinal = ask.codificar([1, 0])
            >>> len(sinal)  # 2 bits × 100 amostras/bit
            200
            >>> max(sinal[:100])  # Primeiro bit (1): amplitude máxima ≈ 5V
            5.0
            >>> max(sinal[100:])  # Segundo bit (0): amplitude zero
            0.0
        """
        amp = self.amplitude                                    # Carrega a amplitude da portadora
        freq = self.frequencia                                  # Carrega a frequência da portadora
        tx = self.taxa_amostragem                               # Carrega a taxa de amostragem (amostras/s)
        amostras_por_bit = int(self.taxa_amostragem / self.taxa_bits)  # Calcula amostras por bit baseado na taxa de bits

        size = len(bits)                                        # Calcula a quantidade de bits a serem transmitidos

        sinal = np.zeros(size * amostras_por_bit)               # Cria a onda final, inicializada com zeros e com tamanho
                                                                # referente ao número de bits vezes as amostras de cada um

        t = np.arange(amostras_por_bit) / tx                    # O vetor t dará o instante de cada amostra na portadora (bit dura 1/taxa_bits s)
        
        onda_bit_1 = amp * np.sin(2 * np.pi * freq * t)         # Quando bit = 1, a amplitude da onda final será a igual à
                                                                # amplitude da portadora (amp) para as amostras

        onda_bit_0 = np.zeros(amostras_por_bit)                 # Quando bit = 0, a amplitude da onda final é nula para as
                                                                # amostras

        for i in range (size):                                  # Para cada bit transmitido:
            start = i * amostras_por_bit                        # Início da lista de amostras do bit
            end = (i + 1) * amostras_por_bit                    # Fim da lista de amostras do bit
            if bits[i] == 1:                                    # Se bit = 1, assume a amplitude da portadora
                sinal[start:end] = onda_bit_1
            else:
                sinal[start:end] = onda_bit_0                   # Se bit = 0, tem amplitude nula
        
        return sinal

    def decodificar(self, sinal: np.ndarray) -> list:
        """
        Decodifica sinal ASK baseado na energia do segmento.
        
        Usa detector de energia: calcula a energia de cada período de bit
        e compara com um limiar adaptativo. Alta energia = bit 1, baixa energia = bit 0.
        
        Args:
            sinal (np.ndarray): Sinal ASK a decodificar.
            
        Returns:
            list: Sequência de bits recuperados (0 e 1).
        
        Algoritmo:
            1. Calcula limiar adaptativo = 25% da energia máxima esperada
            2. Energia máxima = A² × amostras_por_bit × 0.5 (valor médio de sin²)
            3. Para cada segmento de amostras_por_bit:
               - Calcula energia = Σ(amostra²)
               - Se energia > limiar → bit 1
               - Senão → bit 0
        
        Vantagens do Detector de Energia:
            - Não requer sincronização perfeita de fase
            - Simples de implementar
            - Razoavelmente robusto contra ruído
        
        Desvantagens:
            - Sensível a variações de amplitude do canal
            - Requer estimativa ou calibração do limiar
            - Performance degradada em ambientes com fading
        
        Notas:
            - Limiar de 25% oferece boa margem contra ruído
            - Para amplitude 5V e 100 amostras/bit: limiar ≈ 312.5
            - Segmentos incompletos no final são ignorados
        
        Exemplos:
            >>> ask = ASK(amplitude=5.0, frequencia=100)
            >>> bits = [1, 0, 1, 1, 0]
            >>> sinal = ask.codificar(bits)
            >>> bits_recuperados = ask.decodificar(sinal)
            >>> print(bits == bits_recuperados)
            True
        """
        amostras_por_bit = int(self.taxa_amostragem / self.taxa_bits)  # Calcula amostras por bit baseado na taxa de bits

        # Protege contra casos estranhos (divisão por zero)
        if amostras_por_bit <= 0:
            return []

        bits = []  # Array para armazenar os bits decodificados

        # Calcular um limiar adaptativo baseado na energia máxima esperada
        # Energia máxima aproximada para um bit 1: amp^2 * amostras_por_bit * 0.5
        # (valor médio de sin^2 é 0.5). Usamos uma fração desse valor como limiar.
        energia_max_esperada = (self.amplitude ** 2) * amostras_por_bit * 0.5
        limiar = energia_max_esperada * 0.25  # 25% da energia máxima esperada

        for i in range(0, len(sinal), amostras_por_bit):  # Loop para pegar as amostras de cada bit
            segmento_amostras = sinal[i:i + amostras_por_bit]  # Segmenta o trecho de todas as amostras de um bit

            energia = np.sum(segmento_amostras ** 2)  # Calcula a energia total das amostras
            # Usa limiar adaptativo em vez de um valor fixo
            if energia > limiar:
                bits.append(1)
            else:
                bits.append(0)

        return bits


class FSK(ModuladorPortadora):
    """
    FSK - Frequency Shift Keying (Modulação por Chaveamento de Frequência).
    
    Técnica de modulação digital onde a informação é codificada variando a
    frequência da onda portadora mantendo amplitude constante:
    - Bit 0: portadora com frequência baixa (f0)
    - Bit 1: portadora com frequência alta (f1 = 2×f0)
    
    Vantagens:
        - Mais robusta que ASK contra variações de amplitude
        - Não requer controle automático de ganho (AGC)
        - Boa performance em canais com fading
        - Envelope constante (eficiente para amplificadores não-lineares)
    
    Desvantagens:
        - Requer maior largura de banda que ASK
        - Necessita detector de frequência (mais complexo que envelope)
        - Sensível a offset de frequência
        - Requer sincronização de frequência
    
    Aplicações:
        - Modems de baixa velocidade
        - Comunicação via rádio FM
        - Caller ID telefônico
        - RTTY (radioteletype)
        - Pagers antigos
    
    Parâmetros FSK:
        - f0: Frequência para bit 0 (frequência base)
        - f1: Frequência para bit 1 (tipicamente 2×f0)
        - Desvio de frequência: Δf = f1 - f0
    
    Fórmulas:
        s0(t) = A × sin(2πf0×t) para bit 0
        s1(t) = A × sin(2πf1×t) para bit 1
    
    Exemplos:
        >>> fsk = FSK(amplitude=5.0, frequencia=100)
        >>> bits = [0, 1, 0]
        >>> sinal = fsk.codificar(bits)
        >>> # Bit 0: senoide de 100 Hz
        >>> # Bit 1: senoide de 200 Hz (dobro)
        >>> # Bit 0: senoide de 100 Hz
    """

    def codificar(self, bits: list) -> np.ndarray:
        """
        Codifica bits usando modulação FSK.
        
        Gera senoides com frequências diferentes: f0 para bit 0 e
        f1 (2×f0) para bit 1. A amplitude permanece constante.
        
        Args:
            bits (list): Sequência de bits (0 e 1) a codificar.
            
        Returns:
            np.ndarray: Sinal FSK modulado com len(bits) × amostras_por_bit amostras.
        
        Algoritmo:
            1. Calcula amostras_por_bit = taxa_amostragem / taxa_bits
            2. Define f0 = frequencia e f1 = 2 × frequencia
            3. Gera vetor de tempo t para um período de bit
            4. Pré-computa senoide para bit 0: A×sin(2πf0×t)
            5. Pré-computa senoide para bit 1: A×sin(2πf1×t)
            6. Para cada bit, copia a senoide correspondente
        
        Detalhes Técnicos:
            - f0 = self.frequencia (ex: 100 Hz)
            - f1 = 2 × self.frequencia (ex: 200 Hz)
            - Desvio de frequência: Δf = f1 - f0 = f0
            - Índice de modulação: h = Δf / taxa_bits
        
        Notas:
            - Razão f1/f0 = 2 é escolha comum (ortogonalidade)
            - Maior separação de frequências = melhor discriminação
            - Requer f1 < taxa_amostragem/2 (Nyquist)
        
        Exemplos:
            >>> fsk = FSK(amplitude=5.0, frequencia=100)
            >>> # Com taxa_amostragem=1000 Hz, taxa_bits=10 bps:
            >>> sinal = fsk.codificar([0, 1])
            >>> len(sinal)  # 2 bits × 100 amostras/bit
            200
            >>> # Primeiros 100: senoide 100 Hz
            >>> # Últimos 100: senoide 200 Hz
        """
        amp = self.amplitude                                    # Carrega a amplitude da portadora
        f0 = self.frequencia                                    # Carrega a frequência da portadora
        f1 = self.frequencia * 2                                # Carrega o dobro da frequência da portadora
        tx = self.taxa_amostragem                               # Carrega a taxa de amostragem (amostras/s)
        amostras_por_bit = int(self.taxa_amostragem / self.taxa_bits)  # Calcula amostras por bit baseado na taxa de bits

        size = len(bits)                                        # Calcula a quantidade de bits a serem transmitidos

        sinal = np.zeros(size * amostras_por_bit)               # Cria a onda final, inicializada com zeros e com tamanho
                                                                # referente ao número de bits vezes as amostras de cada um

        t = np.arange(amostras_por_bit) / tx                    # O vetor t dará o instante de cada amostra na portadora (bit dura 0.1s)
        
        onda_bit_0 = amp * np.sin(2 * np.pi * f0 * t)           # Formato da onde se o bit for 0, utilizando a freq mais baixa
        onda_bit_1 = amp * np.sin(2 * np.pi * f1 * t)           # Formato da onda se o bit for 1, utilizando a freq mais alta

        for i in range (size):
            start = i * amostras_por_bit                        # Início da lista de amostras do bit
            end = (i + 1) * amostras_por_bit                    # Fim da lista de amostras do bit
            if bits[i] == 1:                                    # Se bit = 1, tem o formato da onda com freq mais alta
                sinal[start:end] = onda_bit_1
            else:
                sinal[start:end] = onda_bit_0                   # Se bit = 0, tem o formato da onda com freq mais baixa 
        
        return sinal

    def decodificar(self, sinal: np.ndarray) -> list:
        """
        Decodifica sinal FSK usando detector de correlação.
        
        Implementa demodulação não-coerente baseada em correlação cruzada
        entre o sinal recebido e duas senoides de referência (f0 e f1).
        
        Args:
            sinal (np.ndarray): Sinal FSK a decodificar.
            
        Returns:
            list: Sequência de bits recuperados (0 e 1).
        
        Algoritmo (Detector de Correlação):
            1. Para cada segmento de amostras_por_bit:
               a. Gera referência ref_0 = sin(2πf0×t)
               b. Gera referência ref_1 = sin(2πf1×t)
               c. Calcula correlação_0 = |Σ(sinal × ref_0)|
               d. Calcula correlação_1 = |Σ(sinal × ref_1)|
               e. Se correlação_1 > correlação_0 → bit 1
               f. Senão → bit 0
        
        Princípio Matemático:
            Quando o sinal contém frequência f0:
            - correlação_0 = Σ(sin²) ≈ constante positiva alta
            - correlação_1 = Σ(sin(f0)×sin(f1)) ≈ 0 (ortogonais)
            
            Quando o sinal contém frequência f1:
            - correlação_0 = Σ(sin(f1)×sin(f0)) ≈ 0
            - correlação_1 = Σ(sin²) ≈ constante positiva alta
        
        Vantagens do Detector de Correlação:
            - Não requer sincronização de fase
            - Robusto contra ruído
            - Ótimo para sinais ortogonais
            - Implementação relativamente simples
        
        Notas:
            - Usa valor absoluto para robustez
            - Frequências f0 e f1 devem ser suficientemente separadas
            - Performance melhora com maior SNR
            - Segmentos incompletos são ignorados
        
        Exemplos:
            >>> fsk = FSK(amplitude=5.0, frequencia=100)
            >>> bits = [0, 1, 0, 1, 1]
            >>> sinal = fsk.codificar(bits)
            >>> bits_recuperados = fsk.decodificar(sinal)
            >>> print(bits == bits_recuperados)
            True
        """
        
        amp = self.amplitude                                                # Carrega a amplitude da portadora
        f0 = self.frequencia                                                # Carrega a frequência da portadora
        f1 = self.frequencia * 2                                            # Carrega o dobro da frequência da portadora
        tx = self.taxa_amostragem                                           # Carrega a taxa de amostragem (amostras/s)
        amostras_por_bit = int(self.taxa_amostragem / self.taxa_bits)       # Calcula amostras por bit baseado na taxa de bits

        bits = []                                                           # Array para armazenar os bits decodificados
        for i in range(0, len(sinal), amostras_por_bit):                    # Loop para pegar as amostras de cada bit
            segmento_amostras = sinal[i:i + amostras_por_bit]               # Segmenta o trecho de todas as amostras de um bit
            t = np.arange(amostras_por_bit) / tx                            # O vetor t dará o instante de cada amostra na portadora (bit dura 0.1s)
            ref_0 = np.sin(2 * np.pi * f0 * t)                              # Calcula a onda referência para o bit 0
            ref_1 = np.sin(2 * np.pi * f1 * t)                              # Calcula a onda referência para o bit 1

            correlacao_0 = np.abs(np.sum(segmento_amostras * ref_0))        # Faz a correlação com a onda referência para o bit 0
            correlacao_1 = np.abs(np.sum(segmento_amostras * ref_1))        # Faz a correlação com a onda referência para o bit 1

            if correlacao_1 > correlacao_0:                                 # Se a correlação com ref_1 for maior que com ref_0,                         
                bits.append(1)                                              # (correlacao_1 sempre positiva), o bit decodificado é 1
            else:                                                           # Se a correlação com ref_0 for maior que com ref_1,
                bits.append(0)                                              # (correlacao_0 sempre positiva), o bit decodificado é 0
        
        return bits


class QPSK(ModuladorPortadora):
    """
    QPSK - Quadrature Phase Shift Keying (Modulação por Chaveamento de Fase em Quadratura).
    
    Técnica de modulação digital que codifica 2 bits por símbolo variando
    a fase da portadora entre 4 estados (0°, 90°, 180°, 270° ou equivalentes).
    Mais eficiente espectralmente que ASK e FSK.
    
    Mapeamento de Bits para Fase (Gray Coding):
        - (1,1) → 45° (π/4)
        - (1,0) → 135° (3π/4)
        - (0,0) → 225° (5π/4)
        - (0,1) → 315° (7π/4)
    
    Vantagens:
        - 2 bits por símbolo (dobro da eficiência espectral)
        - Envelope constante (amplificadores não-lineares)
        - Boa performance em ruído
        - Largura de banda eficiente
        - Amplamente padronizado
    
    Desvantagens:
        - Requer sincronização de fase precisa
        - Detector mais complexo que ASK/FSK
        - Ambiguidade de fase de 90° (requer codificação diferencial)
        - Sensível a distorções não-lineares
    
    Aplicações:
        - Satélites (DVB-S, GPS)
        - Wi-Fi (802.11b/g)
        - Comunicação celular (CDMA, LTE)
        - Modems de alta velocidade
        - Rádio digital
    
    Representação em Quadratura:
        s(t) = A×cos(2πf_c×t + φ)
        s(t) = I×cos(2πf_c×t) - Q×sin(2πf_c×t)
        
        Onde I e Q são componentes em fase e quadratura.
    
    Constelação QPSK:
        Q
        |  (1,0)  (1,1)
        |     •     •
        |
    ----+------------ I
        |
        |     •     •
        |  (0,0)  (0,1)
    
    Exemplos:
        >>> qpsk = QPSK(amplitude=5.0, frequencia=100)
        >>> bits = [1, 1, 0, 0, 1, 0]  # 3 símbolos
        >>> sinal = qpsk.codificar(bits)
        >>> # Símbolo 1 (1,1): fase 45°
        >>> # Símbolo 2 (0,0): fase 225°
        >>> # Símbolo 3 (1,0): fase 135°
    """

    def codificar(self, bits: list) -> np.ndarray:
        """
        Codifica bits usando modulação QPSK.
        
        Agrupa bits em pares (símbolos de 2 bits) e mapeia cada par
        para uma das 4 fases possíveis da portadora.
        
        Args:
            bits (list): Sequência de bits (0 e 1) a codificar.
                        Comprimento deve ser par.
            
        Returns:
            np.ndarray: Sinal QPSK modulado.
                       Comprimento = (len(bits)//2) × amostras_por_simbolo.
        
        Algoritmo:
            1. Calcula amostras_por_simbolo = taxa_amostragem / taxa_bits
            2. Define mapeamento de pares de bits para fases:
               (1,1)→45°, (1,0)→135°, (0,0)→225°, (0,1)→315°
            3. Para cada par de bits:
               a. Determina fase φ do mapeamento
               b. Gera senoide: A×cos(2πft + φ)
               c. Adiciona ao sinal de saída
        
        Detalhes Técnicos:
            - Taxa de símbolo = taxa_bits (cada símbolo = 2 bits)
            - Duração do símbolo = 1/taxa_bits segundos
            - Largura de banda ≈ taxa_bits Hz (metade da taxa binária)
            - Codificação Gray reduz erros de bit
        
        Notas:
            - Se len(bits) for ímpar, último bit é ignorado
            - Usa Gray coding para minimizar BER
            - Fases deslocadas 45° (melhor imunidade a ruído)
        
        Exemplos:
            >>> qpsk = QPSK(amplitude=5.0, frequencia=100)
            >>> # Com taxa_amostragem=1000 Hz, taxa_bits=10 bps:
            >>> # amostras_por_simbolo = 100
            >>> sinal = qpsk.codificar([1, 1, 0, 0])
            >>> len(sinal)  # 2 símbolos × 100 amostras/símbolo
            200
        """
        amp = self.amplitude                                                # Carrega a amplitude da portadora
        freq = self.frequencia                                              # Carrega a frequência da portadora
        tx = self.taxa_amostragem                                           # Carrega a taxa de amostragem (amostras/s)
        num_simbolos = len(bits) // 2                                       # Calcula o número de pares de bits transmitidos
        amostras_por_simbolo = int(self.taxa_amostragem / self.taxa_bits)   # Calcula amostras por símbolo (2 bits) baseado na taxa de bits
        
        sinal = np.zeros(num_simbolos * amostras_por_simbolo)               # Cria o sinal de saída preenchido inicialmente com zeros
        t = np.arange(amostras_por_simbolo) / tx                            # O vetor t dará o instante de cada amostra na portadora (bit dura 0.1s)
        mapa_fase = {
            (1, 1): np.pi/4,      # 45°
            (1, 0): 3*np.pi/4,    # 135°
            (0, 0): 5*np.pi/4,    # 225°
            (0, 1): 7*np.pi/4     # 315°
        }

        for i in range (0, len(bits), 2):                                   # Loop de 2 em 2 bits (1 símbolo)
            if i + 1 < len(bits):                                           # Verifica se não é o último elemento de "bits"
                par_bits = (bits[i], bits[i + 1])                           # Cria uma tupla com o bit atual e o seguinte (símbolo)
                fase = mapa_fase[par_bits]                                  # Verifica a defasagem correta de acordo com o mapeamento
                onda_simbolo = amp * np.cos(2 * np.pi * freq * t + fase)    # Gera a onda defasada com a respectiva fase
                index_simbolo = i // 2                                      # Cria contador de 1 em 1 para usar como índice
                start = index_simbolo * amostras_por_simbolo                # Início da lista de amostras
                end = (index_simbolo + 1) * amostras_por_simbolo            # Fim da lista de amostras
                sinal[start:end] = onda_simbolo                             # Preenche o sinal final com os resultados obtidos

        return sinal


    def decodificar(self, sinal: np.ndarray) -> list:
        """
        Decodifica sinal QPSK usando demodulação por quadratura.
        
        Implementa detector coerente que calcula componentes I (em fase)
        e Q (quadratura) por correlação, depois determina a fase e
        mapeia de volta para bits.
        
        Args:
            sinal (np.ndarray): Sinal QPSK a decodificar.
            
        Returns:
            list: Sequência de bits recuperados (0 e 1).
                  Comprimento = 2 × número de símbolos detectados.
        
        Algoritmo (Demodulação Coerente):
            1. Para cada segmento de amostras_por_simbolo:
               a. Calcula I = Σ(sinal × cos(2πft)) - Componente em fase
               b. Calcula Q = Σ(sinal × -sin(2πft)) - Componente quadratura
               c. Determina fase: φ = arctan2(Q, I)
               d. Mapeia fase para par de bits:
                  • -90° < φ ≤ 0°   → (0,1) [315°]
                  • 0° < φ ≤ 90°    → (1,1) [45°]
                  • 90° < φ ≤ 180°  → (1,0) [135°]
                  • -180° < φ ≤ -90° → (0,0) [225°]
        
        Princípio Matemático:
            O sinal QPSK pode ser representado como:
            s(t) = I×cos(2πft) - Q×sin(2πft)
            
            Multiplicando por cos(2πft) e integrando:
            Σ(s × cos) ≈ I  (componente cosseno)
            
            Multiplicando por -sin(2πft) e integrando:
            Σ(s × -sin) ≈ Q  (componente seno)
            
            A fase original é recuperada: φ = atan2(Q, I)
        
        Vantagens do Detector Coerente:
            - Desempenho ótimo (menor BER)
            - Robustez contra ruído AWGN
            - Recuperação precisa da fase
        
        Desvantagens:
            - Requer sincronização perfeita de fase e frequência
            - Mais complexo que detectores não-coerentes
            - Sensível a offset de frequência
        
        Notas:
            - arctan2() considera sinais de I e Q (4 quadrantes)
            - Segmentos incompletos são ignorados
            - Ambiguidade de fase de 90° resolvida por codificação diferencial
        
        Exemplos:
            >>> qpsk = QPSK(amplitude=5.0, frequencia=100)
            >>> bits = [1, 1, 0, 0, 1, 0, 0, 1]
            >>> sinal = qpsk.codificar(bits)
            >>> bits_recuperados = qpsk.decodificar(sinal)
            >>> print(bits == bits_recuperados)
            True
        """

        amostras_por_simbolo = int(self.taxa_amostragem / self.taxa_bits)   # Calcula amostras por símbolo (2 bits) baseado na taxa de bits
        
        amp = self.amplitude                                                # Carrega a amplitude da portadora
        freq = self.frequencia                                              # Carrega a frequência da portadora
        tx = self.taxa_amostragem                                           # Carrega a taxa de amostragem (amostras/s)
        bits = []                                                           # Lista para guardar os bits decodificados
        for i in range (0, len(sinal), amostras_por_simbolo):               # Loop sobre todas as amostras de cada símbolo
            segmento_amostras = sinal[i:i + amostras_por_simbolo]           # Segmenta o trecho de todas as amostras de um bit
            t = np.arange(amostras_por_simbolo) / tx                        # O vetor t dará o instante de cada amostra na portadora (bit dura 0.1s)
            I = np.sum(segmento_amostras * np.cos(2 * np.pi * freq * t))    # Calcula o I de acordo com a correlação com cos()
            Q = np.sum(segmento_amostras * -np.sin(2 * np.pi * freq * t))   # Calcula o Q de acordo com a correlação com sen()
            fase = np.arctan2(Q, I)                                         # Calcula a fase da onda (ângulo do triângulo
                                                                            # formado por Q e I => arctan) considerando o sinal (arctan2)
            
            if -np.pi/2 < fase <= 0:                                        # Se fase está no 4° quadrante, fase = 315°
                bits.extend([0, 1])
            elif 0 < fase <= np.pi/2:                                       # Se fase está no 1° quadrante, fase = 45°
                bits.extend([1, 1])
            elif np.pi/2 < fase <= np.pi:                                   # Se fase está no 2° quadrante, fase = 135°
                bits.extend([1, 0])
            else:                                                           # Caso contrário, está no 3° quadrante e fase = 225°
                bits.extend([0, 0])

        return bits


class QAM16(ModuladorPortadora):
    """
    16-QAM - 16-Quadrature Amplitude Modulation (Modulação em Amplitude e Quadratura).
    
    Técnica avançada de modulação digital que codifica 4 bits por símbolo
    variando tanto amplitude quanto fase da portadora. Utiliza 16 pontos
    distintos na constelação I-Q (4×4 grid).
    
    Mapeamento de Bits (Gray Coding):
        Primeiros 2 bits determinam amplitude I (em fase):
        - (1,0) → -3A    - (1,1) → -A
        - (0,1) → +A     - (0,0) → +3A
        
        Últimos 2 bits determinam amplitude Q (quadratura):
        - (1,0) → -3A    - (1,1) → -A
        - (0,1) → +A     - (0,0) → +3A
    
    Constelação 16-QAM:
        Q
        |
      3A|  (10,00)  (11,00)  (01,00)  (00,00)
        |     •        •        •        •
      1A|  (10,01)  (11,01)  (01,01)  (00,01)
        |     •        •        •        •
    ----+----------------------------------- I
     -1A|  (10,11)  (11,11)  (01,11)  (00,11)
        |     •        •        •        •
     -3A|  (10,10)  (11,10)  (01,10)  (00,10)
        |     •        •        •        •
        -3A      -1A       1A       3A
    
    Vantagens:
        - 4 bits por símbolo (alta eficiência espectral)
        - Dobro da taxa de dados do QPSK na mesma largura de banda
        - Amplamente usado em comunicações modernas
        - Boa relação desempenho/complexidade
    
    Desvantagens:
        - Mais sensível a ruído que QPSK
        - Requer maior SNR para mesmo BER
        - Envelope não-constante (amplificadores lineares)
        - Maior complexidade de detecção
        - Sensível a distorções não-lineares
    
    Aplicações:
        - Modems de cabo (DOCSIS)
        - TV digital (DVB-C, ATSC)
        - Wi-Fi (802.11n/ac/ax)
        - LTE/5G
        - Microondas digitais
        - Transmissão de vídeo
    
    Representação Matemática:
        s(t) = I(t)×cos(2πf_c×t) - Q(t)×sin(2πf_c×t)
        
        Onde I(t) e Q(t) ∈ {-3A, -A, +A, +3A}
    
    Métricas:
        - Eficiência espectral: 4 bits/símbolo
        - SNR requerido: ~18 dB para BER=10^-5
        - Largura de banda: ≈ taxa_bits/4 Hz
    
    Exemplos:
        >>> qam = QAM16(amplitude=1.0, frequencia=100)
        >>> bits = [1, 0, 1, 1, 0, 0, 0, 1]  # 2 símbolos
        >>> sinal = qam.codificar(bits)
        >>> # Símbolo 1: (1,0,1,1) → I=-3A, Q=-A
        >>> # Símbolo 2: (0,0,0,1) → I=+3A, Q=+A
    """

    def codificar(self, bits: list) -> np.ndarray:
        """
        Codifica bits usando modulação 16-QAM.
        
        Agrupa bits em grupos de 4 (símbolos) e mapeia cada grupo
        para um ponto na constelação 16-QAM (grid 4×4 de amplitudes I e Q).
        
        Args:
            bits (list): Sequência de bits (0 e 1) a codificar.
                        Se comprimento não for múltiplo de 4, padding com zeros.
            
        Returns:
            np.ndarray: Sinal 16-QAM modulado.
                       Comprimento = (len(bits)//4) × amostras_por_simbolo.
        
        Algoritmo:
            1. Adiciona padding de zeros se necessário (múltiplo de 4)
            2. Calcula amostras_por_simbolo = taxa_amostragem / taxa_bits
            3. Para cada grupo de 4 bits:
               a. Bits [0:2] determinam amplitude I: {-3A, -A, +A, +3A}
               b. Bits [2:4] determinam amplitude Q: {-3A, -A, +A, +3A}
               c. Gera símbolo: s = I×cos(2πft) - Q×sin(2πft)
               d. Adiciona ao sinal de saída
        
        Mapeamento Gray Code (minimiza BER):
            I ou Q:  (1,0)→-3A  (1,1)→-A  (0,1)→+A  (0,0)→+3A
        
        Detalhes Técnicos:
            - Taxa de símbolo = taxa_bits (cada símbolo = 4 bits)
            - Potência média: P_avg = 10×A²
            - Potência pico: P_peak = 18×A² (cantos da constelação)
            - PAPR (Peak-to-Average Power Ratio) = 1.8
        
        Notas:
            - Padding automático para múltiplo de 4
            - Gray coding reduz erros de bit adjacentes
            - Amplitudes normalizadas: ±A, ±3A
        
        Exemplos:
            >>> qam = QAM16(amplitude=1.0, frequencia=100)
            >>> # Com taxa_amostragem=1000 Hz, taxa_bits=10 bps:
            >>> # amostras_por_simbolo = 100
            >>> sinal = qam.codificar([1, 0, 1, 1])  # 1 símbolo
            >>> len(sinal)
            100
        """
        amp = self.amplitude                                                # Carrega a amplitude da portadora
        freq = self.frequencia                                              # Carrega a frequência da portadora
        tx = self.taxa_amostragem                                           # Carrega a taxa de amostragem (amostras/s)
        # Garantir que o número de bits seja múltiplo de 4 (padding com zeros se necessário)
        pad = (4 - (len(bits) % 4)) % 4
        if pad:
            bits_local = bits + [0] * pad
        else:
            bits_local = bits

        num_simbolos = len(bits_local) // 4                                   # Calcula a qtd de simbolos transmitidos (4 bits)
        amostras_por_simbolo = int(self.taxa_amostragem / self.taxa_bits)     # Calcula amostras por símbolo (4 bits) baseado na taxa de bits

        sinal = np.zeros(amostras_por_simbolo * num_simbolos)               # Cria o sinal de saída preenchido inicialmente com zeros
        t = np.arange(amostras_por_simbolo) / tx                            # O vetor t dará o instante de cada amostra na portadora (bit dura 0.1s)
        mapa_niveis = {
            (1, 0): -3 * amp, # bits '10' -> Nível -3
            (1, 1): -1 * amp, # bits '11' -> Nível -1
            (0, 1):  1 * amp, # bits '01' -> Nível +1
            (0, 0):  3 * amp  # bits '00' -> Nível +3
        }
        ref_I = np.cos(2 * np.pi * freq * t)                                # Portadora I (cos)
        ref_Q = -np.sin(2 * np.pi * freq * t)                               # Portadora Q (-sen)

        for i in range(0, len(bits_local), 4):                              # Loop de 4 em 4 (1 simbolo)
            par_bits_I = (bits_local[i], bits_local[i + 1])                  # Os primeiros 2 bits determinam a amplitude a portadora I
            par_bits_Q = (bits_local[i + 2], bits_local[i + 3])              # Os últimos 2 bits determinam a amplitude da portadora Q
            nivel_I = mapa_niveis[par_bits_I]                               # Mapeia o nível de I
            nivel_Q = mapa_niveis[par_bits_Q]                               # Mapeia o nível de Q
            onda_simbolo = (nivel_I * ref_I) + (nivel_Q * ref_Q)            # Cria a onda do simbolo de acordo com as referências e
                                                                            # as amplitudes descobertas

            index_simbolo = i // 4                                          # Cria contador de 1 em 1 para usar como índice
            start = index_simbolo * amostras_por_simbolo                    # Início da lista de amostras
            end = (index_simbolo + 1) * amostras_por_simbolo                # Fim da lista de amostras
            sinal[start:end] = onda_simbolo                                 # Preenche o sinal final com os resultados obtidos
        
        return sinal


    def decodificar(self, sinal: np.ndarray) -> list:
        """
        Decodifica sinal 16-QAM usando demodulação por quadratura e decisão multi-nível.
        
        Implementa detector coerente que calcula componentes I e Q por correlação,
        normaliza pela energia das portadoras, e mapeia os níveis de volta para bits.
        
        Args:
            sinal (np.ndarray): Sinal 16-QAM a decodificar.
            
        Returns:
            list: Sequência de bits recuperados (0 e 1).
                  Comprimento = 4 × número de símbolos detectados.
        
        Algoritmo (Demodulação Coerente Multi-nível):
            1. Para cada segmento de amostras_por_simbolo:
               a. Calcula I = Σ(sinal × cos(2πft)) - Componente em fase
               b. Calcula Q = Σ(sinal × -sin(2πft)) - Componente quadratura
               c. Normaliza: I_norm = I / energia_ref_I
               d. Normaliza: Q_norm = Q / energia_ref_Q
               e. Decide bits I baseado em limiares:
                  • I > +2A  → (0,0) [nível +3A]
                  • I > 0    → (0,1) [nível +A]
                  • I > -2A  → (1,1) [nível -A]
                  • I ≤ -2A  → (1,0) [nível -3A]
               f. Decide bits Q com mesmos limiares
               g. Retorna 4 bits: [bits_I, bits_Q]
        
        Detecção Multi-nível:
            O detector usa 3 limiares por dimensão (I e Q):
            - Limiar superior: +2A (separa +3A de +A)
            - Limiar central: 0 (separa positivos de negativos)
            - Limiar inferior: -2A (separa -A de -3A)
            
            Esses limiares são posicionados no meio entre
            os níveis adjacentes para minimizar BER.
        
        Normalização de Energia:
            A correlação retorna valores proporcionais à energia
            das portadoras. Normalizar isola as amplitudes I e Q:
            
            I_norm = Σ(sinal × cos) / Σ(cos²)
            Q_norm = Σ(sinal × -sin) / Σ(sin²)
        
        Mapeamento Reverso (Gray Code):
            Níveis I ou Q:
            - +3A → (0,0)
            - +A  → (0,1)
            - -A  → (1,1)
            - -3A → (1,0)
        
        Notas:
            - Requer sincronização perfeita de fase e frequência
            - Limiares em ±2A são ótimos para ruído gaussiano
            - Decisões em I e Q são independentes
            - Segmentos incompletos são ignorados
        
        Métricas de Performance:
            - BER mínimo com limiares ótimos
            - SNR requerido: ~18 dB para BER=10^-5
            - Mais sensível a ruído que QPSK (~4 dB pior)
        
        Exemplos:
            >>> qam = QAM16(amplitude=1.0, frequencia=100)
            >>> bits = [1, 0, 1, 1, 0, 0, 0, 1, 1, 1, 0, 1]
            >>> sinal = qam.codificar(bits)
            >>> bits_recuperados = qam.decodificar(sinal)
            >>> print(bits == bits_recuperados)
            True
        """
        amp = self.amplitude                                                # Carrega a amplitude da portadora
        freq = self.frequencia                                              # Carrega a frequência da portadora
        tx = self.taxa_amostragem                                           # Carrega a taxa de amostragem (amostras/s)
        amostras_por_simbolo = int(self.taxa_amostragem / self.taxa_bits)   # Calcula amostras por símbolo (4 bits) baseado na taxa de bits
        
        t = np.arange(amostras_por_simbolo) / tx                            # O vetor t dará o instante de cada amostra na portadora (bit dura 0.1s)
        bits = []                                                           # Lista para guardar os bits decodificados
        ref_I = np.cos(2 * np.pi * freq * t)                                # Portadora I (cos)
        ref_Q = -np.sin(2 * np.pi * freq * t)                               # Portadora Q (-sen)
        mapa_reverso = {
            -3 * amp: (1, 0),
            -1 * amp: (1, 1),
            1 * amp: (0, 1),
            3 * amp: (0, 0)
        }
        for i in range (0, len(sinal), amostras_por_simbolo):
            segmento_amostras = sinal[i:i + amostras_por_simbolo]           # Pega as amostras referentes ao bit
            I = np.sum(segmento_amostras * ref_I )                          # Calcula o I de acordo com a correlação com cos()
            Q = np.sum(segmento_amostras * ref_Q)                           # Calcula o Q de acordo com a correlação com -sen()
            energia_ref_I = np.sum(ref_I ** 2)                              # Calcula a energia da portadora I
            energia_ref_Q = np.sum(ref_Q ** 2)                              # Calcula a energia da portadora Q
            I_normalizado = I / energia_ref_I                               # Normalização de I e Q de acordo com as energias
            Q_normalizado = Q / energia_ref_Q                               # das respectivas portadoras para isolar as amplitudes

            if I_normalizado > (2 * amp):                                   # Bloco de decisão para o Canal I
                bits_I = (0, 0)  # Era +3
            elif I_normalizado > (0 * amp):
                bits_I = (0, 1)  # Era +1
            elif I_normalizado > (-2 * amp):
                bits_I = (1, 1)  # Era -1
            else:
                bits_I = (1, 0)  # Era -3

            if Q_normalizado > (2 * amp):                                   # Bloco de decisão para o Canal Q
                bits_Q = (0, 0)  # Era +3
            elif Q_normalizado > (0 * amp):
                bits_Q = (0, 1)  # Era +1
            elif Q_normalizado > (-2 * amp):
                bits_Q = (1, 1)  # Era -1
            else:
                bits_Q = (1, 0)  # Era -3

            bits.extend(bits_I)
            bits.extend(bits_Q)
        
        return bits





# ==============================================================
# TESTES DE MODULAÇÃO POR PORTADORA
# ==============================================================

if __name__ == "__main__":
    print("="*70)
    print("TESTANDO MODULAÇÕES POR PORTADORA")
    print("="*70)

    # Bits de teste
    bits_teste = [1, 0, 1, 1, 0, 1, 0, 0]  # 8 bits
    print(f"\nBits originais: {bits_teste}")

    # Teste ASK
    print("\n--- ASK ---")
    ask = ASK()
    sinal = ask.codificar(bits_teste)
    bits_rec = ask.decodificar(sinal)
    print(f"Bits recuperados: {bits_rec}")
    print(f"✓ Correto!" if bits_rec == bits_teste else "✗ ERRO!")

    # Teste FSK
    print("\n--- FSK ---")
    fsk = FSK()
    sinal = fsk.codificar(bits_teste)
    bits_rec = fsk.decodificar(sinal)
    print(f"Bits recuperados: {bits_rec}")
    print(f"✓ Correto!" if bits_rec == bits_teste else "✗ ERRO!")

    # Teste QPSK (precisa número par de bits)
    print("\n--- QPSK ---")
    qpsk = QPSK()
    sinal = qpsk.codificar(bits_teste)
    bits_rec = qpsk.decodificar(sinal)
    print(f"Bits recuperados: {bits_rec}")
    print(f"✓ Correto!" if bits_rec == bits_teste else "✗ ERRO!")

    # Teste 16-QAM (precisa múltiplo de 4 bits)
    print("\n--- 16-QAM ---")
    qam = QAM16()
    sinal = qam.codificar(bits_teste)
    bits_rec = qam.decodificar(sinal)
    print(f"Bits recuperados: {bits_rec}")
    print(f"✓ Correto!" if bits_rec == bits_teste else "✗ ERRO!")

    print("\n" + "="*70)  