"""
Módulo de Modulação Digital em Banda Base.

Este módulo implementa três técnicas clássicas de modulação digital em banda base,
onde os bits são codificados diretamente em níveis de tensão sem uso de portadora:
- NRZ-Polar: Non-Return-to-Zero Polar
- Manchester: Codificação com transição no meio do bit
- Bipolar (AMI): Alternate Mark Inversion

Classes:
    ModuladorDigital: Classe abstrata base para todos os moduladores digitais.
    NRZPolar: Implementa modulação NRZ-Polar (1→+V, 0→-V).
    Manchester: Implementa codificação Manchester com transição central.
    Bipolar: Implementa modulação Bipolar/AMI (1 alterna ±V, 0→0V).

Exemplos:
    >>> nrz = NRZPolar()
    >>> bits = [1, 0, 1, 1, 0]
    >>> sinal = nrz.codificar(bits)
    >>> bits_recuperados = nrz.decodificar(sinal)
    >>> print(bits == bits_recuperados)
    True

Notas:
    - Todas as modulações usam taxa_amostragem/taxa_bits amostras por bit
    - NRZ: Simple, eficiente, mas sem sincronização
    - Manchester: Autossincronizante, mas usa 2x a largura de banda
    - Bipolar: Detecta erros, DC balanceado, mas mais complexo
"""

from abc import ABC, abstractmethod
import numpy as np
from config import Config

class ModuladorDigital(ABC):
    """
    Classe abstrata base para moduladores digitais em banda base.
    
    Define a interface comum para todos os moduladores digitais e gerencia
    os parâmetros básicos de amplitude e taxa de amostragem. Calcula
    automaticamente o número de amostras por bit.
    
    Attributes:
        amplitude (float): Amplitude do sinal em Volts.
        taxa_amostragem (int): Taxa de amostragem em Hz (amostras/segundo).
        taxa_bits (int): Taxa de transmissão em bits/segundo.
        amostras_por_bit (int): Número de amostras usadas para representar cada bit.
    
    Métodos Abstratos:
        codificar: Converte bits em sinal analógico.
        decodificar: Converte sinal analógico em bits.
    
    Notas:
        - amostras_por_bit = taxa_amostragem / taxa_bits
        - Valores padrão vêm de Config()
        - Subclasses devem implementar codificar() e decodificar()
    """

    def __init__(self, amplitude=None, taxa=None):
        """
        Inicializa o modulador digital com parâmetros configuráveis.
        
        Args:
            amplitude (float, optional): Amplitude do sinal em Volts.
                Se None, usa valor de Config.AMPLITUDE.
            taxa (int, optional): Taxa de amostragem em Hz.
                Se None, usa valor de Config.TAXA_AMOSTRAGEM.
        
        Notas:
            - taxa_bits sempre vem de Config e não pode ser sobrescrito aqui
            - amostras_por_bit é calculado automaticamente
            - Recomendado: amostras_por_bit >= 10 para boa qualidade
        """
        config = Config()
        self.amplitude = amplitude or config.AMPLITUDE
        self.taxa_amostragem = taxa or config.TAXA_AMOSTRAGEM
        self.taxa_bits = config.TAXA_BITS
        # Amostras por bit = taxa_amostragem / taxa_bits
        self.amostras_por_bit = int(self.taxa_amostragem / self.taxa_bits)

    @abstractmethod
    def codificar(self, bits: list) -> np.ndarray:
        """
        Codifica uma sequência de bits em sinal analógico.
        
        Args:
            bits (list): Lista de inteiros 0 e 1 a serem codificados.
            
        Returns:
            np.ndarray: Array numpy com as amostras do sinal.
                       Comprimento = len(bits) × amostras_por_bit.
        
        Notas:
            Método abstrato - deve ser implementado pelas subclasses.
        """
        pass

    @abstractmethod
    def decodificar(self, sinal: np.ndarray) -> list:
        """
        Decodifica um sinal analógico de volta em bits.
        
        Args:
            sinal (np.ndarray): Array numpy com as amostras do sinal.
            
        Returns:
            list: Lista de inteiros 0 e 1 recuperados do sinal.
                  Comprimento = len(sinal) // amostras_por_bit.
        
        Notas:
            Método abstrato - deve ser implementado pelas subclasses.
        """
        pass


class NRZPolar(ModuladorDigital):
    """
    Modulação NRZ-Polar (Non-Return-to-Zero Polar).
    
    Técnica de modulação digital mais simples, onde:
    - Bit 1 é representado por tensão positiva (+V)
    - Bit 0 é representado por tensão negativa (-V)
    - O sinal não retorna a zero entre bits
    
    Vantagens:
        - Simples de implementar
        - Eficiente em largura de banda
        - Fácil de detectar com threshold em 0V
    
    Desvantagens:
        - Sem autossincronização (longas sequências sem transição)
        - Componente DC não nula
        - Dificulta recuperação de clock
    
    Exemplos:
        >>> nrz = NRZPolar(amplitude=5.0)
        >>> bits = [1, 0, 1, 0]
        >>> sinal = nrz.codificar(bits)
        >>> # Para 100 amostras/bit: sinal tem 400 amostras
        >>> # [+5V...+5V, -5V...-5V, +5V...+5V, -5V...-5V]
    """

    def codificar(self, bits: list) -> np.ndarray:
        """
        Codifica bits usando modulação NRZ-Polar.
        
        Cada bit é representado por um nível constante de tensão
        durante toda sua duração (amostras_por_bit amostras).
        
        Args:
            bits (list): Sequência de bits (0 e 1) a codificar.
            
        Returns:
            np.ndarray: Sinal digital com len(bits) × amostras_por_bit amostras.
                       Valores: +amplitude para 1, -amplitude para 0.
        
        Exemplos:
            >>> nrz = NRZPolar(amplitude=5.0)
            >>> sinal = nrz.codificar([1, 0, 1])
            >>> # Com 10 amostras/bit: 30 amostras no total
            >>> print(len(sinal))
            30
        """
        sinal = []
        for bit in bits:
            if bit == 1:
                # Repete amplitude positiva por todas as amostras do bit
                sinal.extend([self.amplitude] * self.amostras_por_bit)
            else:
                # Repete amplitude negativa por todas as amostras do bit
                sinal.extend([-self.amplitude] * self.amostras_por_bit)
        return np.array(sinal)

    def decodificar(self, sinal: np.ndarray) -> list:
        """
        Decodifica sinal NRZ-Polar de volta em bits.
        
        Agrupa amostras em segmentos de tamanho amostras_por_bit e
        calcula a média de cada segmento. Média positiva → bit 1,
        média negativa → bit 0.
        
        Args:
            sinal (np.ndarray): Sinal a decodificar.
            
        Returns:
            list: Sequência de bits recuperados (0 e 1).
        
        Notas:
            - Usa threshold em 0V (média > 0 → 1, média ≤ 0 → 0)
            - Robusta contra ruído moderado
            - Amostras parciais no final são ignoradas
        
        Exemplos:
            >>> nrz = NRZPolar()
            >>> sinal = np.array([5, 5, -5, -5, 5, 5])  # 2 amostras/bit
            >>> bits = nrz.decodificar(sinal)
            >>> print(bits)
            [1, 0, 1]
        """
        bits = []
        # Agrupa amostras por bit e decide baseado na média
        for i in range(0, len(sinal), self.amostras_por_bit):
            segmento = sinal[i:i + self.amostras_por_bit]
            media = np.mean(segmento)
            bits.append(1 if media > 0 else 0)
        return bits


class Manchester(ModuladorDigital):
    """
    Codificação Manchester (IEEE 802.3).
    
    Técnica de codificação digital com transição no meio de cada bit:
    - Bit 1: transição de baixo (-V) para alto (+V) no meio
    - Bit 0: transição de alto (+V) para baixo (-V) no meio
    
    Vantagens:
        - Autossincronizante (sempre há transição no meio do bit)
        - Sem componente DC (balanceado)
        - Facilita recuperação de clock
        - Detecta erros de sincronização
    
    Desvantagens:
        - Usa 2× a largura de banda do NRZ
        - Requer circuitos mais complexos
        - Menor eficiência espectral
    
    Aplicações:
        - Ethernet 10BASE-T
        - RFID
        - NFC
    
    Exemplos:
        >>> manch = Manchester(amplitude=5.0)
        >>> bits = [1, 0]
        >>> sinal = manch.codificar(bits)
        >>> # Bit 1: [-5V, -5V, ..., +5V, +5V, ...]
        >>> # Bit 0: [+5V, +5V, ..., -5V, -5V, ...]
    """

    def codificar(self, bits: list) -> np.ndarray:
        """
        Codifica bits usando modulação Manchester.
        
        Cada bit é dividido em duas metades com tensões opostas,
        garantindo uma transição no meio do bit period.
        
        Args:
            bits (list): Sequência de bits (0 e 1) a codificar.
            
        Returns:
            np.ndarray: Sinal com len(bits) × amostras_por_bit amostras.
                       Cada bit tem transição no meio.
        
        Detalhes:
            - Bit 1: primeira metade = -amplitude, segunda = +amplitude
            - Bit 0: primeira metade = +amplitude, segunda = -amplitude
            - Metade = amostras_por_bit // 2
        
        Exemplos:
            >>> manch = Manchester(amplitude=5.0)
            >>> # Com 100 amostras/bit:
            >>> sinal = manch.codificar([1])
            >>> print(sinal[:50])  # Primeira metade: -5V
            >>> print(sinal[50:])  # Segunda metade: +5V
        """
        sinal = []
        metade = self.amostras_por_bit // 2
        
        for bit in bits:
            if bit == 1:
                # Bit 1: primeira metade negativa, segunda metade positiva
                sinal.extend([-self.amplitude] * metade)
                sinal.extend([self.amplitude] * metade)
            else:
                # Bit 0: primeira metade positiva, segunda metade negativa
                sinal.extend([self.amplitude] * metade)
                sinal.extend([-self.amplitude] * metade)
        return np.array(sinal)

    def decodificar(self, sinal: np.ndarray) -> list:
        """
        Decodifica sinal Manchester de volta em bits.
        
        Divide cada período de bit em duas metades e analisa a direção
        da transição: baixo→alto = 1, alto→baixo = 0.
        
        Args:
            sinal (np.ndarray): Sinal a decodificar.
            
        Returns:
            list: Sequência de bits recuperados (0 e 1).
        
        Algoritmo:
            1. Divide sinal em segmentos de amostras_por_bit
            2. Para cada segmento, calcula média da primeira e segunda metade
            3. Se média1 < 0 e média2 > 0 → bit 1
            4. Caso contrário → bit 0
        
        Notas:
            - Detecta transições mesmo com ruído moderado
            - Segmentos incompletos são ignorados
            - Robusta contra offsets DC
        
        Exemplos:
            >>> manch = Manchester()
            >>> sinal = np.array([-5, -5, 5, 5, 5, 5, -5, -5])  # 4 amostras/bit
            >>> bits = manch.decodificar(sinal)
            >>> print(bits)
            [1, 0]
        """
        bits = []
        metade = self.amostras_por_bit // 2
        
        # Agrupa amostras por bit
        for i in range(0, len(sinal), self.amostras_por_bit):
            primeira_metade = sinal[i:i + metade]
            segunda_metade = sinal[i + metade:i + self.amostras_por_bit]
            
            if len(primeira_metade) > 0 and len(segunda_metade) > 0:
                media1 = np.mean(primeira_metade)
                media2 = np.mean(segunda_metade)
                
                # Bit 1: primeira negativa, segunda positiva
                if media1 < 0 and media2 > 0:
                    bits.append(1)
                else:
                    bits.append(0)
        return bits


class Bipolar(ModuladorDigital):
    """
    Modulação Bipolar AMI (Alternate Mark Inversion).
    
    Técnica de codificação onde bits 1 alternam entre tensões positiva e negativa,
    enquanto bits 0 são representados por tensão zero:
    - Bit 0: 0V (sem sinal)
    - Bit 1: alterna entre +V e -V a cada ocorrência
    
    Vantagens:
        - Sem componente DC (perfeitamente balanceado)
        - Detecta erros de pulso (dois pulsos consecutivos iguais = erro)
        - Melhor para transmissão em transformadores e capacitores
        - Usa apenas 3 níveis de tensão
    
    Desvantagens:
        - Longas sequências de 0s não têm transições (perda de sincronismo)
        - Requer detecção de 3 níveis em vez de 2
        - Mais sensível a ruído que NRZ
    
    Aplicações:
        - Linhas telefônicas T1/E1
        - ISDN (Integrated Services Digital Network)
        - Transmissão de longa distância
    
    Exemplos:
        >>> bip = Bipolar(amplitude=5.0)
        >>> bits = [1, 0, 1, 1, 0, 1]
        >>> sinal = bip.codificar(bits)
        >>> # Resultado: [+5V, 0V, -5V, +5V, 0V, -5V]
        >>> # Note a alternância dos bits 1 entre +V e -V
    """

    def codificar(self, bits: list) -> np.ndarray:
        """
        Codifica bits usando modulação Bipolar AMI.
        
        Bits 1 alternam entre +amplitude e -amplitude, enquanto
        bits 0 são codificados como 0V.
        
        Args:
            bits (list): Sequência de bits (0 e 1) a codificar.
            
        Returns:
            np.ndarray: Sinal com len(bits) × amostras_por_bit amostras.
                       Valores possíveis: +amplitude, 0, -amplitude.
        
        Detalhes:
            - Mantém estado interno (ultimo_valor) para alternar pulsos
            - Primeiro bit 1 usa +amplitude
            - Bits 1 subsequentes alternam sinal
            - Bits 0 sempre geram 0V
        
        Notas:
            A alternância permite detectar erros: se dois pulsos consecutivos
            tiverem o mesmo sinal, houve um erro de transmissão.
        
        Exemplos:
            >>> bip = Bipolar(amplitude=5.0)
            >>> sinal = bip.codificar([1, 1, 0, 1])
            >>> # Com 10 amostras/bit:
            >>> # Primeiros 10: +5V (primeiro 1)
            >>> # Próximos 10: -5V (segundo 1, alterna)
            >>> # Próximos 10: 0V (zero)
            >>> # Últimos 10: +5V (terceiro 1, alterna de novo)
        """
        sinal = []
        ultimo_valor = self.amplitude
        
        for bit in bits:
            if bit == 0:
                # Bit 0: amplitude zero por todas as amostras
                sinal.extend([0] * self.amostras_por_bit)
            else:
                # Bit 1: alterna entre +V e -V
                sinal.extend([ultimo_valor] * self.amostras_por_bit)
                ultimo_valor = -ultimo_valor
        return np.array(sinal)

    def decodificar(self, sinal: np.ndarray) -> list:
        """
        Decodifica sinal Bipolar AMI de volta em bits.
        
        Analisa a magnitude absoluta de cada período de bit para determinar
        se é um 0 (magnitude baixa) ou 1 (magnitude alta).
        
        Args:
            sinal (np.ndarray): Sinal a decodificar.
            
        Returns:
            list: Sequência de bits recuperados (0 e 1).
        
        Algoritmo:
            1. Divide sinal em segmentos de amostras_por_bit
            2. Calcula média do valor absoluto de cada segmento
            3. Se média_abs < limiar (amplitude/2) → bit 0
            4. Se média_abs >= limiar → bit 1
        
        Notas:
            - Limiar = amplitude/2 oferece boa robustez contra ruído
            - Ignora a polaridade (apenas magnitude importa)
            - Para amplitude de 5V, limiar = 2.5V
            - Valores parciais no final são ignorados
        
        Exemplos:
            >>> bip = Bipolar(amplitude=5.0)
            >>> # Com 10 amostras/bit:
            >>> sinal = np.array([5]*10 + [0]*10 + [-5]*10)
            >>> bits = bip.decodificar(sinal)
            >>> print(bits)
            [1, 0, 1]
        """
        bits = []
        # Agrupa amostras por bit e decide baseado na média do valor absoluto
        # Limiar em metade da amplitude para robustez contra ruído
        limiar = self.amplitude / 2.0  # 2.5V para amplitude de 5V
        
        for i in range(0, len(sinal), self.amostras_por_bit):
            segmento = sinal[i:i + self.amostras_por_bit]
            media_abs = np.mean(np.abs(segmento))
            # Se média absoluta é próxima de zero, é bit 0, caso contrário é bit 1
            bits.append(0 if media_abs < limiar else 1)
        return bits

# ==============================================================
# TESTES DE MODULAÇÃO DIGITAL
# ==============================================================

if __name__ == "__main__":
    print("="*70)
    print("TESTANDO MODULAÇÕES DIGITAIS - PESSOA 1")
    print("="*70)

    # Bits de teste
    bits_teste = [1, 0, 1, 1, 0, 0, 1, 0]
    print(f"\nBits originais: {bits_teste}")

    # Teste NRZ-Polar
    print("\n--- NRZ-Polar ---")
    nrz = NRZPolar()
    sinal_nrz = nrz.codificar(bits_teste)
    print(f"Sinal: {sinal_nrz}")
    bits_nrz = nrz.decodificar(sinal_nrz)
    print(f"Bits recuperados: {bits_nrz}")
    print(f"✓ Correto!" if bits_nrz == bits_teste else "✗ ERRO!")

    # Teste Manchester
    print("\n--- Manchester ---")
    manch = Manchester()
    sinal_manch = manch.codificar(bits_teste)
    print(f"Sinal (tamanho {len(sinal_manch)}): {sinal_manch[:16]}...")
    bits_manch = manch.decodificar(sinal_manch)
    print(f"Bits recuperados: {bits_manch}")
    print(f"✓ Correto!" if bits_manch == bits_teste else "✗ ERRO!")

    # Teste Bipolar
    print("\n--- Bipolar ---")
    bip = Bipolar()
    sinal_bip = bip.codificar(bits_teste)
    print(f"Sinal: {sinal_bip}")
    bits_bip = bip.decodificar(sinal_bip)
    print(f"Bits recuperados: {bits_bip}")
    print(f"✓ Correto!" if bits_bip == bits_teste else "✗ ERRO!")

    print("\n" + "="*70)
