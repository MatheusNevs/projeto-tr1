# Guia da Pessoa 1 - Modulações Digitais (Arquitetura OOP)

## 📁 Seu Arquivo

**Caminho:** `camada_fisica/modulador_digital.py`

## 🎯 Suas Responsabilidades

Implementar **3 classes de modulação digital**:

1. **NRZPolar** - Non-Return-to-Zero Polar
2. **Manchester** - Codificação Manchester (IEEE 802.3)
3. **Bipolar** - Alternate Mark Inversion (AMI)

Cada classe deve ter 2 métodos:

- `codificar(bits: list) -> np.ndarray` - Converte bits em sinal
- `decodificar(sinal: np.ndarray) -> list` - Converte sinal em bits

---

## 📚 Conceitos Básicos

### O que é Modulação Digital?

É a conversão de bits (0 e 1) em sinais elétricos (voltagem) para transmissão.

**Por quê?**

- Bits são abstratos (informação digital)
- O canal físico trabalha com sinais analógicos (voltagem)
- Precisamos representar bits como níveis de tensão

### Tipos que você vai implementar:

| Modulação      | Regra                | Vantagem           | Desvantagem            |
| -------------- | -------------------- | ------------------ | ---------------------- |
| **NRZ-Polar**  | 1→+V, 0→-V           | Simples            | Sem sincronização      |
| **Manchester** | 1→(-V,+V), 0→(+V,-V) | Autossincronização | Dobra largura de banda |
| **Bipolar**    | 0→0V, 1→alterna ±V   | DC balanceado      | Complexidade média     |

---

## 🏗️ Estrutura do Arquivo

O arquivo já tem a estrutura base. Você só precisa **completar os métodos**:

```python
from abc import ABC, abstractmethod
import numpy as np
from config import Config

class ModuladorDigital(ABC):
    """Classe abstrata - NÃO MEXER"""
    def __init__(self, amplitude=None):
        config = Config()
        self.amplitude = amplitude or config.AMPLITUDE

    @abstractmethod
    def codificar(self, bits: list) -> np.ndarray:
        pass

    @abstractmethod
    def decodificar(self, sinal: np.ndarray) -> list:
        pass


# ==============================================================
# SUAS IMPLEMENTAÇÕES COMEÇAM AQUI
# ==============================================================

class NRZPolar(ModuladorDigital):
    """
    NRZ-Polar: Bit 1 → +amplitude, Bit 0 → -amplitude
    """

    def codificar(self, bits: list) -> np.ndarray:
        """
        TODO: Implementar codificação NRZ-Polar

        Args:
            bits: Lista de bits [0, 1, 1, 0, ...]

        Returns:
            Sinal numpy array [−V, +V, +V, −V, ...]

        Exemplo:
            bits = [1, 0, 1, 1]
            amplitude = 5.0
            resultado = [5.0, -5.0, 5.0, 5.0]

        Dica:
            Use um loop for para percorrer os bits
            Se bit == 1: adicione +self.amplitude
            Se bit == 0: adicione -self.amplitude
        """
        sinal = []
        for bit in bits:
            if bit == 1:
                sinal.append(self.amplitude)
            else:
                sinal.append(-self.amplitude)
        return np.array(sinal)

    def decodificar(self, sinal: np.ndarray) -> list:
        """
        TODO: Implementar decodificação NRZ-Polar

        Args:
            sinal: Array numpy com valores de tensão

        Returns:
            Lista de bits [0, 1, 1, ...]

        Regra:
            Se valor > 0 → bit 1
            Se valor <= 0 → bit 0
        """
        bits = []
        for valor in sinal:
            if valor > 0:
                bits.append(1)
            else:
                bits.append(0)
        return bits


class Manchester(ModuladorDigital):
    """
    Manchester: Cada bit → 2 valores
    Bit 1 → transição de -V para +V
    Bit 0 → transição de +V para -V
    """

    def codificar(self, bits: list) -> np.ndarray:
        """
        TODO: Implementar codificação Manchester

        Args:
            bits: Lista de bits

        Returns:
            Sinal com DOBRO do tamanho (2 amostras por bit)

        Exemplo:
            bits = [1, 0, 1]
            amplitude = 5.0
            resultado = [-5.0, 5.0, 5.0, -5.0, -5.0, 5.0]
                         |_1__|     |_0__|      |_1__|

        Dica:
            Para bit 1: adicione [-amplitude, +amplitude]
            Para bit 0: adicione [+amplitude, -amplitude]
        """
        sinal = []
        for bit in bits:
            if bit == 1:
                # Bit 1: vai de baixo (-V) para cima (+V)
                sinal.extend([-self.amplitude, self.amplitude])
            else:
                # Bit 0: vai de cima (+V) para baixo (-V)
                sinal.extend([self.amplitude, -self.amplitude])
        return np.array(sinal)

    def decodificar(self, sinal: np.ndarray) -> list:
        """
        TODO: Implementar decodificação Manchester

        Args:
            sinal: Array com 2 amostras por bit

        Returns:
            Lista de bits

        Regra:
            Processe de 2 em 2 valores
            Se (negativo → positivo) = bit 1
            Se (positivo → negativo) = bit 0
        """
        bits = []
        # Processa de 2 em 2 valores
        for i in range(0, len(sinal), 2):
            if i + 1 < len(sinal):
                primeiro = sinal[i]
                segundo = sinal[i + 1]

                # Transição -V → +V = bit 1
                if primeiro < 0 and segundo > 0:
                    bits.append(1)
                # Transição +V → -V = bit 0
                else:
                    bits.append(0)
        return bits


class Bipolar(ModuladorDigital):
    """
    Bipolar (AMI):
    Bit 0 → 0V (tensão zero)
    Bit 1 → alterna entre +V e -V
    """

    def codificar(self, bits: list) -> np.ndarray:
        """
        TODO: Implementar codificação Bipolar

        Args:
            bits: Lista de bits

        Returns:
            Sinal bipolar

        Exemplo:
            bits = [1, 0, 1, 1, 0, 1]
            amplitude = 5.0
            resultado = [5.0, 0, -5.0, 5.0, 0, -5.0]
                         +V   0V  -V    +V  0V  -V

        Dica:
            - Mantenha uma variável para rastrear o último valor usado (±V)
            - Para bit 0: adicione 0
            - Para bit 1: adicione o valor e inverta para o próximo
        """
        sinal = []
        ultimo_valor = self.amplitude  # Começa com +V

        for bit in bits:
            if bit == 0:
                sinal.append(0)  # Bit 0 sempre é 0V
            else:  # bit == 1
                sinal.append(ultimo_valor)
                ultimo_valor = -ultimo_valor  # Inverte para o próximo 1

        return np.array(sinal)

    def decodificar(self, sinal: np.ndarray) -> list:
        """
        TODO: Implementar decodificação Bipolar

        Args:
            sinal: Array com valores 0, +V ou -V

        Returns:
            Lista de bits

        Regra:
            Se valor == 0 → bit 0
            Se valor != 0 (positivo ou negativo) → bit 1
        """
        bits = []
        for valor in sinal:
            if valor == 0:
                bits.append(0)
            else:
                bits.append(1)
        return bits
```

---

## ✅ Como Testar

### Teste Individual (no próprio arquivo)

Adicione no final do arquivo `modulador_digital.py`:

```python
# ==============================================================
# TESTES - Pessoa 1
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
```

Execute:

```bash
python -m camada_fisica.modulador_digital
```

---

## 🔍 Checklist de Verificação

Antes de considerar completo, verifique:

- [ ] `NRZPolar.codificar()` implementado
- [ ] `NRZPolar.decodificar()` implementado
- [ ] `Manchester.codificar()` implementado (retorna dobro de amostras)
- [ ] `Manchester.decodificar()` implementado
- [ ] `Bipolar.codificar()` implementado (alterna ±V para 1s)
- [ ] `Bipolar.decodificar()` implementado
- [ ] Todos os testes passam (bits recuperados == bits originais)
- [ ] Código tem comentários explicativos

---

## 🆘 Dúvidas Comuns

**P: Por que Manchester tem o dobro de valores?**
R: Porque cada bit precisa de uma transição (2 níveis) para carregar informação de sincronismo.

**P: No Bipolar, como garantir alternância correta?**
R: Use uma variável auxiliar (`ultimo_valor`) que inverte a cada bit 1 encontrado.

**P: Posso usar outras bibliotecas?**
R: Apenas `numpy` é permitido para arrays. Não use bibliotecas prontas de modulação.

**P: Como garantir que funciona com a GUI?**
R: Basta implementar corretamente os métodos. A GUI já está preparada para usar suas classes!

---

## 📊 Visualização dos Sinais

### NRZ-Polar

```
Bits:  1    0    1    1    0
      ___      ___  ___
     |   |    |   ||   |
_____|   |____|   ||   |____
     +V   -V   +V  +V   -V
```

### Manchester

```
Bits:  1      0      1
      _|¯    ¯|_    _|¯
     | |    | |    | |
_____|  ¯¯¯|  |___|  ¯¯¯
```

### Bipolar

```
Bits:  1  0  1  1  0  1
      _      _
     | |    | |    |_
_____|  |__|  |__| |
     +V  0  -V +V 0 -V
```

---

## 🎓 Recursos de Estudo

- Material do Moodle sobre Modulação Digital
- [Wikipedia: NRZ](https://pt.wikipedia.org/wiki/Non-return-to-zero)
- [Wikipedia: Manchester](https://pt.wikipedia.org/wiki/Codificação_Manchester)
- Slides da aula sobre codificação de linha

---

## ✨ Próximos Passos

1. Implemente as 3 classes
2. Execute os testes
3. Verifique se todos passam
4. Commit no Git (se estiver usando)
5. Avise o grupo que sua parte está pronta
6. Aguarde integração da Pessoa 4

**Boa sorte!** 🚀
