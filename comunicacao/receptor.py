"""
Módulo Receptor - Coordenação do Pipeline de Recepção.

O Receptor orquestra todas as etapas de recepção e processamento de
um sinal, coordenando as diferentes camadas em ordem inversa à transmissão:

Pipeline de Recepção (ordem inversa ao TX):
    1. Física (Demodulação): Sinal analógico → Bits
    2. Enlace (Desenquadramento): Remove delimitadores
    3. Enlace (Detecção): Verifica EDC, detecta erros
    4. Enlace (Correção): Hamming, corrige erros (opcional)
    5. Aplicação: Bits → Texto

Classes:
    Receptor: Orquestra o pipeline completo de recepção.

Responsabilidades:
    - Demodular sinal recebido
    - Remover enquadramento
    - Detectar presença de erros
    - Corrigir erros quando possível (Hamming)
    - Reconstruir mensagem original
    - Logging de cada etapa
    - Fornecer estatísticas (erros detectados/corrigidos)

Fluxo de Dados (inverso ao TX):
    Sinal (np.ndarray)
        ↓ Modulador.decodificar()
    Quadro (list de bits)
        ↓ Enquadrador.desenquadrar()
    Bits+EDC (list)
        ↓ DetectorErros.verificar()
    Bits+Hamming (list) + flag erro_detectado
        ↓ CorretorHamming.verificar() (opcional)
    Bits (list) + contador erros_corrigidos
        ↓ Conversor.bits_para_texto()
    Texto (str)

Informações de Status:
    - erro_detectado (bool): Flag se EDC detectou erro
    - erros_corrigidos (int): Quantos erros Hamming corrigiu
    - historico (list): Log detalhado de cada etapa

Exemplos:
    >>> from camada_fisica.modulador_digital import NRZPolar
    >>> from camada_enlace.enquadrador import EnquadradorContagem
    >>> from camada_enlace.detector_erros import DetectorParidade
    >>> 
    >>> rx = Receptor(
    ...     modulador=NRZPolar(),
    ...     enquadrador=EnquadradorContagem(),
    ...     detector_erros=DetectorParidade(),
    ...     usar_hamming=True
    ... )
    >>> mensagem = rx.receber(sinal_recebido)
    >>> print(f"Erro detectado: {rx.erro_detectado}")
    >>> print(f"Erros corrigidos: {rx.erros_corrigidos}")
"""
from utils.conversor import Conversor
from camada_fisica.modulador_digital import ModuladorDigital
from camada_enlace.enquadrador import Enquadrador
from camada_enlace.detector_erros import DetectorErros
from camada_enlace.corretor_erros import CorretorHamming
import numpy as np

class Receptor:
    """
    Coordena o processo de recepção através das camadas.
    
    Implementa o pipeline completo de recepção em ordem inversa à transmissão,
    desde demodulação do sinal até reconstrução do texto original, passando
    por detecção e correção de erros.
    
    Attributes:
        modulador (ModuladorDigital): Demodulador para camada física.
        enquadrador (Enquadrador): Desenquadrador para camada de enlace.
        detector_erros (DetectorErros): Detector de erros (EDC).
        usar_hamming (bool): Se True, aplica código de Hamming.
        corretor (CorretorHamming): Corretor Hamming (se usar_hamming=True).
        historico (list): Log de operações para debug.
        erro_detectado (bool): Flag indicando se EDC detectou erro.
        erros_corrigidos (int): Contador de erros corrigidos pelo Hamming.
    
    Pipeline Completo:
        sinal → bits → quadro → edc → hamming → texto
    
    Diferença TX vs RX:
        - TX: Adiciona proteção (hamming, edc, quadro)
        - RX: Remove proteção na ordem inversa (quadro, edc, hamming)
    
    Comportamento com Erros:
        - EDC detecta → flag erro_detectado = True, mas continua processando
        - Hamming corrige → incrementa erros_corrigidos, tenta recuperar dados
        - Se erro não corrigível → dados podem estar corrompidos
    """

    def __init__(self, 
                 modulador: ModuladorDigital,
                 enquadrador: Enquadrador,
                 detector_erros: DetectorErros,
                 usar_hamming: bool = True):
        """
        Inicializa receptor com componentes das camadas.
        
        Args:
            modulador (ModuladorDigital): Mesmo tipo usado no transmissor
                (NRZPolar, Manchester, Bipolar, ASK, FSK, QPSK, QAM16).
            enquadrador (Enquadrador): Mesmo tipo usado no transmissor
                (Contagem, FlagsBits).
            detector_erros (DetectorErros): Mesmo tipo usado no transmissor
                (Paridade, Checksum, CRC).
            usar_hamming (bool): Se True, aplica correção de Hamming.
                Deve ser igual ao valor usado no transmissor.
        
        Notas:
            - Componentes devem ser compatíveis com os do transmissor
            - CorretorHamming é criado automaticamente se usar_hamming=True
            - Histórico e contadores são resetados na criação
        
        Importante:
            Receptor e Transmissor devem usar os MESMOS componentes:
            - Mesmo tipo de modulador
            - Mesmo tipo de enquadrador
            - Mesmo tipo de detector
            - Mesmo valor de usar_hamming
        
        Exemplos:
            >>> rx = Receptor(
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