"""
Módulo de Simulação do Canal de Comunicação.

Este módulo simula um canal de comunicação real com ruído AWGN
(Additive White Gaussian Noise - Ruído Gaussiano Aditivo Branco).
O ruído é modelado como uma distribuição normal que é adicionada
ao sinal transmitido.

Classes:
    CanalComunicacao: Simulador de canal com ruído gaussiano.

Características do Ruído AWGN:
    - Gaussiano: Distribuição normal N(μ, σ²)
    - Aditivo: Somado ao sinal original
    - Branco: Espectro de potência uniforme
    - Modelo realista para muitos canais práticos

Métricas de Qualidade:
    - SNR (Signal-to-Noise Ratio): 10×log₁₀(P_sinal / P_ruído) dB
    - Maior σ → Mais ruído → Menor SNR → Mais erros

Exemplos:
    >>> canal = CanalComunicacao(nivel_ruido=0.5)
    >>> sinal_limpo = np.array([1.0, -1.0, 1.0])
    >>> sinal_ruidoso = canal.transmitir(sinal_limpo)
    >>> # sinal_ruidoso ≈ [1.2, -0.8, 1.3] (com ruído aleatório)
"""
import numpy as np
from config import Config

class CanalComunicacao:
    """
    Simula canal de comunicação com ruído AWGN.
    
    Implementa um canal de comunicação ideal com adição de ruído
    gaussiano. O ruído é caracterizado por sua média (μ) e desvio
    padrão (σ), seguindo distribuição normal N(μ, σ²).
    
    Attributes:
        nivel_ruido (float): Desvio padrão do ruído (σ) em Volts.
        ruido_media (float): Média do ruído (μ) em Volts, geralmente 0.
    
    Modelo Matemático:
        y(t) = x(t) + n(t)
        onde:
        - y(t) = sinal recebido
        - x(t) = sinal transmitido
        - n(t) ~ N(μ, σ²) = ruído gaussiano
    
    Notas:
        - σ = 0: canal perfeito (sem ruído)
        - σ pequeno (0.1-0.5): canal de boa qualidade
        - σ médio (0.5-2.0): canal típico
        - σ grande (>2.0): canal muito ruidoso
    """

    def __init__(self, nivel_ruido=None):
        """
        Inicializa o canal de comunicação.
        
        Args:
            nivel_ruido (float, optional): Desvio padrão do ruído (σ).
                Se None, usa Config.RUIDO_DESVIO.
        
        Exemplos:
            >>> # Canal com ruído padrão
            >>> canal1 = CanalComunicacao()
            >>> 
            >>> # Canal com ruído personalizado
            >>> canal2 = CanalComunicacao(nivel_ruido=1.0)
        """
        config = Config()
        self.nivel_ruido = nivel_ruido or config.RUIDO_DESVIO
        self.ruido_media = config.RUIDO_MEDIA

    def transmitir(self, sinal: np.ndarray) -> np.ndarray:
        """
        Transmite sinal através do canal adicionando ruído AWGN.
        
        Gera ruído gaussiano com a mesma dimensão do sinal e
        adiciona-o ao sinal original, simulando um canal ruidoso.
        
        Args:
            sinal (np.ndarray): Sinal de entrada (limpo).
            
        Returns:
            np.ndarray: Sinal com ruído adicionado.
        
        Processo:
            1. Gera vetor de ruído n ~ N(μ, σ²) com len(sinal) amostras
            2. Retorna sinal_ruidoso = sinal + ruído
        
        Características:
            - Cada amostra recebe ruído independente
            - Ruído segue distribuição normal
            - Processo estocástico (resultado varia a cada execução)
        
        Exemplos:
            >>> canal = CanalComunicacao(nivel_ruido=0.5)
            >>> sinal = np.array([5.0, -5.0, 5.0, -5.0])
            >>> sinal_ruidoso = canal.transmitir(sinal)
            >>> print(sinal_ruidoso)
            # Exemplo: [5.3, -4.8, 5.2, -5.1] (valores variam)
            
        Notas:
            - Amplitude do ruído é proporcional a nivel_ruido (σ)
            - Ruído pode ser positivo ou negativo
            - Para σ=0.5 e amplitude 5V: SNR ≈ 20 dB
        """
        ruido = np.random.normal(
            self.ruido_media, 
            self.nivel_ruido, 
            len(sinal)
        )
        return sinal + ruido

    def set_nivel_ruido(self, nivel: float):
        """
        Ajusta o nível de ruído do canal (desvio padrão).
        
        Args:
            nivel (float): Novo desvio padrão do ruído (σ) em Volts.
        
        Notas:
            - nivel = 0: canal perfeito
            - nivel pequeno: canal de alta qualidade
            - nivel grande: canal degradado
        
        Exemplos:
            >>> canal = CanalComunicacao()
            >>> canal.set_nivel_ruido(1.0)  # Canal mais ruidoso
            >>> canal.set_nivel_ruido(0.1)  # Canal mais limpo
        """
        self.nivel_ruido = nivel

    def set_media_ruido(self, media: float):
        """
        Ajusta a média do ruído do canal.
        
        Args:
            media (float): Nova média do ruído (μ) em Volts.
        
        Notas:
            - Geralmente mantido em 0 (ruído não enviesado)
            - Valor não-zero simula offset DC no canal
            - Pode representar deriva térmica ou desbalanceamento
        
        Exemplos:
            >>> canal = CanalComunicacao()
            >>> canal.set_media_ruido(0.0)   # Ruído centrado (padrão)
            >>> canal.set_media_ruido(0.5)   # Ruído com offset positivo
        """
        self.ruido_media = media
