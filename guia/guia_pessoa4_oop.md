# Guia da Pessoa 4 - Integração, Hamming e Interface (Arquitetura OOP)

## 📁 Seus Arquivos

**Caminhos:**

- `camada_enlace/corretor_erros.py`
- `interface/gui.py`
- `main.py`
- Integração geral do projeto

## 🎯 Suas Responsabilidades

1. **Implementar Código de Hamming** (`corretor_erros.py`)
2. **Melhorar/Ajustar Interface Gráfica** (`gui.py`)
3. **Testar integração completa** de todos os módulos
4. **Criar arquivo principal** (`main.py`)
5. **Documentar** o projeto
6. **Coordenar** a equipe

---

## 📚 Conceitos Básicos

### O que é Código de Hamming?

É um código de **correção de erros** que adiciona bits de paridade em posições estratégicas.

**Diferença para detecção:**

- Detecção: apenas **detecta** se há erro
- Correção: detecta **e corrige** o erro automaticamente

### Como funciona?

1. Bits de paridade ficam nas posições que são **potências de 2** (1, 2, 4, 8, 16...)
2. Cada bit de paridade verifica um conjunto específico de posições
3. Ao receber, calcula-se a **síndrome** (posição do erro)
4. Se síndrome ≠ 0, inverte o bit errado

**Exemplo:**

```
Dados: [1, 0, 1, 1]  (4 bits)
Precisa: 3 bits de paridade (r=3)
Total: 7 bits

Posições: 1  2  3  4  5  6  7
          P1 P2 D1 P4 D2 D3 D4

P1 verifica: 1, 3, 5, 7
P2 verifica: 2, 3, 6, 7
P4 verifica: 4, 5, 6, 7
```

---

## 📝 PARTE 1: Código de Hamming

### Arquivo: `corretor_erros.py`

```python
"""
Corretor de erros usando Código de Hamming
Pessoa 4: Implementar esta classe
"""

class CorretorHamming:
    """
    Implementa código de Hamming (7,4) e variações
    Pode detectar e corrigir 1 erro por bloco
    """

    def calcular_bits_paridade(self, tamanho_dados: int) -> int:
        """
        Calcula quantos bits de paridade são necessários

        Fórmula: 2^r >= m + r + 1
        onde r = bits de paridade, m = bits de dados

        Exemplo:
            4 bits de dados → precisa 3 bits de paridade
            8 bits de dados → precisa 4 bits de paridade
        """
        r = 0
        while (2 ** r) < (tamanho_dados + r + 1):
            r += 1
        return r

    def codificar(self, dados_bits: list) -> list:
        """
        TODO: Implementar codificação Hamming

        Args:
            dados_bits: Lista com bits de dados [1, 0, 1, 1]

        Returns:
            Lista com bits codificados (dados + paridade)

        Algoritmo:
            1. Calcular quantos bits de paridade precisa (r)
            2. Criar array de tamanho m + r (inicializado com 0)
            3. Posições de paridade: 1, 2, 4, 8, ... (potências de 2)
            4. Colocar dados nas posições NÃO-potência-de-2
            5. Calcular cada bit de paridade:
               - P1 (pos 1): verifica pos 1,3,5,7,9,11...
               - P2 (pos 2): verifica pos 2,3,6,7,10,11...
               - P4 (pos 4): verifica pos 4,5,6,7,12,13...
               - etc
            6. Retornar array completo

        Dica: Use operação & (AND) para verificar se posição
              tem bit de paridade setado
        """
        m = len(dados_bits)
        r = self.calcular_bits_paridade(m)
        n = m + r

        # Cria array (índice 1 a n, ignora posição 0)
        hamming = [0] * (n + 1)

        # Insere dados nas posições não-potência-de-2
        j = 0
        for i in range(1, n + 1):
            # Verifica se i é potência de 2
            if (i & (i - 1)) != 0:  # NÃO é potência de 2
                if j < len(dados_bits):
                    hamming[i] = dados_bits[j]
                    j += 1

        # Calcula bits de paridade
        for i in range(r):
            pos_paridade = 2 ** i  # 1, 2, 4, 8, ...
            paridade = 0

            # Verifica todas as posições que têm bit i setado
            for j in range(1, n + 1):
                if j & pos_paridade:  # Se posição j tem bit i
                    paridade ^= hamming[j]  # XOR

            hamming[pos_paridade] = paridade

        return hamming[1:]  # Remove índice 0

    def decodificar(self, hamming_bits: list) -> tuple:
        """
        TODO: Implementar decodificação e correção

        Args:
            hamming_bits: Bits codificados (possivelmente com erro)

        Returns:
            (dados_originais, posicao_erro)
            posicao_erro = 0 se não há erro

        Algoritmo:
            1. Calcular síndrome (posição do erro)
               - Para cada bit de paridade:
                 - Recalcular paridade
                 - Se diferente da recebida: adicionar à síndrome
            2. Se síndrome != 0:
               - Inverter bit na posição síndrome
            3. Extrair dados (posições não-potência-de-2)
            4. Retornar (dados, síndrome)

        Exemplo de cálculo de síndrome:
            Se P1 errado: síndrome += 1
            Se P2 errado: síndrome += 2
            Se P1 e P4 errados: síndrome += 1 + 4 = 5
            → Erro está na posição 5
        """
        n = len(hamming_bits)
        hamming = [0] + hamming_bits  # Adiciona índice 0

        # Calcula número de bits de paridade
        r = 0
        while (2 ** r) < (n + 1):
            r += 1

        # Calcula síndrome
        sindrome = 0
        for i in range(r):
            pos_paridade = 2 ** i
            paridade = 0

            for j in range(1, n + 1):
                if j & pos_paridade:
                    paridade ^= hamming[j]

            # Se paridade incorreta, adiciona à síndrome
            if paridade != 0:
                sindrome += pos_paridade

        # Corrige erro se houver
        if sindrome != 0 and sindrome <= n:
            hamming[sindrome] ^= 1  # Inverte bit errado

        # Extrai dados (posições não-potência-de-2)
        dados = []
        for i in range(1, n + 1):
            if (i & (i - 1)) != 0:  # NÃO é potência de 2
                dados.append(hamming[i])

        return dados, sindrome

    def adicionar(self, dados: list) -> list:
        """
        Adiciona código de Hamming a uma lista de bytes
        Processa em blocos de 4 bits

        Args:
            dados: Lista de bytes [65, 66, 67, ...]

        Returns:
            Lista de bits com Hamming aplicado
        """
        # Converte bytes para bits
        todos_bits = []
        for byte in dados:
            bits = [int(b) for b in format(byte, '08b')]
            todos_bits.extend(bits)

        # Processa em blocos de 4 bits
        hamming_completo = []
        for i in range(0, len(todos_bits), 4):
            bloco = todos_bits[i:i+4]

            # Preenche com zeros se necessário
            if len(bloco) < 4:
                bloco.extend([0] * (4 - len(bloco)))

            # Codifica bloco
            hamming_bloco = self.codificar(bloco)
            hamming_completo.extend(hamming_bloco)

        return hamming_completo

    def verificar(self, hamming_bits: list) -> tuple:
        """
        Verifica e corrige dados com Hamming

        Args:
            hamming_bits: Bits com código de Hamming

        Returns:
            (dados_bytes, numero_erros_corrigidos)
        """
        dados_bits = []
        erros_corrigidos = 0

        # Processa em blocos de 7 bits (Hamming de 4 bits)
        for i in range(0, len(hamming_bits), 7):
            bloco = hamming_bits[i:i+7]

            if len(bloco) == 7:
                dados, erro = self.decodificar(bloco)
                dados_bits.extend(dados)

                if erro != 0:
                    erros_corrigidos += 1

        # Converte bits de volta para bytes
        dados_bytes = []
        for i in range(0, len(dados_bits), 8):
            byte_bits = dados_bits[i:i+8]
            if len(byte_bits) == 8:
                byte_val = int(''.join(map(str, byte_bits)), 2)
                dados_bytes.append(byte_val)

        return dados_bytes, erros_corrigidos
```

### Teste do Hamming:

```python
if __name__ == "__main__":
    print("="*70)
    print("TESTANDO CÓDIGO DE HAMMING - PESSOA 4")
    print("="*70)

    hamming = CorretorHamming()

    # Teste 1: Sem erro
    print("\n--- Teste 1: Sem erro ---")
    dados = [1, 0, 1, 1]
    cod = hamming.codificar(dados)
    print(f"Dados: {dados}")
    print(f"Codificado: {cod}")
    dec, erro = hamming.decodificar(cod)
    print(f"Decodificado: {dec}")
    print(f"Posição erro: {erro}")
    print(f"✓ OK" if dec == dados and erro == 0 else "✗ ERRO")

    # Teste 2: Com erro
    print("\n--- Teste 2: Com erro na posição 3 ---")
    cod_com_erro = cod.copy()
    cod_com_erro[2] ^= 1  # Inverte bit na posição 3 (índice 2)
    print(f"Codificado com erro: {cod_com_erro}")
    dec, erro = hamming.decodificar(cod_com_erro)
    print(f"Decodificado: {dec}")
    print(f"Posição erro: {erro}")
    print(f"✓ CORRIGIDO!" if dec == dados and erro == 3 else "✗ NÃO CORRIGIU")

    # Teste 3: Com bytes
    print("\n--- Teste 3: Bytes completos ---")
    dados_bytes = [65, 66]  # "AB"
    bits_hamming = hamming.adicionar(dados_bytes)
    print(f"Bytes: {dados_bytes}")
    print(f"Bits com Hamming: {len(bits_hamming)} bits")
    rec_bytes, erros = hamming.verificar(bits_hamming)
    print(f"Recuperados: {rec_bytes}")
    print(f"Erros corrigidos: {erros}")
    print(f"✓ OK" if rec_bytes == dados_bytes else "✗ ERRO")

    print("\n" + "="*70)
```

---

## 📝 PARTE 2: Interface Gráfica

### Arquivo: `gui.py`

A interface já está implementada! Suas tarefas:

1. **Testar** todos os componentes
2. **Adicionar melhorias** (opcional):

   - Gráfico do sinal (matplotlib)
   - Estatísticas (BER, taxa de erro)
   - Histórico de transmissões
   - Salvar/carregar configurações

3. **Garantir thread-safety**:
   - Usar `self.root.after()` para atualizações de GUI
   - Não chamar métodos Tk direto de threads

### Melhorias Sugeridas:

```python
# Em gui.py, adicionar métodos:

def adicionar_grafico_sinal(self):
    """
    OPCIONAL: Adicionar visualização do sinal
    Requer: pip install matplotlib
    """
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

    # Criar figura
    fig, ax = plt.subplots(figsize=(8, 3))
    canvas = FigureCanvasTkAgg(fig, master=self.root)
    canvas.get_tk_widget().grid(...)

    # Plotar sinal quando transmitir
    # ax.plot(sinal_tx)
    # canvas.draw()

def adicionar_estatisticas(self):
    """
    OPCIONAL: Mostrar estatísticas da comunicação
    """
    frame_stats = ttk.LabelFrame(self.root, text="Estatísticas")

    # Labels para:
    # - Bits transmitidos
    # - Bits com erro
    # - Taxa de erro (BER)
    # - Erros corrigidos por Hamming
    pass

def salvar_configuracao(self):
    """
    OPCIONAL: Salvar configurações em arquivo JSON
    """
    import json
    config = {
        'modulacao': self.combo_modulacao.get(),
        'enquadramento': self.combo_enquadramento.get(),
        # ...
    }
    with open('config.json', 'w') as f:
        json.dump(config, f)
```

---

## 📝 PARTE 3: Arquivo Principal

### Arquivo: `main.py`

```python
#!/usr/bin/env python3
"""
Simulador de Camadas de Rede - TR1
Ponto de entrada do programa
Pessoa 4: Verificar e ajustar
"""

from interface import InterfaceGrafica
import sys

def verificar_dependencias():
    """Verifica se todas as dependências estão instaladas"""
    try:
        import numpy
        import tkinter
    except ImportError as e:
        print("ERRO: Dependência não instalada!")
        print(f"  {e}")
        print("\nInstale com: pip install numpy")
        sys.exit(1)

def main():
    """Função principal"""
    print("="*70)
    print("SIMULADOR DE CAMADAS DE REDE - TR1")
    print("Arquitetura Orientada a Objetos")
    print("="*70)
    print("\nIniciando interface gráfica...")
    print("Aguarde...\n")

    # Verifica dependências
    verificar_dependencias()

    # Cria e inicia interface
    try:
        app = InterfaceGrafica()
        app.iniciar()
    except KeyboardInterrupt:
        print("\n\nPrograma interrompido pelo usuário")
    except Exception as e:
        print(f"\n\nERRO FATAL: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
```

---

## 📝 PARTE 4: Testes de Integração

### Criar: `testes_integracao.py`

```python
"""
Testes de integração completos
Pessoa 4: Executar para validar tudo
"""

from camada_fisica.modulador_digital import NRZPolar
from camada_enlace.enquadrador import EnquadradorContagem
from camada_enlace.detector_erros import DetectorCRC32
from camada_enlace.corretor_erros import CorretorHamming
from comunicacao import Transmissor, Receptor, CanalComunicacao
from utils.conversor import Conversor

def teste_completo():
    """Teste end-to-end completo"""
    print("="*70)
    print("TESTE DE INTEGRAÇÃO COMPLETO")
    print("="*70)

    # Mensagem de teste
    mensagem = "Hello TR1!"
    print(f"\nMensagem original: '{mensagem}'")

    # Criar componentes
    modulador = NRZPolar()
    enquadrador = EnquadradorContagem()
    detector = DetectorCRC32()

    # Criar TX e RX
    tx = Transmissor(modulador, enquadrador, detector, usar_hamming=True)
    rx = Receptor(modulador, enquadrador, detector, usar_hamming=True)

    # Canal com ruído
    canal = CanalComunicacao(nivel_ruido=0.3)

    # Transmitir
    print("\n--- TRANSMISSÃO ---")
    sinal_tx = tx.transmitir(mensagem)
    print(f"Sinal gerado: {len(sinal_tx)} amostras")

    # Canal
    print("\n--- CANAL ---")
    sinal_rx = canal.transmitir(sinal_tx)
    print("Sinal atravessou canal com ruído")

    # Receber
    print("\n--- RECEPÇÃO ---")
    mensagem_rx = rx.receber(sinal_rx)

    # Resultado
    print("\n" + "="*70)
    print("RESULTADO")
    print("="*70)
    print(f"TX: '{mensagem}'")
    print(f"RX: '{mensagem_rx}'")
    print(f"\n{'✓ SUCESSO!' if mensagem == mensagem_rx else '✗ FALHOU!'}")
    print("="*70)

    return mensagem == mensagem_rx

if __name__ == "__main__":
    sucesso = teste_completo()
    sys.exit(0 if sucesso else 1)
```

Execute:

```bash
python testes_integracao.py
```

---

## ✅ Checklist de Integração

### Código

- [ ] `CorretorHamming` implementado e testado
- [ ] Interface gráfica funcional
- [ ] `main.py` criado
- [ ] Testes de integração passam
- [ ] Todos os módulos importam corretamente

### Testes

- [ ] Teste com NRZ-Polar
- [ ] Teste com Manchester
- [ ] Teste com Bipolar
- [ ] Teste com diferentes níveis de ruído (0.0 a 2.0)
- [ ] Teste com diferentes enquadramentos
- [ ] Teste com diferentes detectores
- [ ] Teste com Hamming ligado/desligado

### Documentação

- [ ] README.md atualizado
- [ ] Comentários nos arquivos
- [ ] Guias das pessoas revisados
- [ ] Relatório iniciado

---

**Boa sorte!** 🚀💪
