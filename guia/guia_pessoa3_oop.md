# Guia da Pessoa 3 - Camada de Enlace (Arquitetura OOP)

## 📁 Seus Arquivos

**Caminhos:**

- `camada_enlace/enquadrador.py`
- `camada_enlace/detector_erros.py`

## 🎯 Suas Responsabilidades

### Arquivo 1: `enquadrador.py`

Implementar **3 classes de enquadramento**:

1. **EnquadradorContagem** - Contagem de caracteres
2. **EnquadradorFlagsBytes** - FLAGS com inserção de bytes
3. **EnquadradorFlagsBits** - FLAGS com inserção de bits

### Arquivo 2: `detector_erros.py`

Implementar **3 classes de detecção de erros**:

1. **DetectorParidade** - Bit de paridade par
2. **DetectorChecksum** - Soma de verificação
3. **DetectorCRC32** - Cyclic Redundancy Check 32 bits

Cada classe precisa de 2 métodos:

- `adicionar()` ou `enquadrar()` - Adiciona informação de controle
- `verificar()` ou `desenquadrar()` - Remove e valida

---

## 📚 Conceitos Básicos

### O que é Enquadramento?

É o processo de **delimitar** onde começa e termina um quadro (frame) na sequência de dados.

**Por quê?**

- O receptor precisa saber onde cada mensagem começa/termina
- Sem delimitação, dados ficam "grudados"

### O que é Detecção de Erros?

Adiciona **bits redundantes** para detectar se houve corrupção na transmissão.

**Por quê?**

- Canais físicos introduzem ruído
- Bits podem ser corrompidos (0→1 ou 1→0)
- Precisamos saber se dados chegaram corretos

---

## 📝 PARTE 1: Enquadramento

### Arquivo: `enquadrador.py`

```python
from abc import ABC, abstractmethod
from config import Config

class Enquadrador(ABC):
    """Classe abstrata - NÃO MEXER"""

    @abstractmethod
    def enquadrar(self, dados: list) -> list:
        """Adiciona delimitadores aos dados"""
        pass

    @abstractmethod
    def desenquadrar(self, quadro: list) -> list:
        """Remove delimitadores e retorna dados"""
        pass


# ==============================================================
# SUAS IMPLEMENTAÇÕES - ENQUADRAMENTO
# ==============================================================

class EnquadradorContagem(Enquadrador):
    """
    Enquadramento por contagem de caracteres
    Formato: [tamanho][dados...]
    """

    def enquadrar(self, dados: list) -> list:
        """
        TODO: Implementar

        Algoritmo:
            1. Contar quantos bytes há em dados
            2. Adicionar esse número no início
            3. Retornar [tamanho] + dados

        Exemplo:
            dados = [65, 66, 67]  # "ABC"
            resultado = [3, 65, 66, 67]
                         ^
                         tamanho
        """
        tamanho = len(dados)
        return [tamanho] + dados

    def desenquadrar(self, quadro: list) -> list:
        """
        TODO: Implementar

        Algoritmo:
            1. Ler primeiro byte (tamanho)
            2. Extrair os próximos 'tamanho' bytes
            3. Retornar esses bytes

        Exemplo:
            quadro = [3, 65, 66, 67]
            resultado = [65, 66, 67]
        """
        if len(quadro) < 1:
            return []

        tamanho = quadro[0]
        dados = quadro[1:tamanho+1]
        return dados


class EnquadradorFlagsBytes(Enquadrador):
    """
    Enquadramento com FLAGS e inserção de bytes
    Formato: [FLAG][dados com escape][FLAG]

    Se dados contêm FLAG ou ESC, insere ESC antes
    """

    def __init__(self):
        config = Config()
        self.flag = config.BYTE_FLAG  # 0x7E
        self.esc = config.BYTE_ESC    # 0x7D

    def enquadrar(self, dados: list) -> list:
        """
        TODO: Implementar

        Algoritmo:
            1. Adicionar FLAG inicial
            2. Para cada byte em dados:
               - Se byte == FLAG ou byte == ESC:
                 - Adicionar ESC
               - Adicionar byte
            3. Adicionar FLAG final

        Exemplo:
            dados = [65, 126, 67]  # 126 = 0x7E (FLAG)
            resultado = [126, 65, 125, 126, 67, 126]
                         FLAG    ESC FLAG      FLAG
        """
        quadro = [self.flag]  # FLAG inicial

        for byte in dados:
            if byte == self.flag or byte == self.esc:
                # Insere byte de escape antes
                quadro.append(self.esc)
            quadro.append(byte)

        quadro.append(self.flag)  # FLAG final
        return quadro

    def desenquadrar(self, quadro: list) -> list:
        """
        TODO: Implementar

        Algoritmo:
            1. Ignorar FLAGS inicial e final
            2. Para cada byte entre as FLAGS:
               - Se encontrar ESC: próximo byte é dado
               - Senão: byte é dado
            3. Retornar dados
        """
        if len(quadro) < 2:
            return []

        dados = []
        i = 1  # Pula FLAG inicial

        while i < len(quadro) - 1:  # Para antes da FLAG final
            if quadro[i] == self.esc:
                # Próximo byte é um dado, não um controle
                i += 1
                if i < len(quadro) - 1:
                    dados.append(quadro[i])
            else:
                dados.append(quadro[i])
            i += 1

        return dados


class EnquadradorFlagsBits(Enquadrador):
    """
    Enquadramento com FLAGS e inserção de bits (bit stuffing)
    Formato: [FLAG][bits com stuffing][FLAG]

    FLAG: 01111110
    Se aparecem 5 uns consecutivos nos dados → insere um 0
    """

    def __init__(self):
        self.flag = [0, 1, 1, 1, 1, 1, 1, 0]  # 01111110

    def enquadrar(self, bits: list) -> list:
        """
        TODO: Implementar bit stuffing

        Algoritmo:
            1. Adicionar FLAG inicial
            2. Contador de uns = 0
            3. Para cada bit em dados:
               - Adicionar bit ao quadro
               - Se bit == 1:
                 - Incrementar contador
                 - Se contador == 5:
                   - Adicionar 0 (stuffing)
                   - Resetar contador
               - Se bit == 0:
                 - Resetar contador
            4. Adicionar FLAG final

        Exemplo:
            bits = [1, 1, 1, 1, 1, 1, 0]
            depois stuffing: [1, 1, 1, 1, 1, 0, 1, 0]
                                           ^ inserido
        """
        quadro = self.flag.copy()
        contador_uns = 0

        for bit in bits:
            quadro.append(bit)

            if bit == 1:
                contador_uns += 1
                # Se acumulou 5 uns, insere um 0
                if contador_uns == 5:
                    quadro.append(0)
                    contador_uns = 0
            else:
                contador_uns = 0

        quadro.extend(self.flag)
        return quadro

    def desenquadrar(self, quadro: list) -> list:
        """
        TODO: Implementar destuffing

        Algoritmo:
            1. Remover FLAGS inicial e final
            2. Contador de uns = 0
            3. Para cada bit:
               - Adicionar bit aos dados
               - Se bit == 1:
                 - Incrementar contador
                 - Se contador == 5:
                   - Próximo bit (0) deve ser REMOVIDO
                   - Resetar contador
               - Se bit == 0:
                 - Resetar contador
            4. Retornar dados
        """
        tam_flag = len(self.flag)
        if len(quadro) <= 2 * tam_flag:
            return []

        # Remove FLAGS
        bits = quadro[tam_flag:-tam_flag]

        # Destuffing
        dados = []
        contador_uns = 0
        i = 0

        while i < len(bits):
            bit = bits[i]
            dados.append(bit)

            if bit == 1:
                contador_uns += 1
                # Se acumulou 5 uns, próximo bit (0) deve ser removido
                if contador_uns == 5:
                    i += 1  # Pula o 0 inserido
                    contador_uns = 0
            else:
                contador_uns = 0

            i += 1

        return dados
```

---

## 📝 PARTE 2: Detecção de Erros

### Arquivo: `detector_erros.py`

```python
from abc import ABC, abstractmethod
from config import Config

class DetectorErros(ABC):
    """Classe abstrata - NÃO MEXER"""

    @abstractmethod
    def adicionar(self, dados: list) -> list:
        """Adiciona bits/bytes de verificação"""
        pass

    @abstractmethod
    def verificar(self, dados_com_verificacao: list) -> tuple:
        """Retorna (dados_originais, tem_erro: bool)"""
        pass


# ==============================================================
# SUAS IMPLEMENTAÇÕES - DETECÇÃO DE ERROS
# ==============================================================

class DetectorParidade(DetectorErros):
    """
    Detector de paridade par
    Adiciona 1 bit de paridade a cada byte
    """

    def adicionar(self, dados: list) -> list:
        """
        TODO: Implementar

        Algoritmo:
            Para cada byte:
                1. Converter byte para 8 bits
                2. Contar quantos 1s existem
                3. Se ímpar: paridade = 1
                   Se par: paridade = 0
                4. Adicionar [byte, paridade] ao resultado

        Exemplo:
            dados = [10]
            10 em binário = 00001010 (tem 2 uns → par)
            paridade = 0
            resultado = [10, 0]
        """
        dados_com_paridade = []

        for byte in dados:
            # Converte byte para bits
            bits = [int(b) for b in format(byte, '08b')]

            # Calcula paridade (número de 1s módulo 2)
            paridade = sum(bits) % 2

            # Adiciona byte e paridade
            dados_com_paridade.extend([byte, paridade])

        return dados_com_paridade

    def verificar(self, dados_com_paridade: list) -> tuple:
        """
        TODO: Implementar

        Algoritmo:
            Processar de 2 em 2 (byte, paridade):
                1. Calcular paridade esperada
                2. Comparar com paridade recebida
                3. Se diferente: erro detectado

        Returns:
            (dados_originais, tem_erro: bool)
        """
        dados = []
        tem_erro = False

        for i in range(0, len(dados_com_paridade), 2):
            if i + 1 < len(dados_com_paridade):
                byte = dados_com_paridade[i]
                paridade_recebida = dados_com_paridade[i + 1]

                # Calcula paridade esperada
                bits = [int(b) for b in format(byte, '08b')]
                paridade_esperada = sum(bits) % 2

                if paridade_recebida != paridade_esperada:
                    tem_erro = True

                dados.append(byte)

        return dados, tem_erro


class DetectorChecksum(DetectorErros):
    """
    Detector por checksum (soma de verificação)
    Adiciona 1 byte ao final
    """

    def adicionar(self, dados: list) -> list:
        """
        TODO: Implementar

        Algoritmo:
            1. Somar todos os bytes (módulo 256)
            2. Checksum = (255 - soma) % 256 (complemento de 1)
            3. Adicionar checksum ao final

        Exemplo:
            dados = [10, 20, 30]
            soma = 60
            checksum = 255 - 60 = 195
            resultado = [10, 20, 30, 195]
        """
        if len(dados) == 0:
            return [0]

        # Soma todos os bytes (módulo 256)
        soma = sum(dados) % 256

        # Complemento de 1
        checksum = (255 - soma) % 256

        return dados + [checksum]

    def verificar(self, dados_com_checksum: list) -> tuple:
        """
        TODO: Implementar

        Algoritmo:
            1. Separar dados do checksum (último byte)
            2. Calcular checksum dos dados
            3. Comparar com checksum recebido

        Returns:
            (dados_originais, tem_erro: bool)
        """
        if len(dados_com_checksum) < 1:
            return [], True

        dados = dados_com_checksum[:-1]
        checksum_recebido = dados_com_checksum[-1]

        # Calcula checksum
        soma = sum(dados) % 256
        checksum_calculado = (255 - soma) % 256

        tem_erro = (checksum_recebido != checksum_calculado)

        return dados, tem_erro


class DetectorCRC32(DetectorErros):
    """
    Detector CRC-32 (IEEE 802)
    Adiciona 4 bytes ao final
    Algoritmo usado em Ethernet, ZIP, PNG
    """

    def __init__(self):
        config = Config()
        self.polinomio = config.CRC32_POLYNOMIAL

        # Tabela CRC-32 simplificada (primeiros 16 valores)
        self.tabela = [
            0x00000000, 0x77073096, 0xEE0E612C, 0x990951BA,
            0x076DC419, 0x706AF48F, 0xE963A535, 0x9E6495A3,
            0x0EDB8832, 0x79DCB8A4, 0xE0D5E91E, 0x97D2D988,
            0x09B64C2B, 0x7EB17CBD, 0xE7B82D07, 0x90BF1D91
        ]

    def calcular_crc(self, dados: list) -> int:
        """
        TODO: Implementar cálculo CRC-32

        Algoritmo (simplificado):
            1. CRC = 0xFFFFFFFF (inicializa com todos 1s)
            2. Para cada byte:
               - índice = (CRC XOR byte) AND 0xFF
               - CRC = (CRC >> 8) XOR tabela[índice]
            3. CRC = CRC XOR 0xFFFFFFFF (inverte bits)

        Nota: Em produção, use biblioteca otimizada
        Esta é versão educacional simplificada
        """
        crc = 0xFFFFFFFF

        for byte in dados:
            indice = (crc ^ byte) & 0xFF
            if indice < len(self.tabela):
                crc = (crc >> 8) ^ self.tabela[indice]
            else:
                crc = (crc >> 8) ^ (byte & 0xFF)

        return crc ^ 0xFFFFFFFF

    def adicionar(self, dados: list) -> list:
        """
        Adiciona CRC-32 (4 bytes) aos dados
        """
        crc = self.calcular_crc(dados)

        # Converte CRC-32 (32 bits) em 4 bytes
        crc_bytes = [
            (crc >> 24) & 0xFF,  # Byte mais significativo
            (crc >> 16) & 0xFF,
            (crc >> 8) & 0xFF,
            crc & 0xFF           # Byte menos significativo
        ]

        return dados + crc_bytes

    def verificar(self, dados_com_crc: list) -> tuple:
        """
        Verifica CRC-32
        """
        if len(dados_com_crc) < 4:
            return [], True

        dados = dados_com_crc[:-4]
        crc_recebido_bytes = dados_com_crc[-4:]

        # Reconstrói CRC-32 recebido
        crc_recebido = (crc_recebido_bytes[0] << 24) | \
                       (crc_recebido_bytes[1] << 16) | \
                       (crc_recebido_bytes[2] << 8) | \
                       crc_recebido_bytes[3]

        crc_calculado = self.calcular_crc(dados)

        tem_erro = (crc_recebido != crc_calculado)

        return dados, tem_erro
```

---

## ✅ Como Testar

Adicione no final de cada arquivo:

```python
# ==============================================================
# TESTES - Pessoa 3
# ==============================================================

if __name__ == "__main__":
    # Teste Enquadramento
    print("="*70)
    print("TESTANDO ENQUADRAMENTO")
    print("="*70)

    dados = [65, 66, 67]  # "ABC"
    print(f"\nDados: {dados}")

    # Teste 1
    print("\n--- Contagem ---")
    enq1 = EnquadradorContagem()
    q1 = enq1.enquadrar(dados)
    print(f"Quadro: {q1}")
    d1 = enq1.desenquadrar(q1)
    print(f"✓ OK" if d1 == dados else "✗ ERRO")

    # Teste 2
    print("\n--- FLAGS Bytes ---")
    enq2 = EnquadradorFlagsBytes()
    q2 = enq2.enquadrar(dados)
    print(f"Quadro: {q2}")
    d2 = enq2.desenquadrar(q2)
    print(f"✓ OK" if d2 == dados else "✗ ERRO")

    # Teste 3
    print("\n--- FLAGS Bits ---")
    bits = [1, 1, 1, 1, 1, 1, 0, 1]
    enq3 = EnquadradorFlagsBits()
    q3 = enq3.enquadrar(bits)
    print(f"Bits: {bits}")
    print(f"Quadro: {q3}")
    d3 = enq3.desenquadrar(q3)
    print(f"✓ OK" if d3 == bits else "✗ ERRO")

    # Teste Detecção
    print("\n" + "="*70)
    print("TESTANDO DETECÇÃO DE ERROS")
    print("="*70)

    dados = [10, 20, 30]
    print(f"\nDados: {dados}")

    # Teste Paridade
    print("\n--- Paridade ---")
    det1 = DetectorParidade()
    com_par = det1.adicionar(dados)
    print(f"Com paridade: {com_par}")
    rec, erro = det1.verificar(com_par)
    print(f"Erro? {erro}")
    print(f"✓ OK" if not erro and rec == dados else "✗ ERRO")

    # Teste Checksum
    print("\n--- Checksum ---")
    det2 = DetectorChecksum()
    com_check = det2.adicionar(dados)
    print(f"Com checksum: {com_check}")
    rec, erro = det2.verificar(com_check)
    print(f"Erro? {erro}")
    print(f"✓ OK" if not erro and rec == dados else "✗ ERRO")

    # Teste CRC-32
    print("\n--- CRC-32 ---")
    det3 = DetectorCRC32()
    com_crc = det3.adicionar(dados)
    print(f"Com CRC: {com_crc}")
    rec, erro = det3.verificar(com_crc)
    print(f"Erro? {erro}")
    print(f"✓ OK" if not erro and rec == dados else "✗ ERRO")
```

Execute:

```bash
python -m camada_enlace.enquadrador
python -m camada_enlace.detector_erros
```

---

## 🔍 Checklist

**Enquadramento:**

- [ ] `EnquadradorContagem` implementado
- [ ] `EnquadradorFlagsBytes` implementado
- [ ] `EnquadradorFlagsBits` implementado (bit stuffing)

**Detecção:**

- [ ] `DetectorParidade` implementado
- [ ] `DetectorChecksum` implementado
- [ ] `DetectorCRC32` implementado

**Testes:**

- [ ] Todos passam sem erros
- [ ] Dados recuperados == dados originais

---

## 🆘 Dúvidas Comuns

**P: Qual a diferença entre enquadramento com bytes e bits?**
R: Bytes trabalha com valores 0-255. Bits trabalha com 0 e 1 individuais.

**P: Por que FLAGS precisa de escape?**
R: Para evitar confusão se os dados contêm o mesmo padrão da FLAG.

**P: CRC é melhor que checksum?**
R: Sim! CRC detecta mais tipos de erros (burst errors, etc).

**P: Paridade detecta todos os erros?**
R: Não! Só detecta número ímpar de erros.

---

**Boa sorte!** 🚀
