"""
Moduladores por portadora: ASK, FSK, QPSK, 16-QAM
"""

from abc import ABC, abstractmethod
import numpy as np
from config import Config

class ModuladorPortadora(ABC):
    """Classe abstrata para moduladores por portadora"""

    def __init__(self, amplitude=None, frequencia=None, taxa=None):
        config = Config()
        self.amplitude = amplitude or config.AMPLITUDE
        self.frequencia = frequencia or config.FREQUENCIA_PORTADORA
        self.taxa_amostragem = taxa or config.TAXA_AMOSTRAGEM
        self.taxa_bits = config.TAXA_BITS

    @abstractmethod
    def codificar(self, bits: list) -> np.ndarray:
        """Codifica bits em sinal modulado"""
        pass

    @abstractmethod
    def decodificar(self, sinal: np.ndarray) -> list:
        """Decodifica sinal modulado em bits"""
        pass


class ASK(ModuladorPortadora):
    """Amplitude Shift Keying"""

    def codificar(self, bits: list) -> np.ndarray:
        """
        Implementar ASK
        Bit 1 → portadora com amplitude A
        Bit 0 → sem sinal (amplitude 0)
        """
        amp = self.amplitude                                    # Carrega a amplitude da portadora
        freq = self.frequencia                                  # Carrega a frequência da portadora
        tx = self.taxa_amostragem                               # Carrega a taxa de amostragem (amostras/s)
        amostras_por_bit = int(self.taxa_amostragem / self.taxa_bits)  # Calcula amostras por bit baseado na taxa de bits

        size = len(bits)                                        # Calcula a quantidade de bits a serem transmitidos

        sinal = np.zeros(size * amostras_por_bit)               # Cria a onda final, inicializada com zeros e com tamanho
                                                                # referente ao número de bits vezes as amostras de cada um

        t = np.arange(amostras_por_bit) / tx                    # O vetor t dará o instante de cada amostra na portadora (bit dura 0.1s)
        
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
        Implementar decodificação ASK baseada no cálculo da energia
        do segmento de amostras
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
    """Frequency Shift Keying"""

    def codificar(self, bits: list) -> np.ndarray:
        """
        Implementar FSK
        Bit 1 → frequência alta
        Bit 0 → frequência baixa
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
        Implementar decodificação FSK baseada no cálculo de correlação
        entre as ondas de referência (f0 e f1) e a onda a ser decodificada:
        se a onda para decodificação e a de referência tiverem mesma estrutura,
        o resultado da correlação com ela será uma função cos^2 (sempre positiva)
        e uma função de onda complexa (com valores positivos e negativos) com 
        a outra onda referência
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
    """Quadrature Phase Shift Keying"""

    def codificar(self, bits: list) -> np.ndarray:
        """
        Implementar QPSK
        Cada par de bits → uma fase específica
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
        Implementar decodificação QPSK baseada no cálculo da
        correlação entre as funções seno (Q padrão) e cosseno (I padrão)
        e a onda a ser decodificada. A fase será o arctan de Q e I e
        será usada para o mapeamento
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
    """16-QAM: Modulação de amplitude e fase"""

    def codificar(self, bits: list) -> np.ndarray:
        """
        Implementar 16-QAM
        Cada 4 bits → uma combinação de amplitude e fase
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
        Implementar decodificação 16-QAM seguindo o mesmo princípio
        de correlação entre as referências das portadoras I e Q e
        normalizando a energia para fazer o mapeamento da amplitude
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
    print("TESTANDO MODULAÇÕES POR PORTADORA - PESSOA 2")
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