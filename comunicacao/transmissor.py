"""
Módulo Transmissor - Coordenação do Pipeline de Transmissão.

O Transmissor orquestra todas as etapas de preparação e transmissão de
uma mensagem, coordenando as diferentes camadas do modelo de comunicação:

Pipeline de Transmissão (ordem correta):
    1. Aplicação: Texto → Bits
    2. Enlace (Correção): Hamming (opcional)
    3. Enlace (Detecção): Adiciona EDC (Paridade/Checksum/CRC)
    4. Enlace (Enquadramento): Adiciona delimitadores
    5. Física (Modulação): Bits → Sinal analógico

Classes:
    Transmissor: Orquestra o pipeline completo de transmissão.

Responsabilidades:
    - Coordenar sequência correta das operações
    - Logging de cada etapa para debug
    - Validar tamanhos e limites
    - Propagar exceções adequadamente

Fluxo de Dados:
    Texto (str)
        ↓ Conversor
    Bits (list)
        ↓ CorretorHamming (opcional)
    Bits+Hamming (list)
        ↓ DetectorErros
    Bits+EDC (list)
        ↓ Enquadrador
    Quadro (list de bits)
        ↓ Modulador
    Sinal (np.ndarray)

Exemplos:
    >>> from camada_fisica.modulador_digital import NRZPolar
    >>> from camada_enlace.enquadrador import EnquadradorContagem
    >>> from camada_enlace.detector_erros import DetectorParidade
    >>> 
    >>> tx = Transmissor(
    ...     modulador=NRZPolar(),
    ...     enquadrador=EnquadradorContagem(),
    ...     detector_erros=DetectorParidade(),
    ...     usar_hamming=True
    ... )
    >>> sinal = tx.transmitir("Olá")
    >>> print(type(sinal))
    <class 'numpy.ndarray'>
"""
from utils.conversor import Conversor
from camada_fisica.modulador_digital import ModuladorDigital
from camada_enlace.enquadrador import Enquadrador
from camada_enlace.detector_erros import DetectorErros
from camada_enlace.corretor_erros import CorretorHamming
import numpy as np

class Transmissor:
    """
    Coordena o processo de transmissão através das camadas.
    
    Implementa o pipeline completo de transmissão, desde conversão de
    texto até geração do sinal modulado, passando por todas as etapas
    de proteção e enquadramento.
    
    Attributes:
        modulador (ModuladorDigital): Modulador para camada física.
        enquadrador (Enquadrador): Enquadrador para camada de enlace.
        detector_erros (DetectorErros): Detector de erros (EDC).
        usar_hamming (bool): Se True, aplica código de Hamming.
        corretor (CorretorHamming): Corretor Hamming (se usar_hamming=True).
        historico (list): Log de operações para debug.
    
    Pipeline Completo:
        texto → bits → hamming → edc → quadro → sinal
    
    Tratamento de Erros:
        - ValueError: Mensagem muito grande para quadro
        - Propaga exceções das camadas inferiores
        - Logs detalhados para debug
    """

    def __init__(self, 
                 modulador: ModuladorDigital,
                 enquadrador: Enquadrador,
                 detector_erros: DetectorErros,
                 usar_hamming: bool = True):
        """
        Inicializa transmissor com componentes das camadas.
        
        Args:
            modulador (ModuladorDigital): Modulador da camada física
                (NRZPolar, Manchester, Bipolar, ASK, FSK, QPSK, QAM16).
            enquadrador (Enquadrador): Protocolo de enquadramento
                (Contagem, FlagsBits).
            detector_erros (DetectorErros): Detector de erros
                (Paridade, Checksum, CRC).
            usar_hamming (bool): Se True, aplica correção de Hamming.
                Default: True.
        
        Notas:
            - Componentes devem ser instâncias já configuradas
            - CorretorHamming é criado automaticamente se usar_hamming=True
            - Histórico de logs é inicializado vazio
        
        Exemplos:
            >>> tx = Transmissor(
            ...     modulador=NRZPolar(amplitude=5.0),
            ...     enquadrador=EnquadradorContagem(),
            ...     detector_erros=DetectorCRCVariavel(32),
            ...     usar_hamming=True
            ... )
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

        Fluxo COMPLETO EM BITS (ordem correta):
        1. Texto → Bits (Aplicação)
        2. Bits → Hamming (Enlace - Correção)
        3. Bits → Detecção de Erros (Enlace)
        4. Bits → Enquadramento (Enlace) ← último da camada de enlace
        5. Bits → Modulação (Física)

        Args:
            mensagem: Texto a transmitir

        Returns:
            Sinal modulado pronto para canal
            
        Raises:
            ValueError: Se o quadro exceder o tamanho máximo configurado
        """
        self._log(f"TX: Mensagem original: '{mensagem}'")

        # 1. Aplicação: Texto → Bits
        bits_dados = Conversor.texto_para_bits(mensagem)
        self._log(f"TX: {len(bits_dados)} bits ({len(mensagem)} caracteres)")

        # 2. Enlace: Correção de erros (Hamming) - opcional
        if self.usar_hamming:
            # Hamming precisa de bytes, então converte temporariamente
            bytes_temp = Conversor.bits_para_bytes(bits_dados)
            bits_hamming = self.corretor.adicionar(bytes_temp)
            bits_dados = bits_hamming
            self._log(f"TX: Hamming aplicado ({len(bits_dados)} bits)")

        # 3. Enlace: Detecção de erros
        bits_com_deteccao = self.detector_erros.adicionar(bits_dados)
        self._log(f"TX: Detecção aplicada ({type(self.detector_erros).__name__}) - {len(bits_com_deteccao)} bits")

        # 4. Enlace: Enquadramento (último passo da camada de enlace)
        try:
            bits_quadro = self.enquadrador.enquadrar(bits_com_deteccao)
            self._log(f"TX: Enquadramento ({type(self.enquadrador).__name__}) - {len(bits_quadro)} bits")
        except ValueError as e:
            erro_msg = f"ERRO: {str(e)}. Tente uma mensagem menor."
            self._log(erro_msg)
            raise ValueError(erro_msg) from e

        # 5. Física: Modulação
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
