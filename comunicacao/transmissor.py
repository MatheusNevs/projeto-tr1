"""
Classe Transmissor - coordena as camadas no envio
"""
from utils.conversor import Conversor
from camada_fisica.modulador_digital import ModuladorDigital
from camada_enlace.enquadrador import Enquadrador
from camada_enlace.detector_erros import DetectorErros
from camada_enlace.corretor_erros import CorretorHamming
import numpy as np

class Transmissor:
    """
    Coordena o processo de transmissão através das camadas
    """

    def __init__(self, 
                 modulador: ModuladorDigital,
                 enquadrador: Enquadrador,
                 detector_erros: DetectorErros,
                 usar_hamming: bool = True):
        """
        Args:
            modulador: Instância de modulador digital
            enquadrador: Instância de enquadrador
            detector_erros: Instância de detector de erros
            usar_hamming: Se deve usar correção de erros Hamming
        """
        self.modulador = modulador
        self.enquadrador = enquadrador
        self.detector_erros = detector_erros
        self.usar_hamming = usar_hamming
        if usar_hamming:
            self.corretor = CorretorHamming()

        self.historico = []  # Para logs

    def transmitir(self, mensagem: str) -> np.ndarray:
        """
        Processa mensagem através das camadas (TX)

        Fluxo:
        1. Texto → Bits (Aplicação)
        2. Bits → Hamming (Enlace - opcional)
        3. Bytes → Detecção de Erros (Enlace)
        4. Dados → Enquadramento (Enlace)
        5. Bits → Modulação (Física)

        Args:
            mensagem: Texto a transmitir

        Returns:
            Sinal modulado pronto para canal
        """
        self._log(f"TX: Mensagem original: '{mensagem}'")

        # 1. Aplicação: Texto → Bits
        bits = Conversor.texto_para_bits(mensagem)
        self._log(f"TX: {len(bits)} bits gerados")

        # 2. Enlace: Bits → Bytes
        dados_bytes = Conversor.bits_para_bytes(bits)
        self._log(f"TX: {len(dados_bytes)} bytes")

        # 3. Enlace: Correção de erros (Hamming) - opcional
        if self.usar_hamming:
            bits_hamming = self.corretor.adicionar(dados_bytes)
            dados_bytes = Conversor.bits_para_bytes(bits_hamming)
            self._log(f"TX: Hamming aplicado")

        # 4. Enlace: Detecção de erros
        dados_com_deteccao = self.detector_erros.adicionar(dados_bytes)
        self._log(f"TX: Detecção de erros aplicada ({type(self.detector_erros).__name__})")

        # 5. Enlace: Enquadramento
        quadro = self.enquadrador.enquadrar(dados_com_deteccao)
        self._log(f"TX: Quadro enquadrado ({type(self.enquadrador).__name__})")

        # 6. Enlace → Física: Bytes → Bits
        bits_quadro = Conversor.bytes_para_bits(quadro)
        self._log(f"TX: {len(bits_quadro)} bits no quadro")

        # 7. Física: Modulação
        sinal = self.modulador.codificar(bits_quadro)
        self._log(f"TX: Sinal modulado ({type(self.modulador).__name__}), {len(sinal)} amostras")

        return sinal

    def _log(self, mensagem: str):
        """Registra evento no histórico"""
        self.historico.append(mensagem)
        print(mensagem)

    def get_historico(self) -> list:
        """Retorna histórico de transmissões"""
        return self.historico.copy()

    def limpar_historico(self):
        """Limpa histórico"""
        self.historico.clear()
