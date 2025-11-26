# 📡 Simulador TR1 - Sistema de Comunicação Digital

**Simulador educacional interativo** para estudo e experimentação com sistemas de comunicação digital, implementando técnicas de modulação, detecção/correção de erros, e visualização de sinais em tempo real.

## 🎯 O que é o Simulador TR1?

O Simulador TR1 é uma ferramenta educacional que permite transmitir mensagens de texto através de um sistema completo de comunicação digital, desde a conversão do texto em sinais elétricos até a recuperação da mensagem original, passando por um canal com ruído.

**Ideal para:**
- 📚 Estudantes de Engenharia de Telecomunicações
- 👨‍🏫 Professores que desejam demonstrar conceitos práticos
- 🔬 Pesquisadores estudando técnicas de comunicação
- 💡 Entusiastas de processamento de sinais

## ✨ Principais Funcionalidades

### 📊 Interface Gráfica Completa
- **Painel de Controle Intuitivo**: Configure todos os parâmetros com sliders e menus
- **Visualização em Tempo Real**: Observe os sinais transmitidos e recebidos
- **Análise de Espectro**: Veja a composição de frequências via FFT
- **Logs Detalhados**: Acompanhe cada etapa da transmissão

### 🔧 Técnicas de Modulação Implementadas

**Modulação Digital (Banda Base):**
- **NRZ-Polar**: Modulação simples e eficiente
- **Manchester**: Autossincronizante, usado em Ethernet
- **Bipolar (AMI)**: Balanceado em DC, usado em telefonia

**Modulação por Portadora:**
- **ASK**: Modulação por amplitude
- **FSK**: Modulação por frequência
- **QPSK**: Modulação por fase (2 bits/símbolo)
- **16-QAM**: Modulação em quadratura (4 bits/símbolo)

### 🛡️ Proteção Contra Erros

**Detecção de Erros:**
- **Paridade**: Detecção simples e rápida
- **Checksum**: Configurável (8/16/24/32 bits)
- **CRC**: Alta confiabilidade (8/16/24/32 bits), usado em Ethernet

**Correção de Erros:**
- **Código de Hamming**: Corrige 1 bit e detecta 2 bits de erro

### 📦 Enquadramento de Dados
- **Contagem de Bytes**: Overhead fixo, simples
- **FLAGS com Bit Stuffing**: Robusto, usado em HDLC/PPP

### 🌊 Simulação de Canal Realístico
- **Ruído AWGN**: Ruído branco gaussiano configurável
- **Parâmetros Ajustáveis**: Média (μ) e desvio padrão (σ)
- **Visualização de Degradação**: Compare sinal transmitido vs recebido

---



## 🚀 Como Começar

### Instalação

**1. Requisitos:**
- Python 3.8 ou superior
- Sistema operacional: Windows, Linux ou macOS

**2. Instalar dependências:**
```bash
pip install -r requirements.txt
```

As únicas dependências são:
- `numpy`: Cálculos científicos e FFT
- `matplotlib`: Visualização de gráficos
- `tkinter`: Interface gráfica (geralmente já vem com Python)

**3. Executar o simulador:**
```bash
python main.py
```

---

## 🖥️ Usando a Interface

### Quick Start - 3 Passos

**1. Configure** (painel esquerdo):
   - Escolha uma modulação (ex: NRZ-Polar)
   - Selecione detecção de erros (ex: CRC-32)
   - Clique em **"Aplicar Configurações"**

**2. Transmita** (campo de mensagem):
   - Digite uma mensagem (ex: "Hello TR1!")
   - Clique em **"Transmitir"**

**3. Observe** (painéis direitos):
   - **Aba "Formas de Onda"**: Veja os sinais TX e RX
   - **Aba "Análise de Espectro"**: Observe a FFT
   - **Logs**: Acompanhe o processamento completo

### Layout da Interface

```
┌────────────────────────────────────────────────────────┐
│  [Configurações]       │   [Visualização]              │
│                        │                               │
│  • Tipo Modulação      │   📊 Gráficos de Sinais       │
│  • Enquadramento       │   📈 Análise FFT              │
│  • Detecção Erros      │   🔍 Ferramentas Zoom         │
│  • Hamming             │                               │
│  • Parâmetros          │                               │
│                        │                               │
│  [Transmissão]         │                               │
│  Mensagem: [____]      │                               │
│  [Transmitir]          │                               │
│                        │                               │
│  [Logs]                │                               │
│  ═══════════════       │                               │
│  TX: Hello             │                               │
│  Canal: σ=0.3          │                               │
│  RX: Hello             │                               │
│  ✓ Sucesso!            │                               │
│  [Limpar Logs]         │                               │
└────────────────────────────────────────────────────────┘
```

### Configurações Principais

| Parâmetro | Descrição | Valores Típicos |
|-----------|-----------|-----------------|
| **Taxa de Amostragem** | Frequência de captura do sinal | 1000 Hz |
| **Taxa de Bits** | Velocidade de transmissão | 10 bps |
| **Ruído (σ)** | Intensidade do ruído no canal | 0 (perfeito) a 2 (muito ruidoso) |
| **Código de Hamming** | Ativar correção automática | ☑ / ☐ |
| **Tamanho EDC** | Bits de detecção de erro | 8, 16, 24 ou 32 bits |

---

## 🧪 Experimentos Sugeridos

### 1. Comparando Modulações
- Configure **NRZ-Polar** e transmita "Test"
- Observe a largura de banda no espectro
- Mude para **Manchester** e repita
- Compare: Manchester usa o dobro da largura de banda

### 2. Efeito do Ruído
- Comece com **σ=0** (sem ruído) → 100% sucesso
- Aumente gradualmente para **σ=0.5** → alguns erros
- Teste **σ=1.5** → mensagem corrompida
- Observe como o Hamming ajuda a corrigir erros

### 3. Eficiência de Detecção
- Configure **Paridade** com σ=0.5
- Faça 10 transmissões e conte sucessos
- Mude para **CRC-32** e repita
- Compare: CRC detecta >99% dos erros

### 4. Análise de Espectro
- Use **ASK** com frequência portadora de 100 Hz
- Vá para aba "Análise de Espectro"
- Observe o pico em 100 Hz (a portadora)
- Compare com modulação digital (sem portadora)

---

## 📚 Documentação Completa

O projeto inclui documentação técnica detalhada na pasta `docs/`:

| Documento | Conteúdo | Para Quem |
|-----------|----------|-----------|
| **[README.md](docs/README.md)** | Índice e navegação | Todos |
| **[ARQUITETURA.md](docs/ARQUITETURA.md)** | Visão do sistema em camadas, fluxo de dados, padrões de design | Desenvolvedores, Estudantes |
| **[FUNDAMENTOS_TEORICOS.md](docs/FUNDAMENTOS_TEORICOS.md)** | Teoria completa, fórmulas matemáticas, conceitos de telecomunicações | Estudantes, Professores |

**Acesso rápido:**
```bash
cd docs/
cat ARQUITETURA.md          # Arquitetura do sistema
cat FUNDAMENTOS_TEORICOS.md # Base teórica
```

---

## 🎓 Sobre o Projeto

**Desenvolvido para:** Disciplina de Teleinformática e Redes 1 (TR1)  
**Instituição:** Universidade de Brasília (UnB)  
**Propósito:** Educacional - demonstração prática de sistemas de comunicação digital  
**Versão:** 1.0  
**Ano:** 2025

### Tecnologias Utilizadas
- **Python 3.8+**: Linguagem principal
- **NumPy**: Processamento de sinais e FFT
- **Matplotlib**: Visualização de gráficos
- **Tkinter**: Interface gráfica

### Conceitos Implementados
- Teorema de Nyquist (amostragem)
- Teorema de Shannon (capacidade de canal)
- Modulações digitais e por portadora
- Códigos de detecção e correção de erros
- Enquadramento de dados
- Canal AWGN (ruído gaussiano)

---

**Bons experimentos! 🚀📡**
