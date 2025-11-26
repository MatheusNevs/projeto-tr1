# Simulador TR1 — Camada Física e Camada de Enlace

Simulador educacional de transmissão de dados, modelando **Camada Física** (modulação/demodulação) e **Camada de Enlace** (enquadramento, detecção e correção de erros).

---

## Funcionalidades

| Categoria | Opções |
|-----------|--------|
| **Modulação Digital** | NRZ-Polar, Manchester, Bipolar |
| **Modulação por Portadora** | ASK, FSK, QPSK, 16-QAM |
| **Enquadramento** | Contagem de caracteres, Flags com bit-stuffing |
| **Detecção de Erros** | Paridade, Checksum (8/16/24/32 bits), CRC (8/16/24/32 bits) |
| **Correção de Erros** | Código de Hamming (7,4) |
| **Canal** | Ruído gaussiano (AWGN) com média e desvio configuráveis |
| **Visualização** | Formas de onda TX/RX, Análise de espectro (FFT) |

---

## Estrutura do Projeto

```
projeto-tr1/
├── camada_fisica/
│   ├── modulador_digital.py    # NRZ-Polar, Manchester, Bipolar
│   └── modulador_portadora.py  # ASK, FSK, QPSK, 16-QAM
│
├── camada_enlace/
│   ├── enquadrador.py          # Contagem, Flags+BitStuffing
│   ├── detector_erros.py       # Paridade, Checksum, CRC
│   └── corretor_erros.py       # Hamming(7,4)
│
├── comunicacao/
│   ├── canal.py                # Canal AWGN
│   ├── transmissor.py          # Orquestra envio (TX)
│   └── receptor.py             # Orquestra recepção (RX)
│
├── interface/
│   └── gui.py                  # Interface gráfica Tkinter
│
├── utils/
│   └── conversor.py            # Texto ↔ Bits ↔ Bytes
│
├── docs/                       # Documentação detalhada
├── config.py                   # Configurações globais (Singleton)
├── main.py                     # Ponto de entrada
├── requirements.txt
└── README.md
```

---

## Como Executar

### Pré-requisitos

- Python 3.8+
- Dependências: `numpy`, `matplotlib`, `tkinter` (geralmente incluso)

```bash
pip install -r requirements.txt
```

### Iniciar o Simulador

```bash
python main.py
```

---

## Usando a Interface

A interface é dividida em **painel de controle** (esquerda) e **visualização de sinais** (direita).

### Painel de Controle

1. **Tipo de Modulação**: escolha entre Digital ou Portadora.
2. **Modulação**: selecione o algoritmo específico (ex.: NRZ-Polar, ASK).
3. **Enquadramento**: Contagem ou FLAGS Bits.
4. **Detecção de Erros**: Paridade, Checksum ou CRC (com tamanho configurável).
5. **Hamming**: ative/desative correção de erros.
6. **Parâmetros do canal**:
   - Taxa de Amostragem (Hz)
   - Taxa de Bits (bps)
   - Frequência da Portadora (Hz) — usado em modulação por portadora
   - Ruído: média (μ) e desvio (σ)
   - Tamanho máximo do quadro (bytes)
   - Tamanho do EDC (8/16/24/32 bits)
7. **Aplicar Configurações**: clique para efetivar as mudanças.
8. **Mensagem**: digite o texto a transmitir.
9. **Transmitir**: envia a mensagem pelo pipeline completo.
10. **Logs**: acompanhe cada etapa (TX → Canal → RX).

### Visualização

- **Aba Formas de Onda**: gráficos do sinal TX, sinal RX e comparação.
- **Aba Análise de Espectro**: FFT dos sinais TX e RX.

---

## Fluxo de Dados

```
           TRANSMISSOR
               │
   ┌───────────▼───────────┐
   │  Texto → Bits (8b/c)  │  Aplicação
   └───────────┬───────────┘
               │
   ┌───────────▼───────────┐
   │  Hamming (7,4) [opc]  │  Enlace – Correção
   └───────────┬───────────┘
               │
   ┌───────────▼───────────┐
   │  Detecção (EDC)       │  Enlace – Detecção
   └───────────┬───────────┘
               │
   ┌───────────▼───────────┐
   │  Enquadramento        │  Enlace – Enquadramento
   └───────────┬───────────┘
               │
   ┌───────────▼───────────┐
   │  Modulação            │  Física
   └───────────┬───────────┘
               │
        ┌──────▼──────┐
        │   CANAL     │  (ruído AWGN)
        └──────┬──────┘
               │
            RECEPTOR
               │
   ┌───────────▼───────────┐
   │  Demodulação          │  Física
   └───────────┬───────────┘
               │
   ┌───────────▼───────────┐
   │  Desenquadramento     │  Enlace
   └───────────┬───────────┘
               │
   ┌───────────▼───────────┐
   │  Verificação (EDC)    │  Enlace
   └───────────┬───────────┘
               │
   ┌───────────▼───────────┐
   │  Hamming (7,4) [opc]  │  Enlace – Correção
   └───────────┬───────────┘
               │
   ┌───────────▼───────────┐
   │  Bits → Texto         │  Aplicação
   └───────────────────────┘
```

---

## Testes Rápidos

Cada módulo possui um bloco de teste embutido:

```bash
# Moduladores
python -m camada_fisica.modulador_digital
python -m camada_fisica.modulador_portadora

# Enlace
python -m camada_enlace.enquadrador
python -m camada_enlace.detector_erros
python -m camada_enlace.corretor_erros
```

---

## Exemplo Programático

```python
from config import Config
from camada_fisica.modulador_portadora import ASK
from camada_enlace.enquadrador import EnquadradorContagem
from camada_enlace.detector_erros import DetectorCRCVariavel
from comunicacao.transmissor import Transmissor
from comunicacao.receptor import Receptor
from comunicacao.canal import CanalComunicacao

# Ajustar parâmetros globais
config = Config()
config.set_taxa_amostragem(1000)
config.set_taxa_bits(10)

# Criar componentes
modulador = ASK()
enquadrador = EnquadradorContagem()
detector = DetectorCRCVariavel(8)

tx = Transmissor(modulador, enquadrador, detector, usar_hamming=False)
rx = Receptor(modulador, enquadrador, detector, usar_hamming=False)
canal = CanalComunicacao(nivel_ruido=0.3)

# Transmitir
sinal = tx.transmitir("Oi")
sinal_rx = canal.transmitir(sinal)
msg = rx.receber(sinal_rx)

print("Recebido:", msg)
```

---

## Documentação Adicional

Veja a pasta `docs/` para informações detalhadas:

| Arquivo | Descrição |
|---------|-----------|
| `index.md` | Índice da documentação |
| `architecture.md` | Arquitetura e padrões |
| `modules.md` | Referência dos módulos |
| `how_to_run.md` | Como executar e depurar |
| `development.md` | Guia para desenvolvedores |
| `changelog.md` | Histórico de alterações |

---

## Requisitos

- Python 3.8+
- numpy
- matplotlib
- tkinter (geralmente já incluso)

Instale com:

```bash
pip install -r requirements.txt
```

---

## Licença

Projeto acadêmico — Universidade de Brasília, disciplina Teleinformática e Redes 1.
