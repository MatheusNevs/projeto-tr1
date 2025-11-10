"""
Utilitários para conversão de dados
"""

class Conversor:
    """Classe com métodos estáticos para conversão"""

    @staticmethod
    def texto_para_bits(texto: str) -> list:
        """Converte texto em lista de bits"""
        bits = []
        for char in texto:
            byte_value = ord(char)
            bits_char = [int(b) for b in format(byte_value, '08b')]
            bits.extend(bits_char)
        return bits

    @staticmethod
    def bits_para_texto(bits: list) -> str:
        """Converte lista de bits em texto"""
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
        """Converte lista de bits em lista de bytes"""
        bytes_list = []
        for i in range(0, len(bits), 8):
            byte_bits = bits[i:i+8]
            if len(byte_bits) == 8:
                byte_value = int(''.join(map(str, byte_bits)), 2)
                bytes_list.append(byte_value)
        return bytes_list

    @staticmethod
    def bytes_para_bits(bytes_list: list) -> list:
        """Converte lista de bytes em lista de bits"""
        bits = []
        for byte in bytes_list:
            bits.extend([int(b) for b in format(byte, '08b')])
        return bits
