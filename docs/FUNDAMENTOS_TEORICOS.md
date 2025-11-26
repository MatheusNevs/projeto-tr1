# 🎓 Fundamentos Teóricos - Simulador TR1

## Conceitos de Telecomunicações Implementados

Este documento explica os fundamentos teóricos por trás das técnicas implementadas no Simulador TR1, servindo como referência educacional para estudantes e profissionais.

---

## Índice

1. [Teoria da Informação](#teoria-da-informação)
2. [Modulação Digital](#modulação-digital)
3. [Modulação por Portadora](#modulação-por-portadora)
4. [Detecção de Erros](#detecção-de-erros)
5. [Correção de Erros](#correção-de-erros)
6. [Enquadramento](#enquadramento)
7. [Teoria de Canais](#teoria-de-canais)
8. [Análise de Sinais](#análise-de-sinais)

---

## Teoria da Informação

### Teorema de Nyquist

**Enunciado:**
> Para reconstruir perfeitamente um sinal analógico, a taxa de amostragem deve ser pelo menos o dobro da frequência máxima presente no sinal.

**Formulação Matemática:**
```
f_s >= 2 × f_max
```

Onde:
- `f_s` = Taxa de amostragem (Hz)
- `f_max` = Frequência máxima do sinal (Hz)

**Exemplo Prático:**
- Sinal com f_max = 100 Hz
- Requer f_s >= 200 Hz
- Recomendado: f_s = 1000 Hz (5× margem)

**Consequências de Violação:**
- **Aliasing:** Frequências altas parecem baixas
- **Distorção:** Sinal reconstruído incorreto
- **Perda de informação:** Irrecuperável

---

### Teorema de Shannon-Hartley

**Enunciado:**
> A capacidade máxima de um canal com ruído é limitada por sua largura de banda e relação sinal-ruído.

**Formulação Matemática:**
```
C = B × log₂(1 + SNR)
```

Onde:
- `C` = Capacidade do canal (bits/s)
- `B` = Largura de banda (Hz)
- `SNR` = Relação sinal-ruído (linear, não dB)

**Conversão SNR:**
```
SNR_linear = 10^(SNR_dB / 10)
```

**Exemplo:**
```
B = 1000 Hz
SNR = 20 dB → SNR_linear = 100

C = 1000 × log₂(1 + 100)
  = 1000 × log₂(101)
  = 1000 × 6.658
  ≈ 6658 bits/s
```

**Implicações:**
- Não é possível transmitir mais que C bits/s sem erros
- Aumentar SNR ou B aumenta capacidade
- Trade-off fundamental em comunicações

---

## Modulação Digital

### 1. NRZ-Polar (Non-Return-to-Zero)

**Princípio:**
Cada bit é representado por um nível de tensão constante durante todo o período do bit.

**Codificação:**
```
bit '1' → +V volts
bit '0' → -V volts
```

**Forma de Onda:**
```
Bits:    1    0    1    1    0
         ___       _____
Sinal:  |   |     |     |
        |   |_____|     |_____
       +V   -V    +V    -V
```

**Características:**

| Aspecto | Valor |
|---------|-------|
| Largura de banda | B = R_b (taxa de bits) |
| Potência DC | Presente se bits desbalanceados |
| Sincronização | Não fornece |
| Complexidade | Mínima |

**Densidade Espectral de Potência:**
```
S(f) = T_b × sinc²(πfT_b)
```

**Vantagens:**
- ✅ Implementação simples
- ✅ Mínima largura de banda
- ✅ Baixo custo

**Desvantagens:**
- ❌ Componente DC (se desbalanceado)
- ❌ Sem autossincronização
- ❌ Longas sequências de bits iguais problemáticas

---

### 2. Manchester (Biphase)

**Princípio:**
Cada bit tem uma transição no meio do período, garantindo sincronização.

**Codificação:**
```
bit '1' → transição baixo-alto (↗)
bit '0' → transição alto-baixo (↘)
```

**Forma de Onda:**
```
Bits:    1      0      1      0
         _↗__   __↘_   _↗__   __↘_
Sinal:  | |  | |  | | | |  | |  | |
        |_|  |_|  |_| |_|  |_|  |_|
```

**Características:**

| Aspecto | Valor |
|---------|-------|
| Largura de banda | B = 2 × R_b |
| Potência DC | Zero (sempre balanceado) |
| Sincronização | Excelente (transição garantida) |
| Complexidade | Média |

**Análise Matemática:**
```
s_Manchester(t) = s_NRZ(t) ⊕ clock(t)

Onde ⊕ é XOR
```

**Vantagens:**
- ✅ Autossincronizante
- ✅ Sem componente DC
- ✅ Fácil detecção de erros (transição ausente)
- ✅ Robusto

**Desvantagens:**
- ❌ Dobra a largura de banda
- ❌ Mais complexo que NRZ
- ❌ Maior consumo de energia

**Aplicações Reais:**
- Ethernet 10BASE-T (IEEE 802.3)
- RFID (Radio-Frequency Identification)
- Smart Cards

---

### 3. Bipolar AMI (Alternate Mark Inversion)

**Princípio:**
Bits '0' são representados por zero volt, e bits '1' alternam entre +V e -V.

**Codificação:**
```
bit '0' → 0V
bit '1' → +V, -V, +V, -V... (alternando)
```

**Forma de Onda:**
```
Bits:    1    0    1    1    0    1
         _              _         _
Sinal:  | |        |‾‾‾|    |   | |
        |_|________|   |____|___|_|
       +V  0V     -V   +V   0V  -V
```

**Características:**

| Aspecto | Valor |
|---------|-------|
| Largura de banda | B ≈ R_b |
| Potência DC | Zero (balanceado) |
| Sincronização | Parcial (só em '1's) |
| Complexidade | Média |

**Detecção de Violação:**
```
Se dois '1's consecutivos têm mesma polaridade:
  → ERRO detectado (Bipolar Violation)
```

**Vantagens:**
- ✅ Sem componente DC
- ✅ Detecta alguns erros (violações)
- ✅ Largura de banda razoável
- ✅ Usado em linhas de longa distância

**Desvantagens:**
- ❌ Longas sequências de '0's problemáticas
- ❌ Requer codificação adicional (scrambling)

**Aplicações Reais:**
- Linhas T1/E1 (1.544/2.048 Mbps)
- ISDN (Integrated Services Digital Network)
- Telefonia digital

---

## Modulação por Portadora

### Conceito Geral

**Modulação:**
> Processo de variar uma ou mais propriedades de uma onda portadora de alta frequência de acordo com o sinal de informação.

**Portadora:**
```
c(t) = A_c × cos(2πf_c × t + φ)

Onde:
  A_c = Amplitude da portadora
  f_c = Frequência da portadora
  φ = Fase da portadora
```

**Propriedades Moduláveis:**
1. **Amplitude** → ASK (Amplitude Shift Keying)
2. **Frequência** → FSK (Frequency Shift Keying)
3. **Fase** → PSK (Phase Shift Keying)
4. **Amplitude + Fase** → QAM (Quadrature Amplitude Modulation)

---

### 1. ASK (Amplitude Shift Keying)

**Princípio:**
Varia a amplitude da portadora conforme os bits.

**Formulação Matemática:**
```
s_ASK(t) = A_i × cos(2πf_c × t)

Onde A_i = {
  A_1  se bit = '1'
  A_0  se bit = '0'
}

Comumente: A_1 = A, A_0 = 0 (OOK - On-Off Keying)
```

**Forma de Onda:**
```
Bits:      1         0         1
           ___                ___
Portadora:|   |             |   |
          |   |_____________|   |___
          Alta  Baixa/Zero   Alta
```

**Detecção:**
```python
# Detector de Energia
energia = sum(sinal² × dt)
if energia > limiar:
    bit = 1
else:
    bit = 0
```

**Largura de Banda:**
```
B_ASK ≈ 2 × R_b
```

**Eficiência Espectral:**
```
η = R_b / B = 0.5 bits/s/Hz
```

**Vantagens:**
- ✅ Implementação simples
- ✅ Baixo custo
- ✅ Boa para fibra óptica

**Desvantagens:**
- ❌ Sensível a ruído de amplitude
- ❌ Sensível a desvanecimento
- ❌ Baixa eficiência espectral

**Aplicações:**
- Comunicação por fibra óptica (OOK)
- Infravermelho (IR)
- Comunicação de baixa taxa

---

### 2. FSK (Frequency Shift Keying)

**Princípio:**
Varia a frequência da portadora conforme os bits.

**Formulação Matemática:**
```
s_FSK(t) = A × cos(2πf_i × t)

Onde f_i = {
  f_1 = f_c + Δf  se bit = '1'
  f_0 = f_c - Δf  se bit = '0'
}
```

**Forma de Onda:**
```
Bits:      1              0
           ~~~~~~~~~~~    ~~~~~
Portadora: ~ freq alta ~  ~fr baixa~
          ~~~~~~~~~~~    ~~~~~
```

**Detecção (por Correlação):**
```python
# Correlação com frequências de referência
cor_1 = correlacao(sinal, cos(2π×f_1×t))
cor_0 = correlacao(sinal, cos(2π×f_0×t))

if cor_1 > cor_0:
    bit = 1
else:
    bit = 0
```

**Largura de Banda (Regra de Carson):**
```
B_FSK = 2(Δf + R_b)

Onde Δf = |f_1 - f_0| / 2
```

**Índice de Modulação:**
```
h = 2Δf × T_b

h < 1: Narrow-band FSK
h >= 1: Wide-band FSK
```

**Vantagens:**
- ✅ Robusto contra ruído de amplitude
- ✅ Baixa taxa de erro
- ✅ Funciona bem em canais ruidosos

**Desvantagens:**
- ❌ Maior largura de banda que ASK
- ❌ Mais complexo
- ❌ Requer sincronização de frequência

**Aplicações:**
- Modems de baixa velocidade
- Rádio amador
- Pagers
- Caller ID

---

### 3. QPSK (Quaternary Phase Shift Keying)

**Princípio:**
Usa 4 fases diferentes para representar 4 símbolos (2 bits cada).

**Mapeamento:**
```
00 → Fase 45°  (π/4)
01 → Fase 135° (3π/4)
11 → Fase 225° (5π/4)
10 → Fase 315° (7π/4)
```

**Formulação Matemática:**
```
s_QPSK(t) = A × cos(2πf_c × t + φ_i)

Onde φ_i ∈ {π/4, 3π/4, 5π/4, 7π/4}
```

**Representação em Constelação:**
```
     Q (Quadratura)
        ↑
   01   |   00
    •   |   •
  ------+------- I (In-phase)
    •   |   •
   11   |   10
```

**Decomposição I/Q:**
```
s(t) = I(t) × cos(2πf_c × t) - Q(t) × sin(2πf_c × t)

Onde:
  I(t) = componente em fase
  Q(t) = componente em quadratura
```

**Eficiência Espectral:**
```
η = 2 bits/símbolo
B_QPSK ≈ R_b (mesma que BPSK, mas 2× taxa)
```

**Vantagens:**
- ✅ Dobra taxa de bits sem aumentar largura de banda
- ✅ Boa eficiência espectral
- ✅ Robusto

**Desvantagens:**
- ❌ Mais complexo que ASK/FSK
- ❌ Requer sincronização de fase
- ❌ Sensível a variações de fase

**Aplicações:**
- Satélite (DVB-S)
- 3G/4G (UMTS, LTE)
- Wi-Fi (802.11)

---

### 4. QAM-16 (16-Quadrature Amplitude Modulation)

**Princípio:**
Combina modulação de amplitude e fase para criar 16 símbolos (4 bits cada).

**Constelação 16-QAM:**
```
     Q
     ↑
  •  •  •  •
  •  •  •  •
--+--------+-- I
  •  •  •  •
  •  •  •  •
```

**Mapeamento (Gray Coding):**
```
0000 → (-3, +3)
0001 → (-3, +1)
0011 → (-3, -1)
0010 → (-3, -3)
...
```

**Formulação Matemática:**
```
s_QAM(t) = I_k × cos(2πf_c × t) - Q_k × sin(2πf_c × t)

Onde I_k, Q_k ∈ {-3, -1, +1, +3} (normalizado)
```

**Distância Euclidiana:**
```
d_min = 2A (entre símbolos adjacentes)

Maior d_min → Menor probabilidade de erro
```

**Eficiência Espectral:**
```
η = 4 bits/símbolo
B_QAM16 ≈ R_b / 4
```

**Vantagens:**
- ✅ Altíssima eficiência espectral
- ✅ Alta taxa de dados
- ✅ Otimizado para canais de alta qualidade

**Desvantagens:**
- ❌ Muito sensível a ruído
- ❌ Requer SNR alto (>18 dB)
- ❌ Complexidade elevada
- ❌ Sincronização crítica

**Aplicações:**
- Wi-Fi 802.11n/ac (até 256-QAM)
- 4G/5G LTE
- TV digital (DVB-T/C)
- Modems de cabo

---

## Detecção de Erros

### 1. Paridade

**Princípio:**
Adiciona 1 bit para tornar o número total de '1's par (paridade par) ou ímpar (paridade ímpar).

**Algoritmo (Paridade Par):**
```python
def calcular_paridade(byte):
    num_uns = count_ones(byte)
    if num_uns % 2 == 0:
        return 0  # Já é par
    else:
        return 1  # Torna par
```

**Exemplo:**
```
Dados: 10110101 (5 uns - ímpar)
Bit de paridade: 1
Resultado: 10110101|1 (6 uns - par)
```

**Taxa de Detecção:**
```
Detecta: Número ímpar de erros
Não detecta: Número par de erros

Probabilidade de detecção ≈ 50%
```

**Overhead:**
```
Overhead = 1 bit / 8 bits = 12.5%
```

**Vantagens:**
- ✅ Extremamente simples
- ✅ Baixo overhead
- ✅ Rápido

**Desvantagens:**
- ❌ Baixa taxa de detecção
- ❌ Não detecta erros pares
- ❌ Não localiza erro

---

### 2. Checksum

**Princípio:**
Soma todos os bytes e transmite os bits menos significativos da soma como redundância.

**Algoritmo (Checksum de 16 bits):**
```python
def calcular_checksum(dados):
    soma = 0
    for byte in dados:
        soma += byte
        if soma > 0xFFFF:  # Overflow
            soma = (soma & 0xFFFF) + (soma >> 16)
    return ~soma & 0xFFFF  # Complemento de 1
```

**Exemplo:**
```
Dados: [0x25, 0xAB, 0x01, 0x05]
Soma: 0x25 + 0xAB + 0x01 + 0x05 = 0xD6
Checksum 16-bit: ~0x00D6 = 0xFF29
```

**Verificação:**
```python
def verificar(dados, checksum):
    soma_total = calcular_checksum(dados) + checksum
    return soma_total == 0xFFFF
```

**Taxa de Detecção:**
```
Detecta: ~95% dos erros aleatórios
Não detecta: Erros que se cancelam (raros)
```

**Vantagens:**
- ✅ Simples
- ✅ Boa detecção para erros aleatórios
- ✅ Usado em TCP/UDP

**Desvantagens:**
- ❌ Não detecta reordenação
- ❌ Não detecta erros múltiplos específicos
- ❌ Menos robusto que CRC

**Aplicações:**
- TCP/IP (RFC 1071)
- UDP
- ICMP

---

### 3. CRC (Cyclic Redundancy Check)

**Princípio:**
Trata os dados como um polinômio e realiza divisão polinomial por um polinômio gerador.

**Matemática:**
```
M(x) = mensagem como polinômio
G(x) = polinômio gerador
R(x) = resto da divisão M(x) × x^n / G(x)

CRC = coeficientes de R(x)
```

**Exemplo (CRC-8 com G(x) = x³+x²+1):**
```
Dados: 1101
G(x): 1101 (x³ + x² + 1)

1. Shift: 1101000 (dados × x³)
2. Dividir por 1101
3. Resto: 011
4. CRC = 011

Transmitir: 1101|011
```

**Polinômios Padrão:**

| CRC | Polinômio | Aplicação |
|-----|-----------|-----------|
| CRC-8 | x⁸+x²+x+1 | 1-Wire, Bluetooth |
| CRC-16 | x¹⁶+x¹⁵+x²+1 | USB, Modbus |
| CRC-24 | x²⁴+x²³+x⁶+x⁵+x+1 | FlexRay |
| CRC-32 | x³²+x²⁶+x²³+...+1 | Ethernet, ZIP |

**Implementação Eficiente (Tabela de Lookup):**
```python
def crc32(dados):
    crc = 0xFFFFFFFF
    for byte in dados:
        index = (crc ^ byte) & 0xFF
        crc = (crc >> 8) ^ tabela_crc32[index]
    return ~crc & 0xFFFFFFFF
```

**Taxa de Detecção:**
```
CRC-32:
- Todos os erros de burst <= 32 bits: 100%
- Erros aleatórios: 99.9999998%
- Erros de burst > 32 bits: 1 - 2^(-32)
```

**Vantagens:**
- ✅ Excelente detecção
- ✅ Detecta erros de burst
- ✅ Matemática sólida
- ✅ Padrão industrial

**Desvantagens:**
- ❌ Mais complexo
- ❌ Overhead variável
- ❌ Apenas detecta, não corrige

**Aplicações:**
- Ethernet (IEEE 802.3)
- USB
- SATA/SAS
- Compressão (ZIP, RAR)

---

## Correção de Erros

### Código de Hamming

**Princípio:**
Adiciona bits de paridade em posições estratégicas (potências de 2) para permitir localização e correção de 1 erro.

**Propriedade SECDED:**
- **SEC:** Single Error Correction (corrige 1 bit)
- **DED:** Double Error Detection (detecta 2 bits)

**Cálculo de Bits de Paridade:**
```
2^r >= m + r + 1

Onde:
  m = bits de dados
  r = bits de paridade
```

**Exemplos:**
```
m=4  → r=3  → n=7  (Hamming(7,4))
m=8  → r=4  → n=12 (Hamming(12,8))
m=16 → r=5  → n=21 (Hamming(21,16))
```

**Posicionamento:**
```
Posição:  1  2  3  4  5  6  7  8  9  10 11 12
Tipo:     P1 P2 D1 P4 D2 D3 D4 P8 D5 D6 D7 D8

P1 cobre posições com bit 0 = 1: 1,3,5,7,9,11
P2 cobre posições com bit 1 = 1: 2,3,6,7,10,11
P4 cobre posições com bit 2 = 1: 4,5,6,7,12
P8 cobre posições com bit 3 = 1: 8,9,10,11,12
```

**Algoritmo de Codificação:**
```python
def codificar_hamming(dados):
    # 1. Inserir dados nas posições corretas
    # 2. Calcular cada bit de paridade
    for i in [1, 2, 4, 8, ...]:  # Potências de 2
        paridade = calcular_paridade(posições_cobertas[i])
        codigo[i] = paridade
    return codigo
```

**Algoritmo de Decodificação:**
```python
def decodificar_hamming(codigo):
    # 1. Calcular síndrome
    sindrome = 0
    for i in [1, 2, 4, 8, ...]:
        if verificar_paridade(posições_cobertas[i]) == 1:
            sindrome += i
    
    # 2. Corrigir erro (se houver)
    if sindrome != 0:
        codigo[sindrome] ^= 1  # Inverte bit errado
    
    # 3. Extrair dados
    return extrair_dados(codigo)
```

**Síndrome e Localização:**
```
Síndrome = 0: Sem erros
Síndrome = k: Erro na posição k
```

**Exemplo Hamming(7,4):**
```
Dados: 1011

1. Posicionar:
   Pos: 1 2 3 4 5 6 7
   Val: _ _ 1 _ 0 1 1

2. Calcular P1 (pos 1,3,5,7):
   P1 ⊕ 1 ⊕ 0 ⊕ 1 = 0
   P1 = 0

3. Calcular P2 (pos 2,3,6,7):
   P2 ⊕ 1 ⊕ 1 ⊕ 1 = 1
   P2 = 1

4. Calcular P4 (pos 4,5,6,7):
   P4 ⊕ 0 ⊕ 1 ⊕ 1 = 0
   P4 = 0

Código: 0110011
```

**Capacidade de Correção:**
```
Hamming(7,4):
- Corrige 1 erro
- Detecta 2 erros
- Overhead: 3/4 = 75%

Hamming(127,120):
- Corrige 1 erro
- Detecta 2 erros
- Overhead: 7/120 = 5.8%
```

**Vantagens:**
- ✅ Corrige erros automaticamente
- ✅ Matemática elegante
- ✅ Overhead diminui com blocos maiores

**Desvantagens:**
- ❌ Só corrige 1 erro
- ❌ Overhead alto para blocos pequenos
- ❌ Não lida bem com erros de burst

**Extensões:**
- **Hamming Estendido:** Adiciona 1 bit para SECDED
- **Reed-Solomon:** Corrige múltiplos erros
- **Turbo Codes:** Usado em 4G/5G

---

## Enquadramento

### 1. Contagem de Bytes

**Princípio:**
O quadro começa com um campo indicando o número de bytes que seguem.

**Estrutura:**
```
┌──────────────┬─────────────────────┐
│ Tamanho (16) │   Dados (N bytes)   │
└──────────────┴─────────────────────┘
```

**Exemplo:**
```
Tamanho: 5 (0x0005)
Dados: "Hello"

Quadro: [0x00, 0x05, 'H', 'e', 'l', 'l', 'o']
```

**Desenquadramento:**
```python
def desenquadrar(stream):
    tamanho = ler_16_bits(stream[0:2])
    dados = stream[2:2+tamanho]
    return dados
```

**Overhead:**
```
Overhead = 16 bits fixos

Para 64 bytes: 16/512 = 3.1%
Para 1024 bytes: 16/8192 = 0.2%
```

**Problema:**
```
Se o campo tamanho for corrompido:
  → Todos os dados subsequentes são perdidos
  → Perda de sincronização
```

**Soluções:**
- Duplicar campo tamanho
- Adicionar checksum ao header
- Usar timeout de ressincronização

---

### 2. FLAGS com Bit Stuffing

**Princípio:**
Delimitar quadro com padrão especial (FLAG), e garantir que ele não apareça nos dados através de bit stuffing.

**FLAG Padrão:**
```
FLAG = 01111110 (0x7E)
```

**Regra de Bit Stuffing:**
```
Após 5 bits '1' consecutivos nos dados:
  → Inserir '0' (stuff bit)
```

**Exemplo de Stuffing:**
```
Dados originais: 01111111
                    ↓ (5 '1's)
Após stuffing:   011111011

Dados originais: 01111110  (FLAG!)
                    ↓
Após stuffing:   011111010
```

**Algoritmo de Stuffing:**
```python
def bit_stuffing(dados):
    resultado = []
    contador_uns = 0
    
    for bit in dados:
        resultado.append(bit)
        
        if bit == 1:
            contador_uns += 1
            if contador_uns == 5:
                resultado.append(0)  # Stuff
                contador_uns = 0
        else:
            contador_uns = 0
    
    return resultado
```

**Algoritmo de Destuffing:**
```python
def bit_destuffing(dados):
    resultado = []
    contador_uns = 0
    skip_next = False
    
    for bit in dados:
        if skip_next:
            skip_next = False
            contador_uns = 0
            continue  # Pula bit stuffed
        
        resultado.append(bit)
        
        if bit == 1:
            contador_uns += 1
            if contador_uns == 5:
                skip_next = True
        else:
            contador_uns = 0
    
    return resultado
```

**Quadro Completo:**
```
┌──────┬──────────────────────┬──────┐
│ FLAG │   Dados (stuffed)    │ FLAG │
└──────┴──────────────────────┴──────┘
 01111110                      01111110
```

**Overhead:**
```
Overhead médio: ~2-5%
Pior caso: Dados = 11111111... → 20% overhead
Melhor caso: Sem sequências de 5 '1's → 0% overhead
```

**Vantagens:**
- ✅ Ressincronização possível (procurar FLAG)
- ✅ Robusto
- ✅ Não depende de campo de tamanho

**Desvantagens:**
- ❌ Overhead variável
- ❌ Processamento bit a bit
- ❌ Complexidade maior

**Protocolos que Usam:**
- HDLC (High-Level Data Link Control)
- PPP (Point-to-Point Protocol)
- Ethernet (preâmbulo similar)

---

## Teoria de Canais

### Modelo AWGN

**AWGN:** Additive White Gaussian Noise

**Modelo Matemático:**
```
y(t) = x(t) + n(t)

Onde:
  x(t) = sinal transmitido
  n(t) = ruído gaussiano branco
  y(t) = sinal recebido
```

**Propriedades do Ruído:**
```
n(t) ~ N(μ, σ²)

μ = média (tipicamente 0)
σ² = variância (potência do ruído)
```

**Densidade de Probabilidade:**
```
f(n) = (1 / (σ√(2π))) × e^(-(n-μ)²/(2σ²))
```

**"Branco":**
> Todas as frequências têm a mesma densidade espectral de potência.
```
S_n(f) = N_0 / 2 (constante para todas as frequências)
```

### SNR (Signal-to-Noise Ratio)

**Definição:**
```
SNR = P_sinal / P_ruído

SNR_dB = 10 × log₁₀(SNR)
```

**Cálculo da Potência:**
```
P_sinal = E[x²(t)] = (1/T) ∫ x²(t) dt
P_ruído = E[n²(t)] = σ²
```

**Interpretação:**
```
SNR_dB > 30: Excelente (quase sem erros)
SNR_dB = 20-30: Muito bom
SNR_dB = 15-20: Bom
SNR_dB = 10-15: Aceitável
SNR_dB < 10: Ruim (muitos erros)
```

**Relação com BER:**
```
Para BPSK:
BER ≈ (1/2) × erfc(√(E_b/N_0))

Onde E_b/N_0 é SNR por bit
```

---

## Análise de Sinais

### Transformada de Fourier

**Propósito:**
Decompor sinal temporal em componentes de frequência.

**Transformada Contínua:**
```
X(f) = ∫ x(t) × e^(-j2πft) dt
```

**Transformada Discreta (DFT):**
```
X[k] = Σ x[n] × e^(-j2πkn/N)
       n=0 até N-1

Onde:
  N = número de amostras
  k = índice de frequência
```

**FFT (Fast Fourier Transform):**
- Algoritmo eficiente para calcular DFT
- Complexidade: O(N log N) em vez de O(N²)

**Implementação:**
```python
import numpy as np

# Calcular FFT
fft_resultado = np.fft.fft(sinal)
frequencias = np.fft.fftfreq(len(sinal), 1/taxa_amostragem)

# Magnitude
magnitude = np.abs(fft_resultado)

# Em dB
magnitude_db = 20 * np.log10(magnitude + 1e-10)
```

**Interpretação do Espectro:**

**Sinal NRZ:**
- Pico em DC (0 Hz)
- Componentes até ~taxa_bits Hz
- Forma sinc²

**Sinal Manchester:**
- Sem DC
- Pico em ~taxa_bits/2 Hz
- Largura de banda 2× NRZ

**Sinal ASK:**
- Pico em freq_portadora
- Largura ~2×taxa_bits
- Bandas laterais simétricas

---

## Referências

### Livros Clássicos
1. **"Communication Systems" - Simon Haykin**
   - Teoria completa de comunicações

2. **"Digital Communications" - John Proakis**
   - Matemática detalhada de modulações digitais

3. **"Error Control Coding" - Shu Lin, Daniel Costello**
   - Códigos de correção de erros

4. **"Computer Networks" - Andrew Tanenbaum**
   - Camada de enlace e protocolos

### Padrões (RFCs e IEEE)
- **RFC 1071:** Internet Checksum
- **IEEE 802.3:** Ethernet (CRC-32, Manchester)
- **ISO/IEC 13239:** HDLC (FLAGS, Bit Stuffing)
- **ITU-T G.711:** PCM Encoding

### Conceitos Fundamentais
- **Claude Shannon (1948):** Teoria da Informação
- **Richard Hamming (1950):** Código de Hamming
- **Harry Nyquist (1928):** Teorema de Amostragem

---

**Desenvolvido para fins educacionais - Simulador TR1**  
**Universidade de Brasília (UnB)**  
**Novembro 2024**
