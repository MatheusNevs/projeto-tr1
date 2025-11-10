# Guia da Pessoa 2 - Modulações por Portadora (Arquitetura OOP)

## 📁 Seu Arquivo

**Caminho:** `camada_fisica/modulador_portadora.py`

## 🎯 Suas Responsabilidades

Implementar **4 classes de modulação por portadora**:

1. **ASK** - Amplitude Shift Keying
2. **FSK** - Frequency Shift Keying
3. **QPSK** - Quadrature Phase Shift Keying (4-PSK)
4. **QAM16** - 16-Quadrature Amplitude Modulation

Cada classe deve ter 2 métodos:

- `codificar(bits: list) -> np.ndarray` - Converte bits em sinal modulado
- `decodificar(sinal: np.ndarray) -> list` - Converte sinal em bits

---

## 📚 Conceitos Básicos

### O que é Modulação por Portadora?

Usa uma **onda senoidal** (portadora) para transmitir dados digitais, variando suas propriedades.

**Fórmula básica da portadora:**

```
s(t) = A × cos(2πft + φ)
```

- **A** = Amplitude
- **f** = Frequência (Hz)
- **φ** = Fase (radianos)
- **t** = Tempo

### Tipos que você vai implementar:

| Modulação  | O que varia      | Bits/símbolo | Vantagem           |
| ---------- | ---------------- | ------------ | ------------------ |
| **ASK**    | Amplitude        | 1            | Simples            |
| **FSK**    | Frequência       | 1            | Robusto a ruído    |
| **QPSK**   | Fase             | 2            | Eficiente          |
| **16-QAM** | Amplitude + Fase | 4            | Alta taxa de dados |

---

## 🏗️ Estrutura do Arquivo

```python
from abc import ABC, abstractmethod
import numpy as np
from config import Config

class ModuladorPortadora(ABC):
    """Classe abstrata - NÃO MEXER"""
    def __init__(self, amplitude=None, frequencia=None, taxa=None):
        config = Config()
        self.amplitude = amplitude or config.AMPLITUDE
        self.frequencia = frequencia or config.FREQUENCIA_PORTADORA
        self.taxa_amostragem = taxa or config.TAXA_AMOSTRAGEM

    @abstractmethod
    def codificar(self, bits: list) -> np.ndarray:
        pass

    @abstractmethod
    def decodificar(self, sinal: np.ndarray) -> list:
        pass


# ==============================================================
# SUAS IMPLEMENTAÇÕES COMEÇAM AQUI
# ==============================================================

class ASK(ModuladorPortadora):
    """
    Amplitude Shift Keying
    Bit 1 → portadora com amplitude A
    Bit 0 → sem sinal (amplitude 0)
    """

    def codificar(self, bits: list) -> np.ndarray:
        """
        TODO: Implementar ASK

        Args:
            bits: Lista de bits [0, 1, 1, ...]

        Returns:
            Sinal modulado em ASK

        Exemplo visual:
            Bit 1: ~~~~ (onda senoidal com amplitude A)
            Bit 0: ____ (sem sinal, amplitude 0)

        Algoritmo:
            1. Para cada bit, criar vetor de tempo
            2. Se bit == 1: gerar cos(2πft) com amplitude A
            3. Se bit == 0: gerar zeros
            4. Concatenar todas as ondas
        """
        amostras_por_bit = self.taxa_amostragem // 10  # 100 amostras por bit
        sinal = []

        for bit in bits:
            # Gera vetor de tempo para este bit (0.1 segundo)
            t = np.linspace(0, 0.1, amostras_por_bit, endpoint=False)

            if bit == 1:
                # Bit 1: portadora com amplitude A
                onda = self.amplitude * np.cos(2 * np.pi * self.frequencia * t)
            else:
                # Bit 0: sem sinal (amplitude 0)
                onda = np.zeros(amostras_por_bit)

            sinal.extend(onda)

        return np.array(sinal)

    def decodificar(self, sinal: np.ndarray) -> list:
        """
        TODO: Implementar decodificação ASK

        Args:
            sinal: Sinal ASK recebido

        Returns:
            Lista de bits decodificados

        Algoritmo (detector de energia):
            1. Dividir sinal em segmentos (um por bit)
            2. Calcular energia de cada segmento (soma dos quadrados)
            3. Se energia > limiar → bit 1, senão bit 0
        """
        amostras_por_bit = self.taxa_amostragem // 10
        bits = []

        for i in range(0, len(sinal), amostras_por_bit):
            segmento = sinal[i:i+amostras_por_bit]

            # Calcula energia do segmento
            energia = np.sum(segmento ** 2)

            # Limiar: se energia > 0.1 → bit 1
            if energia > 0.1:
                bits.append(1)
            else:
                bits.append(0)

        return bits


class FSK(ModuladorPortadora):
    """
    Frequency Shift Keying
    Bit 1 → frequência alta (f1)
    Bit 0 → frequência baixa (f0)
    """

    def codificar(self, bits: list) -> np.ndarray:
        """
        TODO: Implementar FSK

        Algoritmo:
            - Defina duas frequências: f0 e f1
            - Para bit 0: use frequência f0
            - Para bit 1: use frequência f1

        Sugestão:
            f0 = self.frequencia        # Ex: 100 Hz
            f1 = self.frequencia * 2    # Ex: 200 Hz
        """
        amostras_por_bit = self.taxa_amostragem // 10
        sinal = []

        # Define duas frequências
        freq_0 = self.frequencia        # Frequência para bit 0
        freq_1 = self.frequencia * 2    # Frequência para bit 1

        for bit in bits:
            t = np.linspace(0, 0.1, amostras_por_bit, endpoint=False)

            if bit == 1:
                onda = self.amplitude * np.cos(2 * np.pi * freq_1 * t)
            else:
                onda = self.amplitude * np.cos(2 * np.pi * freq_0 * t)

            sinal.extend(onda)

        return np.array(sinal)

    def decodificar(self, sinal: np.ndarray) -> list:
        """
        TODO: Implementar decodificação FSK

        Algoritmo (detector de correlação):
            1. Para cada segmento, calcular correlação com f0 e f1
            2. Se correlação com f1 > correlação com f0 → bit 1
            3. Caso contrário → bit 0

        Correlação: soma(sinal × referência)
        """
        amostras_por_bit = self.taxa_amostragem // 10
        bits = []

        freq_0 = self.frequencia
        freq_1 = self.frequencia * 2

        for i in range(0, len(sinal), amostras_por_bit):
            segmento = sinal[i:i+amostras_por_bit]
            t = np.linspace(0, 0.1, len(segmento), endpoint=False)

            # Correlação com cada frequência
            ref_0 = np.cos(2 * np.pi * freq_0 * t)
            ref_1 = np.cos(2 * np.pi * freq_1 * t)

            correlacao_0 = np.abs(np.sum(segmento * ref_0))
            correlacao_1 = np.abs(np.sum(segmento * ref_1))

            # Decide baseado em qual correlação é maior
            if correlacao_1 > correlacao_0:
                bits.append(1)
            else:
                bits.append(0)

        return bits


class QPSK(ModuladorPortadora):
    """
    Quadrature Phase Shift Keying
    Cada símbolo representa 2 bits (4 fases possíveis)

    Mapeamento:
    00 → fase 45°  (π/4)
    01 → fase 135° (3π/4)
    10 → fase 225° (5π/4)
    11 → fase 315° (7π/4)
    """

    def codificar(self, bits: list) -> np.ndarray:
        """
        TODO: Implementar QPSK

        IMPORTANTE: Processa 2 bits por vez!

        Algoritmo:
            1. Criar dicionário de fases
            2. Processar bits em pares (00, 01, 10, 11)
            3. Para cada par, gerar portadora com fase correspondente
        """
        amostras_por_simbolo = self.taxa_amostragem // 10
        sinal = []

        # Mapeia pares de bits para fases
        mapa_fase = {
            (0, 0): np.pi/4,      # 45°
            (0, 1): 3*np.pi/4,    # 135°
            (1, 0): 5*np.pi/4,    # 225°
            (1, 1): 7*np.pi/4     # 315°
        }

        # Processa bits de 2 em 2
        for i in range(0, len(bits), 2):
            if i + 1 < len(bits):
                par_bits = (bits[i], bits[i+1])
                fase = mapa_fase[par_bits]

                t = np.linspace(0, 0.1, amostras_por_simbolo, endpoint=False)
                onda = self.amplitude * np.cos(2 * np.pi * self.frequencia * t + fase)
                sinal.extend(onda)

        return np.array(sinal)

    def decodificar(self, sinal: np.ndarray) -> list:
        """
        TODO: Implementar decodificação QPSK

        Algoritmo:
            1. Para cada símbolo, detectar componentes I e Q
            2. Calcular fase: arctan2(Q, I)
            3. Mapear fase de volta para par de bits

        Componentes I e Q:
            I (In-phase) = integral de sinal × cos(2πft)
            Q (Quadrature) = integral de sinal × sin(2πft)
        """
        amostras_por_simbolo = self.taxa_amostragem // 10
        bits = []

        for i in range(0, len(sinal), amostras_por_simbolo):
            segmento = sinal[i:i+amostras_por_simbolo]
            t = np.linspace(0, 0.1, len(segmento), endpoint=False)

            # Detecta componentes I e Q
            I = np.sum(segmento * np.cos(2 * np.pi * self.frequencia * t))
            Q = np.sum(segmento * np.sin(2 * np.pi * self.frequencia * t))

            # Calcula fase
            fase = np.arctan2(Q, I)

            # Mapeia fase para bits
            if -np.pi/2 < fase <= 0:
                bits.extend([0, 0])
            elif 0 < fase <= np.pi/2:
                bits.extend([0, 1])
            elif np.pi/2 < fase <= np.pi:
                bits.extend([1, 0])
            else:
                bits.extend([1, 1])

        return bits


class QAM16(ModuladorPortadora):
    """
    16-QAM: Modulação de amplitude e fase
    Cada símbolo representa 4 bits (16 combinações)

    Constelação 4×4:
         Q
         |
      3  •  • 1
         |
    -----•--•----- I
         |
      2  •  • 0
         |
    """

    def codificar(self, bits: list) -> np.ndarray:
        """
        TODO: Implementar 16-QAM

        IMPORTANTE: Processa 4 bits por vez!

        Algoritmo:
            1. Níveis de amplitude: -3A, -A, +A, +3A
            2. Primeiros 2 bits → componente I
            3. Últimos 2 bits → componente Q
            4. Sinal = I×cos(ωt) - Q×sin(ωt)
        """
        amostras_por_simbolo = self.taxa_amostragem // 10
        sinal = []

        # Níveis de amplitude: -3, -1, +1, +3
        niveis = [-3, -1, 1, 3]

        # Processa bits de 4 em 4
        for i in range(0, len(bits), 4):
            if i + 3 < len(bits):
                # Primeiros 2 bits → índice I
                idx_I = bits[i] * 2 + bits[i+1]  # 00→0, 01→1, 10→2, 11→3
                # Últimos 2 bits → índice Q
                idx_Q = bits[i+2] * 2 + bits[i+3]

                I = niveis[idx_I] * self.amplitude / 3
                Q = niveis[idx_Q] * self.amplitude / 3

                t = np.linspace(0, 0.1, amostras_por_simbolo, endpoint=False)
                # Sinal = I×cos(ωt) - Q×sin(ωt)
                onda = I * np.cos(2 * np.pi * self.frequencia * t) - \
                       Q * np.sin(2 * np.pi * self.frequencia * t)
                sinal.extend(onda)

        return np.array(sinal)

    def decodificar(self, sinal: np.ndarray) -> list:
        """
        TODO: Implementar decodificação 16-QAM

        Algoritmo:
            1. Detectar componentes I e Q
            2. Quantizar I e Q para os 4 níveis
            3. Converter índices de volta para 4 bits
        """
        amostras_por_simbolo = self.taxa_amostragem // 10
        bits = []

        for i in range(0, len(sinal), amostras_por_simbolo):
            segmento = sinal[i:i+amostras_por_simbolo]
            t = np.linspace(0, 0.1, len(segmento), endpoint=False)

            # Detecta I e Q
            I = np.sum(segmento * np.cos(2 * np.pi * self.frequencia * t))
            Q = -np.sum(segmento * np.sin(2 * np.pi * self.frequencia * t))

            # Quantiza I e Q para níveis -3, -1, 1, 3
            def quantizar(valor):
                if valor < -2:
                    return 0  # -3
                elif valor < 0:
                    return 1  # -1
                elif valor < 2:
                    return 2  # +1
                else:
                    return 3  # +3

            idx_I = quantizar(I)
            idx_Q = quantizar(Q)

            # Converte índices de volta para bits
            bits.append((idx_I >> 1) & 1)  # Bit mais significativo de I
            bits.append(idx_I & 1)         # Bit menos significativo de I
            bits.append((idx_Q >> 1) & 1)  # Bit mais significativo de Q
            bits.append(idx_Q & 1)         # Bit menos significativo de Q

        return bits
```

---

## ✅ Como Testar

Adicione no final do arquivo:

```python
# ==============================================================
# TESTES - Pessoa 2
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
```

Execute:

```bash
python -m camada_fisica.modulador_portadora
```

---

## 🔍 Checklist

- [ ] `ASK.codificar()` e `decodificar()`
- [ ] `FSK.codificar()` e `decodificar()`
- [ ] `QPSK.codificar()` e `decodificar()` (2 bits/símbolo)
- [ ] `QAM16.codificar()` e `decodificar()` (4 bits/símbolo)
- [ ] Todos os testes passam
- [ ] Código comentado

---

## 🆘 Dúvidas Comuns

**P: Como calcular componentes I e Q?**
R: I = soma(sinal × cos), Q = soma(sinal × sin)

**P: QPSK processa quantos bits?**
R: 2 bits por símbolo (4 fases)

**P: 16-QAM processa quantos bits?**
R: 4 bits por símbolo (16 combinações)

**P: Como testar sem ruído?**
R: Use `CanalComunicacao(nivel_ruido=0.0)`

---

**Boa sorte!** 🚀
