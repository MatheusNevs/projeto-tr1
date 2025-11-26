"""
Módulo de Conversão de Dados.

Este módulo fornece utilitários para conversão entre diferentes representações
de dados: texto, bits e bytes. É fundamental para a conversão da mensagem
original em formato binário para transmissão e vice-versa.

Classes:
    Conversor: Classe com métodos estáticos para conversões de dados.

Exemplos:
    >>> bits = Conversor.texto_para_bits("AB")
    >>> print(bits)
    [0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1, 0]
    >>> texto = Conversor.bits_para_texto(bits)
    >>> print(texto)
    AB
"""

class Conversor:
    """
    Classe utilitária para conversão entre texto, bits e bytes.
    
    Fornece métodos estáticos para converter dados entre diferentes
    representações. Essencial para preparar mensagens para transmissão
    e reconstruir mensagens recebidas.
    
    Métodos:
        texto_para_bits: Converte string em lista de bits.
        bits_para_texto: Converte lista de bits em string.
        bits_para_bytes: Converte lista de bits em lista de bytes.
        bytes_para_bits: Converte lista de bytes em lista de bits.
    
    Notas:
        - Todos os métodos são estáticos, não requerem instanciação
        - Formato de bits: lista de inteiros 0 e 1
        - Formato de bytes: lista de inteiros 0-255
        - Codificação: ASCII de 8 bits
    """

    @staticmethod
    def texto_para_bits(texto: str) -> list:
        """
        Converte texto ASCII em lista de bits.
        
        Cada caractere é convertido em seu valor ASCII de 8 bits,
        resultando em uma lista linear de 0s e 1s.
        
        Args:
            texto (str): String a ser convertida.
            
        Returns:
            list: Lista de inteiros (0 ou 1) representando os bits.
                  Cada caractere gera 8 bits.
                  
        Exemplos:
            >>> bits = Conversor.texto_para_bits("Hi")
            >>> print(bits)
            [0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 1, 0, 1, 0, 0, 1]
            >>> len(bits)
            16
            
        Notas:
            - 'H' = 72 = 01001000
            - 'i' = 105 = 01101001
            - Total: 2 caracteres × 8 bits = 16 bits
        """
        bits = []
        for char in texto:
            byte_value = ord(char)
            bits_char = [int(b) for b in format(byte_value, '08b')]
            bits.extend(bits_char)
        return bits

    @staticmethod
    def bits_para_texto(bits: list) -> str:
        """
        Converte lista de bits em texto ASCII.
        
        Agrupa bits em bytes (8 bits) e converte cada byte no caractere
        ASCII correspondente. Ignora caracteres não imprimíveis.
        
        Args:
            bits (list): Lista de inteiros (0 ou 1).
            
        Returns:
            str: Texto reconstruído a partir dos bits.
            
        Notas:
            - Bits são agrupados de 8 em 8
            - Apenas caracteres ASCII imprimíveis (32-126) são incluídos
            - Bits restantes (< 8) são ignorados
            
        Exemplos:
            >>> bits = [0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 1, 0, 1, 0, 0, 1]
            >>> texto = Conversor.bits_para_texto(bits)
            >>> print(texto)
            Hi
            
        Avisos:
            Se os bits estiverem corrompidos, caracteres podem ser perdidos
            ou substituídos por valores incorretos.
        """
        texto = ""
        for i in range(0, len(bits), 8):
            byte_bits = bits[i:i+8]
            if len(byte_bits) == 8:
                byte_value = int(''.join(map(str, byte_bits)), 2)
                if 32 <= byte_value <= 126:  # ASCII imprimível
                    texto += chr(byte_value)
        return texto

    @staticmethod
    def bits_para_bytes(bits: list) -> list:
        """
        Converte lista de bits em lista de bytes.
        
        Agrupa bits em conjuntos de 8 e converte cada grupo em um
        inteiro de 0 a 255 (byte). Útil para manipulação de dados
        binários e cálculos de verificação.
        
        Args:
            bits (list): Lista de inteiros (0 ou 1).
            
        Returns:
            list: Lista de inteiros (0-255), cada um representando um byte.
            
        Notas:
            - Bits são agrupados de 8 em 8
            - Bits restantes (< 8) são ignorados
            - Ordem: big-endian (bit mais significativo primeiro)
            
        Exemplos:
            >>> bits = [0, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1]
            >>> bytes_list = Conversor.bits_para_bytes(bits)
            >>> print(bytes_list)
            [65, 255]
            
        Aplicações:
            - Cálculo de checksums e CRCs
            - Enquadramento de dados
            - Armazenamento em formato binário
        """
        bytes_list = []
        for i in range(0, len(bits), 8):
            byte_bits = bits[i:i+8]
            if len(byte_bits) == 8:
                byte_value = int(''.join(map(str, byte_bits)), 2)
                bytes_list.append(byte_value)
        return bytes_list

    @staticmethod
    def bytes_para_bits(bytes_list: list) -> list:
        """
        Converte lista de bytes em lista de bits.
        
        Cada byte (0-255) é expandido em seus 8 bits correspondentes,
        resultando em uma lista linear de 0s e 1s.
        
        Args:
            bytes_list (list): Lista de inteiros (0-255).
            
        Returns:
            list: Lista de inteiros (0 ou 1), cada byte gera 8 bits.
            
        Notas:
            - Cada byte gera exatamente 8 bits
            - Ordem: big-endian (bit mais significativo primeiro)
            - Comprimento da saída = 8 × comprimento da entrada
            
        Exemplos:
            >>> bytes_list = [65, 255]
            >>> bits = Conversor.bytes_para_bits(bytes_list)
            >>> print(bits)
            [0, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1]
            >>> len(bits)
            16
            
        Aplicações:
            - Preparação de dados para modulação
            - Processamento de quadros recebidos
            - Manipulação de dados binários
        """
        bits = []
        for byte in bytes_list:
            bits.extend([int(b) for b in format(byte, '08b')])
        return bits
