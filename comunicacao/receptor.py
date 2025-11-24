"""
Classe Receptor - coordena as camadas na recepção
"""
from utils.conversor import Conversor
from camada_fisica.modulador_digital import ModuladorDigital
from camada_enlace.enquadrador import Enquadrador
from camada_enlace.detector_erros import DetectorErros
from camada_enlace.corretor_erros import CorretorHamming
import numpy as np

class Receptor:
    """
    Coordena o processo de recepção através das camadas
    """

    def __init__(self, 
                 modulador: ModuladorDigital,
                 enquadrador: Enquadrador,
                 detector_erros: DetectorErros,
                 usar_hamming: bool = True):
        """
        Args:
            modulador: Mesma instância/tipo do transmissor
            enquadrador: Mesma instância/tipo do transmissor
            detector_erros: Mesma instância/tipo do transmissor
            usar_hamming: Se deve usar correção de erros Hamming
        """
        self.modulador = modulador
        self.enquadrador = enquadrador
        self.detector_erros = detector_erros
        self.usar_hamming = usar_hamming
        if usar_hamming:
            self.corretor = CorretorHamming()

        self.historico = []
        self.erro_detectado = False
        self.erros_corrigidos = 0

    def receber(self, sinal: np.ndarray) -> str:
        """
        Processa sinal através das camadas (RX)

        Fluxo COMPLETO EM BITS (inverso do TX):
        1. Sinal → Demodulação (Física)
        2. Bits → Desenquadramento (Enlace)
        3. Bits → Verificação de Erros (Enlace)
        4. Bits → Hamming (Enlace - Correção)
        5. Bits → Texto (Aplicação)

        Args:
            sinal: Sinal recebido do canal

        Returns:
            Mensagem reconstruída
        """
        self._log(f"RX: Recebendo sinal com {len(sinal)} amostras")

        # 1. Física: Demodulação
        bits_recuperados = self.modulador.decodificar(sinal)
        self._log(f"RX: {len(bits_recuperados)} bits demodulados")

        # 2. Enlace: Desenquadramento (primeiro passo da camada de enlace)
        bits_dados = self.enquadrador.desenquadrar(bits_recuperados)
        self._log(f"RX: Desenquadramento ({type(self.enquadrador).__name__}) - {len(bits_dados)} bits")

        # 3. Enlace: Verificação de erros
        bits_sem_deteccao, self.erro_detectado = self.detector_erros.verificar(bits_dados)
        if self.erro_detectado:
            self._log(f"RX: ⚠️  ERRO DETECTADO!")
        else:
            self._log(f"RX: ✓ Sem erros detectados")
        self._log(f"RX: Verificação ({type(self.detector_erros).__name__}) - {len(bits_sem_deteccao)} bits")

        # 4. Enlace: Correção de erros (Hamming) - opcional
        if self.usar_hamming:
            dados_bytes, self.erros_corrigidos = self.corretor.verificar(bits_sem_deteccao)
            self._log(f"RX: Hamming - {self.erros_corrigidos} erro(s) corrigido(s)")
            bits_sem_deteccao = Conversor.bytes_para_bits(dados_bytes)

        # 5. Aplicação: Bits → Texto
        mensagem = Conversor.bits_para_texto(bits_sem_deteccao)
        self._log(f"RX: Mensagem reconstruída: '{mensagem}'")

        return mensagem

    def _log(self, mensagem: str):
        """Registra evento no histórico"""
        self.historico.append(mensagem)
        print(mensagem)

    def get_historico(self) -> list:
        """Retorna histórico de recepções"""
        return self.historico.copy()

    def limpar_historico(self):
        """Limpa histórico"""
        self.historico.clear()

    def get_status(self) -> dict:
        """Retorna status da última recepção"""
        return {
            'erro_detectado': self.erro_detectado,
            'erros_corrigidos': self.erros_corrigidos
        }