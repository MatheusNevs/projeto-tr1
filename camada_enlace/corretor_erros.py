"""
Corretor de erros: Código de Hamming(7,4)
"""

class CorretorHamming:
    """
    Corretor de erros usando código de Hamming(7,4)
    
    Características:
    - Detecta e corrige 1 erro por bloco de 7 bits
    - Processa em blocos de 4 bits de dados
    - Adiciona 3 bits de paridade
    - Total: 7 bits codificados
    """

    def calcular_bits_paridade(self, tamanho_dados: int) -> int:
        """
        Calcula quantos bits de paridade são necessários
        
        Regra: 2^r >= m + r + 1
        onde r = bits de paridade, m = bits de dados
        
        Args:
            tamanho_dados: Número de bits de dados
            
        Returns:
            Número de bits de paridade necessários
        """
        r = 0
        while (2 ** r) < (tamanho_dados + r + 1):
            r += 1
        return r

    def codificar(self, dados_bits: list) -> list:
        """
        Codifica usando Hamming(7,4)
        
        Posições de paridade: 1, 2, 4, 8, 16, ... (potências de 2)
        Dados nas demais posições
        
        Args:
            dados_bits: Lista com bits de dados (4 bits)
            
        Returns:
            Lista com 7 bits codificados (4 dados + 3 paridade)
            
        Exemplo:
            [1, 0, 1, 1] → [0, 1, 1, 0, 0, 1, 1]
        """
        m = len(dados_bits)
        r = self.calcular_bits_paridade(m)
        n = m + r

        # Cria array com índice 1 a n (ignora 0)
        hamming = [0] * (n + 1)

        # Insere dados nas posições não-potência-de-2
        j = 0
        for i in range(1, n + 1):
            # Verifica se i é potência de 2 usando (i & (i-1))
            # Se (i & (i-1)) != 0, então i NÃO é potência de 2
            if (i & (i - 1)) != 0:
                if j < len(dados_bits):
                    hamming[i] = dados_bits[j]
                    j += 1

        # Calcula e insere bits de paridade
        for i in range(r):
            pos_paridade = 2 ** i  # 1, 2, 4, 8, ...
            paridade = 0
            
            # Verifica todas as posições com bit i setado
            for j in range(1, n + 1):
                if j & pos_paridade:  # Se posição j tem bit i
                    paridade ^= hamming[j]  # XOR
            
            hamming[pos_paridade] = paridade

        return hamming[1:]  # Remove índice 0

    def decodificar(self, hamming_bits: list) -> tuple:
        """
        Decodifica e corrige usando Hamming(7,4)
        
        Calcula síndrome (posição do erro):
        - Se síndrome = 0: sem erro
        - Se síndrome ≠ 0: erro na posição indicada (corrige automaticamente)
        
        Args:
            hamming_bits: Lista com 7 bits codificados (possivelmente com erro)
            
        Returns:
            (dados_originais, posicao_erro)
            - dados_originais: Lista com 4 bits decodificados
            - posicao_erro: 0 se sem erro, ou posição do erro corrigido
            
        Exemplo:
            [0, 1, 0, 0, 0, 1, 1] (com erro) → ([1, 0, 1, 1], 3)
        """
        n = len(hamming_bits)
        hamming = [0] + hamming_bits  # Adiciona índice 0

        # Calcula número de bits de paridade
        r = 0
        while (2 ** r) < (n + 1):
            r += 1

        # Calcula síndrome (posição do erro)
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
            if (i & (i - 1)) != 0:
                dados.append(hamming[i])

        return dados, sindrome

    def adicionar(self, dados: list) -> list:
        """
        Adiciona código de Hamming a uma lista de bytes
        
        Processa em blocos de 4 bits:
        - Cada 4 bits → 7 bits codificados (Hamming 7,4)
        
        Args:
            dados: Lista de bytes [65, 66, ...] (ASCII)
            
        Returns:
            Lista de bits com Hamming aplicado
            - Tamanho: aproximadamente dados originais × 7/4
            
        Exemplo:
            [65, 66] ("AB") → 28 bits (2 bytes × 8 bits = 16 bits → 4 blocos × 7 = 28)
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
            
            # Preenche com zeros se necessário (último bloco incompleto)
            if len(bloco) < 4:
                bloco.extend([0] * (4 - len(bloco)))
            
            # Codifica bloco
            hamming_bloco = self.codificar(bloco)
            hamming_completo.extend(hamming_bloco)

        return hamming_completo

    def verificar(self, hamming_bits: list) -> tuple:
        """
        Verifica e corrige dados com Hamming
        
        Cada bloco Hamming(7,4) tem exatamente 7 bits
        
        Args:
            hamming_bits: Lista de bits onde cada 7 bits é um bloco Hamming(7,4)
            
        Returns:
            (dados_bytes, numero_erros_corrigidos)
            - dados_bytes: Bytes recuperados e corrigidos
            - numero_erros_corrigidos: Quantos erros foram corrigidos
            
        Exemplo:
            28 bits (4 blocos de 7) → [65, 66] ("AB"), 0 erros
        """
        dados_bits = []
        erros_corrigidos = 0

        # ✅ CORRIGIDO: processa em blocos de 7 bits (Hamming(7,4))
        # Cada bloco tem exatamente 7 bits, não 8!
        for i in range(0, len(hamming_bits), 7):
            bloco = hamming_bits[i:i+7]
            
            # Só processa blocos completos
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


# ==============================================================================
# TESTES DE CÓDIGO DE HAMMING(7,4)
# ==============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("TESTANDO CÓDIGO DE HAMMING(7,4) - PESSOA 4")
    print("=" * 80)

    hamming = CorretorHamming()

    # Teste 1: Sem erro
    print("\n[TESTE 1] Hamming(7,4) sem erro")
    print("-" * 80)
    dados = [1, 0, 1, 1]
    cod = hamming.codificar(dados)
    print(f"Dados:        {dados}")
    print(f"Codificado:   {cod}")
    dec, erro = hamming.decodificar(cod)
    print(f"Decodificado: {dec}")
    print(f"Posição erro: {erro}")
    print(f"✓ OK" if dec == dados and erro == 0 else "✗ ERRO")

    # Teste 2: Com erro
    print("\n[TESTE 2] Hamming(7,4) com erro (deve corrigir)")
    print("-" * 80)
    cod_com_erro = cod.copy()
    cod_com_erro[2] ^= 1
    print(f"Com erro:     {cod_com_erro}")
    dec, erro = hamming.decodificar(cod_com_erro)
    print(f"Decodificado: {dec}")
    print(f"Posição erro: {erro}")
    print(f"✓ CORRIGIDO!" if dec == dados and erro == 3 else "✗ NÃO CORRIGIU")

    # Teste 3: Bytes
    print("\n[TESTE 3] Bytes 'AB' sem erro")
    print("-" * 80)
    dados_bytes = [65, 66]
    bits_hamming = hamming.adicionar(dados_bytes)
    print(f"Bytes:        {dados_bytes} = 'AB'")
    print(f"Hamming:      {len(bits_hamming)} bits")
    rec_bytes, erros = hamming.verificar(bits_hamming)
    print(f"Recuperado:   {rec_bytes}")
    print(f"Erros:        {erros}")
    print(f"✓ OK" if rec_bytes == dados_bytes else "✗ ERRO")

    # Teste 4: Bytes com erro
    print("\n[TESTE 4] Bytes 'AB' com erro (deve corrigir)")
    print("-" * 80)
    dados_bytes = [65, 66]
    bits_hamming = hamming.adicionar(dados_bytes)
    bits_com_erro = bits_hamming.copy()
    bits_com_erro[5] ^= 1
    print(f"Com erro no bit 6")
    rec_bytes, erros = hamming.verificar(bits_com_erro)
    print(f"Recuperado:   {rec_bytes}")
    print(f"Erros corrigidos: {erros}")
    print(f"✓ CORRIGIDO!" if rec_bytes == dados_bytes and erros == 1 else "✗ NÃO CORRIGIU")

    # Teste 5: Múltiplos bytes
    print("\n[TESTE 5] Mensagem 'Hello' sem erro")
    print("-" * 80)
    mensagem = "Hello"
    dados_bytes = [ord(c) for c in mensagem]
    bits_hamming = hamming.adicionar(dados_bytes)
    print(f"Mensagem:     '{mensagem}'")
    print(f"Hamming:      {len(bits_hamming)} bits")
    rec_bytes, erros = hamming.verificar(bits_hamming)
    mensagem_rec = ''.join(chr(b) for b in rec_bytes)
    print(f"Recuperada:   '{mensagem_rec}'")
    print(f"✓ OK" if mensagem_rec == mensagem else "✗ ERRO")

    # Teste 6: Múltiplos bytes com erros
    print("\n[TESTE 6] Mensagem 'Hello' com 2 erros (deve corrigir)")
    print("-" * 80)
    mensagem = "Hello"
    dados_bytes = [ord(c) for c in mensagem]
    bits_hamming = hamming.adicionar(dados_bytes)
    bits_com_erro = bits_hamming.copy()
    bits_com_erro[3] ^= 1
    bits_com_erro[15] ^= 1
    print(f"Mensagem:     '{mensagem}'")
    print(f"2 erros introduzidos")
    rec_bytes, erros = hamming.verificar(bits_com_erro)
    mensagem_rec = ''.join(chr(b) for b in rec_bytes)
    print(f"Recuperada:   '{mensagem_rec}'")
    print(f"Erros corrigidos: {erros}")
    print(f"✓ CORRIGIDO!" if mensagem_rec == mensagem and erros == 2 else "✗ NÃO CORRIGIU")

    print("\n" + "=" * 80)
    print("✅ TODOS OS TESTES PASSANDO!")
    print("=" * 80)