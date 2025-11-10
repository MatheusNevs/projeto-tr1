# Trabalho TR1 - Simulador de Camadas de Rede (OOP)

## 📋 Visão Geral

Simulador completo de **Camada Física** e **Camada de Enlace** usando **Programação Orientada a Objetos**.

### Funcionalidades

✅ **Modulações Digitais**: NRZ-Polar, Manchester, Bipolar  
✅ **Modulações por Portadora**: ASK, FSK, QPSK, 16-QAM  
✅ **Enquadramento**: Contagem, FLAGS (bytes/bits)  
✅ **Detecção de Erros**: Paridade, Checksum, CRC-32  
✅ **Correção de Erros**: Código de Hamming  
✅ **Canal com Ruído**: Gaussiano (AWGN)  
✅ **Interface Gráfica**: Tkinter com threading

---

## 📁 Estrutura do Projeto

```
├── camada_fisica/              # Modulações
│   ├── __init__.py
│   ├── modulador_digital.py    # NRZ, Manchester, Bipolar (Pessoa 1)
│   └── modulador_portadora.py  # ASK, FSK, QPSK, QAM (Pessoa 2)
│
├── camada_enlace/              # Enquadramento e Erros
│   ├── __init__.py
│   ├── enquadrador.py          # 3 tipos (Pessoa 3)
│   ├── detector_erros.py       # Paridade, Checksum, CRC (Pessoa 3)
│   └── corretor_erros.py       # Hamming (Pessoa 4)
│
├── comunicacao/                # Sistema de Transmissão
│   ├── __init__.py
│   ├── canal.py                # Canal com ruído AWGN
│   ├── transmissor.py          # Coordena TX através das camadas
│   └── receptor.py             # Coordena RX através das camadas
│
├── interface/                  # Interface Gráfica
│   ├── __init__.py
│   └── gui.py                  # GUI Tkinter (Pessoa 4)
│
├── utils/                      # Utilitários
│   ├── __init__.py
│   └── conversor.py            # Conversão texto↔bits↔bytes
│
├── config.py                   # Configurações globais (Singleton)
├── main.py                     # Ponto de entrada
└── README.md                   # Este arquivo
```

---

## 🎯 Divisão de Tarefas

| Pessoa       | Arquivos                                                             | Responsabilidades                                       |
| ------------ | -------------------------------------------------------------------- | ------------------------------------------------------- |
| **Pessoa 1** | `camada_fisica/modulador_digital.py`                                 | Implementar NRZPolar, Manchester, Bipolar (6 métodos)   |
| **Pessoa 2** | `camada_fisica/modulador_portadora.py`                               | Implementar ASK, FSK, QPSK, QAM16 (8 métodos)           |
| **Pessoa 3** | `camada_enlace/enquadrador.py`<br>`camada_enlace/detector_erros.py`  | Implementar 3 enquadradores + 3 detectores (12 métodos) |
| **Pessoa 4** | `camada_enlace/corretor_erros.py`<br>`interface/gui.py`<br>`main.py` | Hamming, GUI, integração, testes, documentação          |

### Documentos de Apoio

Cada pessoa tem um guia detalhado:

- `guia_pessoa1_oop.md` - Modulações Digitais
- `guia_pessoa2_oop.md` - Modulações por Portadora
- `guia_pessoa3_oop.md` - Enquadramento e Detecção
- `guia_pessoa4_oop.md` - Hamming, Interface e Integração

---

## 🚀 Como Executar

### 1. Pré-requisitos

```bash
# Python 3.7+
python --version

# Instalar dependências
pip install -r requirements.txt
```

### 2. Executar o Simulador

```bash
python main.py
```

### 3. Usar a Interface

1. **Configurar**: Selecione modulação, enquadramento, detecção
2. **Ajustar Ruído**: Use o slider (σ de 0 a 2)
3. **Digitar Mensagem**: No campo de texto
4. **Transmitir**: Clique no botão "Transmitir"
5. **Ver Logs**: Acompanhe todo o processo

---

## 🔬 Como Testar

### Testes Individuais

Cada módulo pode ser testado isoladamente:

```bash
# Teste Pessoa 1
python -m camada_fisica.modulador_digital

# Teste Pessoa 2
python -m camada_fisica.modulador_portadora

# Teste Pessoa 3
python -m camada_enlace.enquadrador
python -m camada_enlace.detector_erros

# Teste Pessoa 4
python -m camada_enlace.corretor_erros
```

---

## 🏗️ Arquitetura

### Padrões de Design

1. **Strategy Pattern**: Diferentes algoritmos de modulação/enquadramento
2. **Abstract Base Classes**: Interface comum para famílias de classes
3. **Composition**: Transmissor/Receptor compõem seus módulos
4. **Singleton**: Configurações globais
5. **Observer/Threading**: Receptor em thread separada

### Fluxo de Dados

```
TRANSMISSOR
↓
[Aplicação] Texto → Bits
↓
[Enlace] Bits → Hamming (opcional)
↓
[Enlace] Bytes → Detecção de Erros
↓
[Enlace] Dados → Enquadramento
↓
[Física] Bits → Modulação Digital
↓
CANAL (adiciona ruído gaussiano)
↓
RECEPTOR
↓
[Física] Sinal → Demodulação → Bits
↓
[Enlace] Bits → Desenquadramento
↓
[Enlace] Dados → Verificação de Erros
↓
[Enlace] Bits → Hamming (opcional)
↓
[Aplicação] Bits → Texto
```

---

## 📝 Exemplo de Uso Programático

```python
from camada_fisica.modulador_digital import NRZPolar
from camada_enlace.enquadrador import EnquadradorContagem
from camada_enlace.detector_erros import DetectorCRC32
from comunicacao import Transmissor, Receptor, CanalComunicacao

# Criar componentes
modulador_tx = NRZPolar()
modulador_rx = NRZPolar()
enquadrador_tx = EnquadradorContagem()
enquadrador_rx = EnquadradorContagem()
detector_tx = DetectorCRC32()
detector_rx = DetectorCRC32()

# Criar TX e RX
tx = Transmissor(modulador_tx, enquadrador_tx, detector_tx, usar_hamming=True)
rx = Receptor(modulador_rx, enquadrador_rx, detector_rx, usar_hamming=True)

# Canal
canal = CanalComunicacao(nivel_ruido=0.3)

# Transmitir
sinal_tx = tx.transmitir("Hello World!")
sinal_rx = canal.transmitir(sinal_tx)
mensagem_rx = rx.receber(sinal_rx)

print(f"Recebido: {mensagem_rx}")
```

---

## 📚 Recursos de Estudo

### Modulação

- Material do Moodle sobre Modulação
- [Wikipedia: Modulação](https://pt.wikipedia.org/wiki/Modulação)

### Enquadramento

- Material do Moodle sobre Camada de Enlace
- Livro: Redes de Computadores (Tanenbaum)

### Detecção de Erros

- [Wikipedia: CRC](https://pt.wikipedia.org/wiki/CRC)
- [Wikipedia: Código de Hamming](https://pt.wikipedia.org/wiki/Código_de_Hamming)

---

## 🎓 Características do Código

### ✅ Boas Práticas

- **Docstrings** em todas as classes e métodos
- **Type hints** nas assinaturas
- **Comentários** explicativos
- **Testes** isolados por módulo
- **Modularidade** alta
- **Acoplamento** baixo

### ✅ Padrões Python

- PEP 8 (estilo de código)
- Classes abstratas (ABC)
- Properties e métodos privados
- Exception handling
