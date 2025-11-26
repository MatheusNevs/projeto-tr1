# 📡 Arquitetura do Sistema - Simulador TR1

## Visão Geral

O **Simulador TR1** é um sistema educacional completo para demonstração de comunicação digital, implementando todas as camadas do modelo de comunicação desde a entrada de texto até a transmissão do sinal analógico, passando por técnicas de detecção/correção de erros, enquadramento e modulação.

### Objetivo

Simular um sistema de comunicação digital end-to-end com:
- Múltiplas técnicas de modulação (digital e por portadora)
- Detecção e correção de erros (Paridade, Checksum, CRC, Hamming)
- Enquadramento de dados (Contagem de Bytes, Bit Stuffing)
- Canal com ruído AWGN (Additive White Gaussian Noise)
- Visualização gráfica de sinais e espectros

---

## 🏗️ Arquitetura em Camadas

O sistema segue uma arquitetura em camadas inspirada no modelo OSI, com cada camada responsável por uma função específica:

```
┌─────────────────────────────────────────────────────────────┐
│                      INTERFACE GRÁFICA                       │
│  (Tkinter + Matplotlib - Controles e Visualização)          │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┴───────────────────┐
        │                                       │
        ▼                                       ▼
┌──────────────┐                      ┌──────────────┐
│ TRANSMISSOR  │                      │   RECEPTOR   │
│ (Pipeline TX)│                      │ (Pipeline RX)│
└──────────────┘                      └──────────────┘
        │                                       ▲
        │           ┌───────────────┐          │
        └──────────►│  CANAL AWGN   │──────────┘
                    │ (Adiciona Ruído)
                    └───────────────┘

PIPELINE DE TRANSMISSÃO (TX):
┌─────────────────────────────────────────────────────────────┐
│ Texto → Bits → [Hamming] → [EDC] → [Quadro] → [Modulação]  │
└─────────────────────────────────────────────────────────────┘

PIPELINE DE RECEPÇÃO (RX):
┌─────────────────────────────────────────────────────────────┐
│ Sinal → [Demodulação] → [Desenquadrar] → [EDC] → [Hamming] │
└─────────────────────────────────────────────────────────────┘
```

---

## 📦 Estrutura de Módulos

### 1. **Configuração Global** (`config.py`)
- **Padrão:** Singleton
- **Responsabilidade:** Centralizar parâmetros globais do sistema
- **Parâmetros:**
  - Taxa de amostragem (Hz)
  - Taxa de bits (bps)
  - Frequência da portadora (Hz)
  - Tamanho máximo do quadro (bytes)
  - Tensão de nível alto/baixo (V)

**Por que Singleton?**
- Garante consistência de configurações em todo o sistema
- Evita conflitos entre componentes
- Facilita acesso global a parâmetros

---

### 2. **Camada Física** (`camada_fisica/`)

#### 2.1 Modulação Digital (`modulador_digital.py`)
Converte bits em sinais elétricos de banda base.

**Classes:**
- `NRZPolar`: Modulação mais simples (1 → +V, 0 → -V)
- `Manchester`: Autossincronizante, transição no meio do bit
- `Bipolar (AMI)`: DC balanceado, alterna polaridade dos '1's

**Fluxo:**
```
Bits: [1, 0, 1, 1, 0]
  ↓
NRZPolar.codificar()
  ↓
Sinal: [+V, +V, +V, -V, -V, -V, +V, +V, +V, ...]
       └─────┘ └─────┘ └─────┘
       amostras_por_bit
```

**Características:**
| Modulação  | Largura de Banda | Auto-Sincronização | DC Balanceado |
|------------|------------------|--------------------| --------------|
| NRZ-Polar  | Mínima (1×)      | ❌ Não             | ❌ Não        |
| Manchester | Dobrada (2×)     | ✅ Sim             | ✅ Sim        |
| Bipolar    | Média            | Parcial            | ✅ Sim        |

#### 2.2 Modulação por Portadora (`modulador_portadora.py`)
Modula sinais digitais em portadora de alta frequência.

**Classes:**
- `ASK`: Amplitude Shift Keying (varia amplitude)
- `FSK`: Frequency Shift Keying (varia frequência)
- `QPSK`: Quaternary Phase Shift Keying (4 fases, 2 bits/símbolo)
- `QAM16`: 16-QAM (16 símbolos, 4 bits/símbolo)

**Comparação:**
| Modulação | Bits/Símbolo | Eficiência | Resistência a Ruído |
|-----------|--------------|------------|---------------------|
| ASK       | 1            | Baixa      | Baixa               |
| FSK       | 1            | Média      | Alta                |
| QPSK      | 2            | Alta       | Média               |
| QAM16     | 4            | Muito Alta | Baixa               |

---

### 3. **Camada de Enlace** (`camada_enlace/`)

#### 3.1 Detecção de Erros (`detector_erros.py`)
Adiciona redundância para detectar erros.

**Técnicas Implementadas:**

| Técnica   | Overhead     | Taxa de Detecção | Aplicação Real  |
|-----------|--------------|------------------|-----------------|
| Paridade  | 1 bit/byte   | ~50%             | RAM, Serial     |
| Checksum  | 8-32 bits    | ~95%             | TCP/IP, UDP     |
| CRC       | 8-32 bits    | >99.99%          | Ethernet, USB   |

**Fluxo:**
```
Dados: [01010101, 11001100]
  ↓
DetectorCRC.adicionar_edc()
  ↓
[01010101, 11001100, CRC32: 10110010...]
```

#### 3.2 Correção de Erros (`corretor_erros.py`)
Implementa código de Hamming para correção.

**Hamming (SECDED):**
- **SEC:** Single Error Correction (corrige 1 bit)
- **DED:** Double Error Detection (detecta 2 bits)

**Cálculo de bits de paridade:**
```
2^r >= m + r + 1
onde:
  m = bits de dados
  r = bits de paridade
```

**Exemplo:**
```
4 bits dados → 3 bits paridade → 7 bits total
[D1, D2, D3, D4] → [P1, P2, D1, P4, D2, D3, D4]
                    └──────────────────────────┘
                      Posições: 1, 2, 3, 4, 5, 6, 7
```

#### 3.3 Enquadramento (`enquadrador.py`)
Delimita início e fim de quadros.

**Métodos:**

**a) Contagem de Bytes:**
```
┌────────────┬─────────────────────────┐
│ Tamanho(16)│      Dados...           │
└────────────┴─────────────────────────┘
```
- **Overhead:** Fixo (16 bits)
- **Vantagem:** Simples
- **Desvantagem:** Vulnerável a erros no campo tamanho

**b) FLAGS com Bit Stuffing:**
```
┌──────┬─────────────────────────┬──────┐
│ FLAG │   Dados (stuffed)       │ FLAG │
└──────┴─────────────────────────┴──────┘
FLAG = 01111110
```
- **Regra:** Após 5 '1's consecutivos, insere '0'
- **Vantagem:** Robusto
- **Desvantage:** Overhead variável

---

### 4. **Comunicação** (`comunicacao/`)

#### 4.1 Transmissor (`transmissor.py`)
Orquestra todo o pipeline de transmissão.

**Pipeline Completo:**
```python
texto = "Hello"
  ↓ Conversor.texto_para_bits()
bits = [01001000, 01100101, ...]
  ↓ CorretorHamming.codificar() [se habilitado]
bits_hamming = [bits com redundância]
  ↓ DetectorErros.adicionar_edc()
bits_edc = [bits + CRC/Checksum]
  ↓ Enquadrador.enquadrar()
quadro = [FLAG + bits_edc + FLAG]
  ↓ Modulador.codificar()
sinal = np.array([1.2, -0.8, 1.1, ...])
```

#### 4.2 Receptor (`receptor.py`)
Realiza o processo inverso do transmissor.

**Pipeline Completo:**
```python
sinal = np.array([1.2, -0.8, ...])
  ↓ Modulador.decodificar()
quadro = [FLAG + bits + FLAG]
  ↓ Enquadrador.desenquadrar()
bits_edc = [bits + CRC]
  ↓ DetectorErros.verificar_edc()
bits_hamming = [bits válidos]
  ↓ CorretorHamming.decodificar() [se habilitado]
bits = [bits originais corrigidos]
  ↓ Conversor.bits_para_texto()
texto = "Hello"
```

#### 4.3 Canal (`canal.py`)
Simula canal com ruído AWGN.

**Modelo Matemático:**
```
y(t) = x(t) + n(t)

onde:
  x(t) = sinal transmitido
  n(t) = ruído gaussiano ~ N(μ, σ²)
  y(t) = sinal recebido
```

**SNR (Signal-to-Noise Ratio):**
```
SNR = 10 × log₁₀(P_sinal / P_ruído) [dB]
```

**Interpretação:**
- **SNR > 20 dB:** Qualidade excelente
- **10-20 dB:** Boa qualidade
- **5-10 dB:** Qualidade aceitável
- **< 5 dB:** Muitos erros

---

### 5. **Interface Gráfica** (`interface/gui.py`)

#### Estrutura da Interface

**Layout em Duas Colunas:**
```
┌────────────────────────────────────────────────────────────┐
│              Simulador TR1 - Camadas de Rede               │
├──────────────────────┬─────────────────────────────────────┤
│   CONTROLES (550px)  │     GRÁFICOS (Expansível)           │
│                      │                                     │
│  ┌────────────────┐  │  ┌──────────────────────────────┐  │
│  │ Configurações  │  │  │ [Aba: Formas de Onda]        │  │
│  ├────────────────┤  │  │                              │  │
│  │ • Modulação    │  │  │  ┌──────────────────────┐    │  │
│  │ • Enquadramento│  │  │  │ Sinal TX             │    │  │
│  │ • Detecção EDC │  │  │  └──────────────────────┘    │  │
│  │ • Hamming      │  │  │  ┌──────────────────────┐    │  │
│  │ • Ruído (μ,σ)  │  │  │  │ Sinal RX             │    │  │
│  │ • Taxa Amostr. │  │  │  └──────────────────────┘    │  │
│  │ • Taxa Bits    │  │  │  ┌──────────────────────┐    │  │
│  │ • Freq. Portad.│  │  │  │ Comparação TX vs RX  │    │  │
│  └────────────────┘  │  │  └──────────────────────┘    │  │
│                      │  │                              │  │
│  ┌────────────────┐  │  │ [Aba: Análise Espectro]      │  │
│  │ Transmissão    │  │  │                              │  │
│  ├────────────────┤  │  │  ┌──────────────────────┐    │  │
│  │ Mensagem: ___  │  │  │  │ FFT TX               │    │  │
│  │ [Transmitir]   │  │  │  └──────────────────────┘    │  │
│  └────────────────┘  │  │  ┌──────────────────────┐    │  │
│                      │  │  │ FFT RX               │    │  │
│  ┌────────────────┐  │  │  └──────────────────────┘    │  │
│  │ Logs           │  │  │                              │  │
│  │ ╔════════════╗ │  │  └──────────────────────────────┘  │
│  │ ║ TX: Hello  ║ │  │                                     │
│  │ ║ Canal: σ=0.3║│  │                                     │
│  │ ║ RX: Hello  ║ │  │                                     │
│  │ ║ ✓ Sucesso! ║ │  │                                     │
│  │ ╚════════════╝ │  │                                     │
│  │ [Limpar Logs]  │  │                                     │
│  └────────────────┘  │                                     │
│                      │                                     │
│  Status: Pronto      │                                     │
└──────────────────────┴─────────────────────────────────────┘
```

#### Componentes Principais

**1. Painel de Configurações:**
- Comboboxes para seleção de técnicas
- Sliders para parâmetros contínuos
- Checkboxes para opções binárias
- Botão "Aplicar Configurações"

**2. Painel de Transmissão:**
- Campo de entrada de mensagem
- Botão "Transmitir"

**3. Área de Logs:**
- ScrolledText com histórico completo
- Mostra todas as etapas do processo
- Estatísticas de erros

**4. Visualizações:**
- **Aba 1:** Formas de onda (domínio do tempo)
- **Aba 2:** Espectro FFT (domínio da frequência)
- Ferramentas de zoom/pan do Matplotlib

#### Threading e Concorrência

**Arquitetura Multi-Thread:**
```
Thread Principal (Tkinter)
  │
  ├─ Renderização da GUI
  ├─ Processamento de eventos
  └─ Atualização de widgets
  
Thread de Transmissão (daemon)
  │
  ├─ Codificação da mensagem
  ├─ Passagem pelo canal
  ├─ Decodificação
  └─ Logs (via root.after())
```

**Thread-Safety:**
- Logs usam `root.after(0, callback)` para evitar race conditions
- Thread daemon termina automaticamente com o programa
- Fila thread-safe (`queue.Queue`) para comunicação

---

## 🔄 Fluxo de Dados Completo

### Exemplo: Transmissão de "Hi"

#### **TRANSMISSOR (TX)**

**1. Entrada:**
```
Mensagem: "Hi"
```

**2. Conversão para Bits:**
```python
Conversor.texto_para_bits("Hi")
→ [01001000, 01101001]  # ASCII de 'H' e 'i'
```

**3. Código de Hamming (Opcional):**
```python
CorretorHamming.codificar([01001000])
→ [01001000 → 0100010011101]  # 8 bits → 13 bits
```

**4. Detecção de Erros (CRC-32):**
```python
DetectorCRC.adicionar_edc([bits])
→ [bits originais + CRC: 32 bits]
```

**5. Enquadramento (FLAGS):**
```python
EnquadradorFlagsBits.enquadrar([bits + CRC])
→ [01111110 + bits stuffed + 01111110]
```

**6. Modulação (NRZ-Polar, 10 bps, 1000 Hz):**
```python
NRZPolar.codificar([quadro])
→ Sinal: [+V, +V, ..., -V, -V, ...]
         └─100 amostras/bit─┘
```

---

#### **CANAL**

**7. Adição de Ruído (σ=0.3):**
```python
Canal.transmitir(sinal_tx)
→ sinal_rx = sinal_tx + np.random.normal(0, 0.3, len(sinal_tx))
```

**Visualização:**
```
TX: ────┐      ┌────┐      ┌────
        │      │    │      │
        └──────┘    └──────┘

RX: ───┐╲     ┌╱──┐╲     ┌╱──
       │ ╲   ╱│   │ ╲   ╱│
       └──╲─╱─┘   └──╲─╱─┘
          ruído
```

---

#### **RECEPTOR (RX)**

**8. Demodulação:**
```python
NRZPolar.decodificar(sinal_rx)
→ [quadro com possíveis erros]
```

**9. Desenquadramento:**
```python
EnquadradorFlagsBits.desenquadrar([quadro])
→ [bits + CRC]
```

**10. Verificação de Erros:**
```python
DetectorCRC.verificar_edc([bits + CRC])
→ erro_detectado = False  # Se CRC válido
→ [bits sem CRC]
```

**11. Correção de Erros:**
```python
CorretorHamming.decodificar([bits])
→ [bits corrigidos]
→ erros_corrigidos = 2  # Bits corrigidos
```

**12. Conversão para Texto:**
```python
Conversor.bits_para_texto([01001000, 01101001])
→ "Hi"
```

---

## 📊 Métricas e Estatísticas

### Estatísticas Exibidas na Interface

**1. Estatísticas de Sinal:**
- Mínimo, Máximo, Média, Desvio Padrão (V)
- Número de amostras
- Duração temporal (ms)

**2. Qualidade da Transmissão:**
- **MSE** (Mean Squared Error): `mean((RX - TX)²)`
- **SNR** (Signal-to-Noise Ratio): `10 × log₁₀(P_sinal / P_ruído)` dB

**3. Análise de Espectro:**
- Frequência dominante (Hz)
- Potência total (dB)
- Distribuição espectral

**4. Detecção/Correção:**
- Erros detectados pelo EDC
- Bits corrigidos pelo Hamming

### Exemplo de Saída de Logs

```
================================================================================
INICIANDO TRANSMISSÃO
================================================================================

>>> TRANSMISSOR <<<
Mensagem original: 'Hello'
Bits (40): [01001000, 01100101, 01101100, 01101100, 01101111]
Aplicando Hamming... (40 bits → 65 bits)
Adicionando CRC-32... (65 bits → 97 bits)
Enquadrando (FLAGS)... (97 bits → 115 bits)
Modulando NRZ-Polar... (115 bits → 11500 amostras)

>>> CANAL DE COMUNICAÇÃO <<<
Sinal atravessou o canal (ruído σ=0.30)

>>> RECEPTOR <<<
Demodulando... (11500 amostras → 115 bits)
Desenquadrando... (115 bits → 97 bits)
Verificando CRC-32... ✓ SEM ERROS
Decodificando Hamming... 2 bits corrigidos
Bits finais (40): [01001000, 01100101, 01101100, 01101100, 01101111]
Mensagem recuperada: 'Hello'

================================================================================
RESULTADO
================================================================================
Mensagem TX: 'Hello'
Mensagem RX: 'Hello'
✓ TRANSMISSÃO BEM-SUCEDIDA!
Erros detectados: 0
Erros corrigidos (Hamming): 2
================================================================================
```

---


## 🔧 Padrões de Design Utilizados

### 1. **Singleton** (`Config`)
Garante única instância de configuração global.

```python
class Config:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
```

### 2. **Strategy** (Moduladores, Detectores, Enquadradores)
Permite trocar algoritmos em runtime.

```python
class Transmissor:
    def __init__(self, modulador, enquadrador, detector, usar_hamming):
        self.modulador = modulador  # Pode ser NRZ, Manchester, ASK, etc.
        self.enquadrador = enquadrador  # Pode ser Contagem ou FLAGS
        self.detector = detector  # Pode ser CRC, Checksum, Paridade
```

### 3. **Template Method** (Classes Base Abstratas)
Define esqueleto do algoritmo em classe base.

```python
class ModuladorDigital(ABC):
    @abstractmethod
    def codificar(self, bits):
        pass
    
    @abstractmethod
    def decodificar(self, sinal):
        pass
```

### 4. **Observer** (Logs)
Interface notifica sobre mudanças de estado.

### 5. **Facade** (Transmissor/Receptor)
Simplifica interface complexa do subsistema.

---

## 🚀 Casos de Uso

### Caso de Uso 1: Comparação de Modulações
**Objetivo:** Comparar largura de banda de NRZ vs Manchester

**Passos:**
1. Configurar NRZ-Polar, transmitir "Test"
2. Observar espectro (largura de banda B1)
3. Configurar Manchester, transmitir "Test"
4. Observar espectro (largura de banda B2 ≈ 2×B1)

**Resultado Esperado:** Manchester ocupa o dobro da largura de banda.

---

### Caso de Uso 2: Análise de Impacto do Ruído
**Objetivo:** Determinar SNR mínimo para transmissão confiável

**Passos:**
1. Configurar sistema com Hamming + CRC
2. Transmitir mensagem com σ=0.1 (SNR alto)
3. Aumentar gradualmente σ até σ=2.0
4. Observar taxa de erros e mensagens corrompidas

**Resultado Esperado:** 
- σ < 0.5: 100% sucesso
- 0.5 < σ < 1.0: Hamming corrige alguns erros
- σ > 1.5: Mensagem completamente corrompida

---

### Caso de Uso 3: Teste de Técnicas de Detecção
**Objetivo:** Comparar eficácia de Paridade vs CRC

**Passos:**
1. Configurar Paridade, σ=0.5, transmitir 10 vezes
2. Anotar taxa de detecção de erros
3. Configurar CRC-32, σ=0.5, transmitir 10 vezes
4. Comparar taxas de detecção

**Resultado Esperado:** CRC detecta >99% dos erros, Paridade ~50%.

---

## 📝 Conclusão

O **Simulador TR1** oferece uma visão completa e prática de um sistema de comunicação digital, desde a geração do sinal até a recuperação da mensagem, passando por todas as etapas intermediárias. 

**Principais Contribuições:**
- ✅ Implementação educacional de conceitos de telecomunicações
- ✅ Visualização gráfica de sinais e espectros
- ✅ Experimentação com diferentes parâmetros
- ✅ Análise de impacto de ruído em comunicação
- ✅ Comparação de técnicas de detecção/correção de erros

**Público-Alvo:**
- Estudantes de Engenharia de Telecomunicações
- Profissionais de redes e comunicação
- Pesquisadores em sistemas digitais
- Entusiastas de processamento de sinais

---

**Desenvolvido para o curso de Telecomunicações (TR1) - Universidade de Brasília (UnB)**

**Versão:** 1.0  
**Data:** Novembro 2025  
**Licença:** Educacional
