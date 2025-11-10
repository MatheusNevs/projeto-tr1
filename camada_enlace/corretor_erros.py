"""
Corretor de erros: Código de Hamming
Pessoa 4: Implementar esta classe
"""

class CorretorHamming:
    """Corretor de erros usando código de Hamming"""

    def calcular_bits_paridade(self, tamanho_dados: int) -> int:
        """
        Calcula quantos bits de paridade são necessários
        Regra: 2^r >= m + r + 1
        """
        r = 0
        while (2 ** r) < (tamanho_dados + r + 1):
            r += 1
        return r

    def codificar(self, dados_bits: list) -> list:
        """
        TODO Pessoa 4: Implementar código de Hamming
        Posições de paridade: 1, 2, 4, 8, 16, ... (potências de 2)
        """
        m = len(dados_bits)
        r = self.calcular_bits_paridade(m)
        n = m + r

        hamming = [0] * (n + 1)

        # Insere dados nas posições não-potência-de-2
        j = 0
        for i in range(1, n + 1):
            if (i & (i - 1)) != 0:  # Não é potência de 2
                if j < len(dados_bits):
                    hamming[i] = dados_bits[j]
                    j += 1

        # Calcula bits de paridade
        for i in range(r):
            pos_paridade = 2 ** i
            paridade = 0
            for j in range(1, n + 1):
                if j & pos_paridade:
                    paridade ^= hamming[j]
            hamming[pos_paridade] = paridade

        return hamming[1:]

    def decodificar(self, hamming_bits: list) -> tuple:
        """
        TODO Pessoa 4: Implementar decodificação e correção
        Retorna: (dados_originais, posicao_erro)
        """
        n = len(hamming_bits)
        hamming = [0] + hamming_bits

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
            if paridade != 0:
                sindrome += pos_paridade

        # Corrige erro
        if sindrome != 0 and sindrome <= n:
            hamming[sindrome] ^= 1

        # Extrai dados
        dados = []
        for i in range(1, n + 1):
            if (i & (i - 1)) != 0:
                dados.append(hamming[i])

        return dados, sindrome

    def adicionar(self, dados: list) -> list:
        """Adiciona código de Hamming a bytes (processa em blocos de 4 bits)"""
        todos_bits = []
        for byte in dados:
            bits = [int(b) for b in format(byte, '08b')]
            todos_bits.extend(bits)

        hamming_completo = []
        for i in range(0, len(todos_bits), 4):
            bloco = todos_bits[i:i+4]
            if len(bloco) < 4:
                bloco.extend([0] * (4 - len(bloco)))
            hamming_bloco = self.codificar(bloco)
            hamming_completo.extend(hamming_bloco)

        return hamming_completo

    def verificar(self, hamming_bits: list) -> tuple:
        """Verifica e corrige dados com Hamming"""
        dados_bits = []
        erros_corrigidos = 0

        for i in range(0, len(hamming_bits), 8):
            bloco = hamming_bits[i:i+8]
            if len(bloco) == 8:
                dados, erro = self.decodificar(bloco)
                dados_bits.extend(dados)
                if erro != 0:
                    erros_corrigidos += 1

        # Converte bits para bytes
        dados_bytes = []
        for i in range(0, len(dados_bits), 8):
            byte_bits = dados_bits[i:i+8]
            if len(byte_bits) == 8:
                byte_val = int(''.join(map(str, byte_bits)), 2)
                dados_bytes.append(byte_val)

        return dados_bytes, erros_corrigidos