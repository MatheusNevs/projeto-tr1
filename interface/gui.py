"""
Módulo de Interface Gráfica - Interface visual interativa para simulador de comunicação TR1.

Este módulo implementa a interface gráfica do usuário (GUI) para o simulador de 
comunicação digital, permitindo configuração interativa de todos os parâmetros do 
sistema, transmissão de mensagens e visualização em tempo real dos sinais e espectros.

Classes:
    InterfaceGrafica: Janela principal com controles, logs e gráficos interativos

Componentes da Interface:
    1. Painel de Configurações:
       - Seleção de modulação (digital/portadora)
       - Configuração de enquadramento
       - Seleção de detecção/correção de erros
       - Ajuste de parâmetros (taxa amostragem, bits, frequência)
       - Controle de ruído AWGN (μ, σ)
    
    2. Painel de Transmissão:
       - Campo para entrada de mensagem
       - Botão de transmitir
    
    3. Área de Logs:
       - Exibição de todas as operações realizadas
       - Estatísticas de transmissão/recepção
       - Mensagens de erro e sucesso
    
    4. Visualizações Gráficas:
       - Aba 1: Formas de onda (TX, RX e comparação)
       - Aba 2: Análise de espectro (FFT dos sinais)
       - Ferramentas de zoom e navegação (matplotlib)
    
    5. Barra de Status:
       - Indicador visual do estado atual

Tecnologias Utilizadas:
    - Tkinter: Framework GUI nativo do Python
    - Matplotlib: Visualização de sinais e espectros
    - Threading: Processamento não-bloqueante
    - NumPy: Cálculos científicos (FFT, estatísticas)

Características:
    - Interface responsiva com threads separadas
    - Visualização em tempo real de sinais
    - Análise de espectro via FFT
    - Configuração dinâmica de todos os parâmetros
    - Logs detalhados de operações
    - Estatísticas de MSE e SNR
    - Suporte para redimensionamento de janela

Exemplos de Uso:
    >>> from interface.gui import InterfaceGrafica
    >>> app = InterfaceGrafica()
    >>> app.iniciar()  # Abre a janela principal

Notas:
    - A interface executa transmissões em threads separadas para não bloquear a GUI
    - Todos os gráficos são interativos (zoom, pan, salvar)
    - Validações impedem configurações inválidas
    - Logs são thread-safe usando root.after()

Avisos:
    - Mensagens muito grandes podem exceder o tamanho máximo do quadro
    - Taxa de amostragem deve respeitar o teorema de Nyquist
    - Ruído muito alto pode causar perda total da mensagem

Autor: Projeto TR1 - UnB
Data: 2024
"""
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import queue
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from comunicacao import Transmissor, Receptor, CanalComunicacao
from camada_fisica.modulador_digital import NRZPolar, Manchester, Bipolar
from camada_fisica.modulador_portadora import ASK, FSK, QPSK, QAM16
from camada_enlace.enquadrador import EnquadradorContagem, EnquadradorFlagsBits
from camada_enlace.detector_erros import (DetectorParidade, DetectorChecksumVariavel, 
                                          DetectorCRCVariavel)

class InterfaceGrafica:
    """
    Interface gráfica principal do simulador de comunicação TR1.
    
    Implementa uma janela Tkinter completa com controles para configuração de todos os
    parâmetros do sistema de comunicação, área de transmissão, logs detalhados e 
    visualizações gráficas interativas (formas de onda e análise de espectro).
    
    A interface é dividida em:
    - Painel esquerdo: Controles e logs (largura fixa 550px)
    - Painel direito: Gráficos com abas (expansível)
    
    Attributes:
        root (tk.Tk): Janela principal da aplicação
        transmissor (Transmissor): Pipeline de transmissão configurado
        receptor (Receptor): Pipeline de recepção configurado
        canal (CanalComunicacao): Canal AWGN para adicionar ruído
        fila_recepcao (queue.Queue): Fila thread-safe para comunicação
        receptor_ativo (bool): Flag indicando se receptor está ativo
        ultimo_sinal_tx (np.ndarray): Último sinal transmitido para visualização
        ultimo_sinal_rx (np.ndarray): Último sinal recebido para visualização
        fig (matplotlib.figure.Figure): Figura das formas de onda
        canvas (FigureCanvasTkAgg): Canvas matplotlib para formas de onda
        toolbar (NavigationToolbar2Tk): Barra de ferramentas de navegação
        fig_espectro (matplotlib.figure.Figure): Figura dos espectros
        canvas_espectro (FigureCanvasTkAgg): Canvas matplotlib para espectros
        
        Widgets de Configuração:
            combo_tipo_modulacao (ttk.Combobox): Digital ou Portadora
            combo_modulacao (ttk.Combobox): Tipo específico de modulação
            combo_enquadramento (ttk.Combobox): Contagem ou FLAGS Bits
            combo_deteccao (ttk.Combobox): Paridade, Checksum ou CRC
            combo_tamanho_edc (ttk.Combobox): 8, 16, 24 ou 32 bits
            var_hamming (tk.BooleanVar): Ativar/desativar Hamming
            slider_ruido_desvio (ttk.Scale): Desvio padrão do ruído (0-2)
            slider_ruido_media (ttk.Scale): Média do ruído (-1 a 1)
            slider_taxa_amostragem (ttk.Scale): Taxa de amostragem (100-10000 Hz)
            slider_taxa_bits (ttk.Scale): Taxa de bits (1-1000 bps)
            slider_freq_portadora (ttk.Scale): Frequência portadora (10-1000 Hz)
            slider_tamanho_quadro (ttk.Scale): Tamanho máximo quadro (64-1024 bytes)
            
        Widgets de Transmissão:
            entry_mensagem (ttk.Entry): Campo para digitar mensagem
            
        Widgets de Visualização:
            text_logs (scrolledtext.ScrolledText): Área de logs
            label_status (ttk.Label): Indicador de status
            ax1, ax2, ax3 (matplotlib.axes.Axes): Eixos das formas de onda
            ax_esp_tx, ax_esp_rx (matplotlib.axes.Axes): Eixos dos espectros
    
    Métodos Públicos:
        iniciar(): Inicia o loop principal da interface
        
    Métodos Privados de Interface:
        _criar_interface(): Cria todos os widgets
        _atualizar_opcoes_modulacao(): Atualiza opções baseado no tipo
        _configurar_componentes(): Aplica configurações selecionadas
        _transmitir(): Inicia processo de transmissão
        _processar_transmissao(): Executa transmissão em thread separada
        _atualizar_graficos(): Atualiza gráficos de forma de onda
        _atualizar_espectro(): Atualiza gráficos de espectro (FFT)
        _log(): Adiciona mensagem aos logs (thread-safe)
        _limpar_logs(): Limpa área de logs
        
    Métodos de Atualização de Labels:
        _atualizar_label_ruido_desvio(): Atualiza valor exibido
        _atualizar_label_ruido_media(): Atualiza valor exibido
        _atualizar_label_tamanho_quadro(): Atualiza valor exibido
        _atualizar_label_taxa_amostragem(): Atualiza valor exibido
        _atualizar_label_taxa_bits(): Atualiza valor exibido
        _atualizar_label_freq_portadora(): Atualiza valor exibido
    
    Workflow de Transmissão:
        1. Usuário configura parâmetros e clica "Transmitir"
        2. _transmitir() valida e inicia thread
        3. _processar_transmissao() executa TX → Canal → RX
        4. Logs são atualizados em tempo real
        5. _atualizar_graficos() e _atualizar_espectro() mostram resultados
        6. Status final indica sucesso ou erro
    
    Exemplos:
        >>> app = InterfaceGrafica()
        >>> app.iniciar()  # Abre janela principal
        
        # A interface permite:
        # - Selecionar "NRZ-Polar" e transmitir "Hello"
        # - Configurar ruído σ=0.3 e observar degradação
        # - Analisar espectro para ver componentes de frequência
        # - Comparar TX vs RX graficamente
    
    Notas:
        - Threading evita bloqueio da interface durante transmissão
        - root.after() garante thread-safety nas atualizações de GUI
        - Matplotlib integrado permite zoom, pan e save de gráficos
        - Estatísticas incluem MSE, SNR, frequência dominante
    
    Avisos:
        - Mensagens longas podem exceder tamanho máximo do quadro
        - Taxa de amostragem baixa pode violar Nyquist
        - Ruído σ > 1.0 pode corromper completamente a mensagem
    
    Aplicações:
        - Educação em sistemas de comunicação digital
        - Experimentação com diferentes técnicas de modulação
        - Análise de efeitos de ruído em comunicação
        - Comparação visual de técnicas de detecção/correção de erros
        - Análise de espectro de diferentes modulações
    """

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Simulador TR1 - Camadas de Rede (OOP)")
        self.root.geometry("1600x900")

        # Componentes de comunicação
        self.transmissor = None
        self.receptor = None
        self.canal = CanalComunicacao()

        # Thread e fila para receptor
        self.fila_recepcao = queue.Queue()
        self.receptor_ativo = False

        # Armazenar sinais para visualização
        self.ultimo_sinal_tx = None
        self.ultimo_sinal_rx = None

        # Matplotlib figure, canvas e toolbar
        self.fig = None
        self.canvas = None
        self.toolbar = None

        self._criar_interface()
        self._configurar_componentes()

    def _criar_interface(self):
        """
        Cria e organiza todos os widgets da interface gráfica.
        
        Estrutura a interface em layout de duas colunas usando PanedWindow:
        - Coluna esquerda: Controles de configuração, transmissão e logs
        - Coluna direita: Gráficos com abas (formas de onda e espectro)
        
        Cria os seguintes componentes:
        1. Frame de configurações com sliders e comboboxes
        2. Frame de transmissão com campo de mensagem
        3. Área de logs com scroll
        4. Notebook com 2 abas de visualização
        5. Gráficos matplotlib integrados
        6. Barras de ferramentas de navegação
        
        Configurações Criadas:
            - Tipo de modulação (Digital/Portadora)
            - Modulação específica (NRZ, Manchester, ASK, etc.)
            - Enquadramento (Contagem/FLAGS)
            - Detecção de erros (Paridade/Checksum/CRC)
            - Código de Hamming (checkbox)
            - Tamanho do EDC (8/16/24/32 bits)
            - Taxa de amostragem (100-10000 Hz)
            - Taxa de bits (1-1000 bps)
            - Frequência portadora (10-1000 Hz)
            - Parâmetros de ruído (μ, σ)
            - Tamanho máximo do quadro (64-1024 bytes)
        
        Gráficos Criados:
            Aba 1 - Formas de Onda:
                - Sinal transmitido (TX)
                - Sinal recebido (RX)
                - Comparação TX vs RX
            
            Aba 2 - Análise de Espectro:
                - FFT do sinal TX
                - FFT do sinal RX
        
        Layout:
            - PanedWindow permite redimensionamento manual
            - Grid system para organização precisa
            - Frames aninhados para agrupamento lógico
            - Configuração de weight para expansão adequada
        
        Exemplos:
            # Chamado automaticamente no __init__
            >>> app = InterfaceGrafica()
            # Interface já está criada e pronta
        
        Notas:
            - Utiliza ttk para widgets com tema nativo do OS
            - Labels dos sliders são atualizadas dinamicamente
            - Comboboxes são read-only para evitar valores inválidos
            - Matplotlib toolbar permite zoom, pan e save
            - Grid columnconfigure/rowconfigure para responsividade
        
        Avisos:
            - Não chamar este método diretamente após __init__
            - Modificar estrutura requer ajuste de índices grid
        """

        # Frame principal
        main_frame = ttk.Frame(self.root, padding="5")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # PanedWindow para permitir redimensionamento manual entre controles e gráficos
        paned_window = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        paned_window.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Coluna esquerda - controles
        left_frame = ttk.Frame(paned_window, width=550)
        paned_window.add(left_frame, weight=0)

        # Coluna direita - gráficos (expansível)
        right_frame = ttk.Frame(paned_window)
        paned_window.add(right_frame, weight=1)

        # Título
        titulo = ttk.Label(left_frame, text="Simulador de Comunicação - TR1", 
                          font=('Arial', 14, 'bold'))
        titulo.grid(row=0, column=0, pady=(0, 10), sticky=tk.W+tk.E)

        # === CONFIGURAÇÕES ===
        config_frame = ttk.LabelFrame(left_frame, text="Configurações", padding="10")
        config_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        # Grid com 2 colunas de configurações
        # Linha 0: Tipo de Modulação e Modulação
        ttk.Label(config_frame, text="Tipo de Modulação:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.combo_tipo_modulacao = ttk.Combobox(config_frame, state='readonly',
                                                 values=['Digital', 'Portadora'])
        self.combo_tipo_modulacao.set('Digital')
        self.combo_tipo_modulacao.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        self.combo_tipo_modulacao.bind('<<ComboboxSelected>>', self._atualizar_opcoes_modulacao)

        ttk.Label(config_frame, text="Modulação:").grid(row=0, column=2, sticky=tk.W, padx=(15,0), pady=5)
        self.combo_modulacao = ttk.Combobox(config_frame, state='readonly',
                                            values=['NRZ-Polar', 'Manchester', 'Bipolar'])
        self.combo_modulacao.set('NRZ-Polar')
        self.combo_modulacao.grid(row=0, column=3, sticky=(tk.W, tk.E), padx=5, pady=5)

        # Linha 1: Enquadramento e Detecção
        ttk.Label(config_frame, text="Enquadramento:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.combo_enquadramento = ttk.Combobox(config_frame, state='readonly',
                                                values=['Contagem', 'FLAGS Bits'])
        self.combo_enquadramento.set('Contagem')
        self.combo_enquadramento.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)

        ttk.Label(config_frame, text="Detecção de Erros:").grid(row=1, column=2, sticky=tk.W, padx=(15,0), pady=5)
        self.combo_deteccao = ttk.Combobox(config_frame, state='readonly',
                                           values=['Paridade', 'Checksum (variável)', 'CRC (variável)'])
        self.combo_deteccao.set('CRC (variável)')
        self.combo_deteccao.grid(row=1, column=3, sticky=(tk.W, tk.E), padx=5, pady=5)

        # Linha 2: Hamming e Desvio do Ruído (σ)
        self.var_hamming = tk.BooleanVar(value=True)
        ttk.Checkbutton(config_frame, text="Usar Código de Hamming", 
                       variable=self.var_hamming).grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=5)

        ttk.Label(config_frame, text="Ruído - Desvio (σ):").grid(row=2, column=2, sticky=tk.W, padx=(15,0), pady=5)
        ruido_desvio_frame = ttk.Frame(config_frame)
        ruido_desvio_frame.grid(row=2, column=3, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        self.slider_ruido_desvio = ttk.Scale(ruido_desvio_frame, from_=0, to=2, orient=tk.HORIZONTAL)
        self.slider_ruido_desvio.set(0.3)
        self.slider_ruido_desvio.grid(row=0, column=0, sticky=(tk.W, tk.E))
        self.label_ruido_desvio = ttk.Label(ruido_desvio_frame, text="0.30", width=5)
        self.label_ruido_desvio.grid(row=0, column=1, padx=(5,0))
        self.slider_ruido_desvio.configure(command=self._atualizar_label_ruido_desvio)
        ruido_desvio_frame.columnconfigure(0, weight=1)

        # Linha 3: Taxa de Amostragem e Média do Ruído (μ)
        ttk.Label(config_frame, text="Taxa Amostragem:").grid(row=3, column=0, sticky=tk.W, pady=5)
        taxa_amostragem_frame = ttk.Frame(config_frame)
        taxa_amostragem_frame.grid(row=3, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        self.slider_taxa_amostragem = ttk.Scale(taxa_amostragem_frame, from_=100, to=10000, orient=tk.HORIZONTAL)
        self.slider_taxa_amostragem.set(1000)
        self.slider_taxa_amostragem.grid(row=0, column=0, sticky=(tk.W, tk.E))
        self.label_taxa_amostragem = ttk.Label(taxa_amostragem_frame, text="1000 Hz", width=10)
        self.label_taxa_amostragem.grid(row=0, column=1, padx=(5,0))
        self.slider_taxa_amostragem.configure(command=self._atualizar_label_taxa_amostragem)
        taxa_amostragem_frame.columnconfigure(0, weight=1)
        
        ttk.Label(config_frame, text="Ruído - Média (μ):").grid(row=3, column=2, sticky=tk.W, padx=(15,0), pady=5)
        ruido_media_frame = ttk.Frame(config_frame)
        ruido_media_frame.grid(row=3, column=3, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        self.slider_ruido_media = ttk.Scale(ruido_media_frame, from_=-1, to=1, orient=tk.HORIZONTAL)
        self.slider_ruido_media.set(0.0)
        self.slider_ruido_media.grid(row=0, column=0, sticky=(tk.W, tk.E))
        self.label_ruido_media = ttk.Label(ruido_media_frame, text="0.00", width=5)
        self.label_ruido_media.grid(row=0, column=1, padx=(5,0))
        self.slider_ruido_media.configure(command=self._atualizar_label_ruido_media)
        ruido_media_frame.columnconfigure(0, weight=1)

        # Linha 4: Tamanho Máximo do Quadro
        ttk.Label(config_frame, text="Tamanho Máx. Quadro:").grid(row=4, column=0, sticky=tk.W, pady=5)
        quadro_frame = ttk.Frame(config_frame)
        quadro_frame.grid(row=4, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        self.slider_tamanho_quadro = ttk.Scale(quadro_frame, from_=64, to=1024, orient=tk.HORIZONTAL)
        self.slider_tamanho_quadro.set(256)
        self.slider_tamanho_quadro.grid(row=0, column=0, sticky=(tk.W, tk.E))
        self.label_tamanho_quadro = ttk.Label(quadro_frame, text="256 bytes", width=10)
        self.label_tamanho_quadro.grid(row=0, column=1, padx=(5,0))
        self.slider_tamanho_quadro.configure(command=self._atualizar_label_tamanho_quadro)
        quadro_frame.columnconfigure(0, weight=1)

        # Linha 4 (coluna 3-4): Tamanho do EDC
        ttk.Label(config_frame, text="Tamanho EDC:").grid(row=4, column=2, sticky=tk.W, padx=(15,0), pady=5)
        self.combo_tamanho_edc = ttk.Combobox(config_frame, values=['8 bits', '16 bits', '24 bits', '32 bits'], 
                                              state='readonly', width=10)
        self.combo_tamanho_edc.set('32 bits')
        self.combo_tamanho_edc.grid(row=4, column=3, sticky=(tk.W, tk.E), padx=5, pady=5)

        # Linha 5: Taxa de Bits e Frequência da Portadora
        ttk.Label(config_frame, text="Taxa de Bits:").grid(row=5, column=0, sticky=tk.W, pady=5)
        taxa_bits_frame = ttk.Frame(config_frame)
        taxa_bits_frame.grid(row=5, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        self.slider_taxa_bits = ttk.Scale(taxa_bits_frame, from_=1, to=1000, orient=tk.HORIZONTAL)
        self.slider_taxa_bits.set(10)
        self.slider_taxa_bits.grid(row=0, column=0, sticky=(tk.W, tk.E))
        self.label_taxa_bits = ttk.Label(taxa_bits_frame, text="10 bps", width=10)
        self.label_taxa_bits.grid(row=0, column=1, padx=(5,0))
        self.slider_taxa_bits.configure(command=self._atualizar_label_taxa_bits)
        taxa_bits_frame.columnconfigure(0, weight=1)

        ttk.Label(config_frame, text="Freq. Portadora:").grid(row=5, column=2, sticky=tk.W, padx=(15,0), pady=5)
        freq_portadora_frame = ttk.Frame(config_frame)
        freq_portadora_frame.grid(row=5, column=3, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        self.slider_freq_portadora = ttk.Scale(freq_portadora_frame, from_=10, to=1000, orient=tk.HORIZONTAL)
        self.slider_freq_portadora.set(100)
        self.slider_freq_portadora.grid(row=0, column=0, sticky=(tk.W, tk.E))
        self.label_freq_portadora = ttk.Label(freq_portadora_frame, text="100 Hz", width=10)
        self.label_freq_portadora.grid(row=0, column=1, padx=(5,0))
        self.slider_freq_portadora.configure(command=self._atualizar_label_freq_portadora)
        freq_portadora_frame.columnconfigure(0, weight=1)

        # Linha 6: Botão aplicar
        ttk.Button(config_frame, text="Aplicar Configurações", 
                  command=self._configurar_componentes).grid(row=6, column=0, columnspan=4, pady=(10, 0))

        # Configurar colunas expansíveis
        config_frame.columnconfigure(1, weight=1)
        config_frame.columnconfigure(3, weight=1)

        # === TRANSMISSÃO ===
        tx_frame = ttk.LabelFrame(left_frame, text="Transmissão", padding="10")
        tx_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Label(tx_frame, text="Mensagem:", width=18).grid(row=0, column=0, sticky=tk.W, pady=5)
        self.entry_mensagem = ttk.Entry(tx_frame, width=40)
        self.entry_mensagem.insert(0, "Hello World from TR1!")
        self.entry_mensagem.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)

        ttk.Button(tx_frame, text="Transmitir", 
                  command=self._transmitir, width=15).grid(row=0, column=2, padx=5, pady=5)
        
        tx_frame.columnconfigure(1, weight=1)

        # === LOGS ===
        logs_frame = ttk.LabelFrame(left_frame, text="Logs da Comunicação", padding="10")
        logs_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))

        self.text_logs = scrolledtext.ScrolledText(logs_frame, width=62, height=20, 
                                                   font=('Courier', 8), wrap=tk.WORD)
        self.text_logs.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 5))

        # Botão limpar
        ttk.Button(logs_frame, text="Limpar Logs", 
                  command=self._limpar_logs, width=15).grid(row=1, column=0)

        logs_frame.columnconfigure(0, weight=1)
        logs_frame.rowconfigure(0, weight=1)

        # === STATUS ===
        status_frame = ttk.Frame(left_frame)
        status_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(0, 5))

        ttk.Label(status_frame, text="Status:", font=('Arial', 9, 'bold')).grid(row=0, column=0, sticky=tk.W)
        self.label_status = ttk.Label(status_frame, text="Pronto", 
                                      font=('Arial', 9), foreground='green')
        self.label_status.grid(row=0, column=1, sticky=tk.W, padx=(5, 0))

        # === GRÁFICOS (coluna direita) com abas ===
        # Criar Notebook (abas)
        notebook = ttk.Notebook(right_frame)
        notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # ==== ABA 1: FORMAS DE ONDA ====
        aba_forma_onda = ttk.Frame(notebook, padding="5")
        notebook.add(aba_forma_onda, text="Formas de Onda")

        # Criar figura matplotlib para formas de onda
        self.fig, (self.ax1, self.ax2, self.ax3) = plt.subplots(3, 1, figsize=(10, 8.5))
        self.fig.suptitle('Formas de Onda - TX vs RX', fontsize=13, fontweight='bold')
        
        # Configuração inicial dos gráficos
        for ax in [self.ax1, self.ax2, self.ax3]:
            ax.set_xlabel('Tempo (ms)', fontsize=9)
            ax.set_ylabel('Amplitude (V)', fontsize=9)
            ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)
            ax.tick_params(labelsize=8)
        
        self.ax1.set_title('Sinal Transmitido (TX)', fontsize=10, pad=8)
        self.ax2.set_title('Sinal Recebido (RX)', fontsize=10, pad=8)
        self.ax3.set_title('Comparação TX vs RX', fontsize=10, pad=8)
        
        # Mensagem inicial
        self.ax2.text(0.5, 0.5, 'Aguardando transmissão...', 
                     ha='center', va='center', transform=self.ax2.transAxes,
                     fontsize=13, style='italic', color='gray', alpha=0.5)
        
        plt.tight_layout()

        # Incorporar matplotlib no tkinter
        # Create toolbar first so it keeps a fixed height and the canvas can expand
        toolbar_frame = ttk.Frame(aba_forma_onda)
        toolbar_frame.pack(side=tk.TOP, fill=tk.X, padx=2, pady=(0, 2))
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=aba_forma_onda)
        self.toolbar = NavigationToolbar2Tk(self.canvas, toolbar_frame)
        self.toolbar.update()
        # Pack canvas after toolbar so the canvas expansion does not hide the toolbar
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=2, pady=2)

        # Ensure toolbar and canvas refresh on resize
        def _on_resize_forma(event):
            try:
                self.toolbar.update()
            except Exception:
                pass
            try:
                self.canvas.draw_idle()
            except Exception:
                pass

        aba_forma_onda.bind('<Configure>', _on_resize_forma)

        # ==== ABA 2: ANÁLISE DE ESPECTRO ====
        aba_espectro = ttk.Frame(notebook, padding="5")
        notebook.add(aba_espectro, text="Análise de Espectro")

        # Criar figura matplotlib para espectro
        self.fig_espectro, (self.ax_esp_tx, self.ax_esp_rx) = plt.subplots(2, 1, figsize=(10, 8.5))
        self.fig_espectro.suptitle('Análise de Espectro - FFT', fontsize=13, fontweight='bold')
        
        # Configuração inicial dos gráficos de espectro
        for ax in [self.ax_esp_tx, self.ax_esp_rx]:
            ax.set_xlabel('Frequência (Hz)', fontsize=9)
            ax.set_ylabel('Magnitude (dB)', fontsize=9)
            ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)
            ax.tick_params(labelsize=8)
        
        self.ax_esp_tx.set_title('Espectro do Sinal Transmitido (TX)', fontsize=10, pad=8)
        self.ax_esp_rx.set_title('Espectro do Sinal Recebido (RX)', fontsize=10, pad=8)
        
        # Mensagem inicial
        self.ax_esp_rx.text(0.5, 0.5, 'Aguardando transmissão...', 
                           ha='center', va='center', transform=self.ax_esp_rx.transAxes,
                           fontsize=13, style='italic', color='gray', alpha=0.5)
        
        plt.tight_layout()

        # Incorporar matplotlib no tkinter (espectro)
        toolbar_esp_frame = ttk.Frame(aba_espectro)
        toolbar_esp_frame.pack(side=tk.TOP, fill=tk.X, padx=2, pady=(0, 2))

        self.canvas_espectro = FigureCanvasTkAgg(self.fig_espectro, master=aba_espectro)
        self.toolbar_espectro = NavigationToolbar2Tk(self.canvas_espectro, toolbar_esp_frame)
        self.toolbar_espectro.update()
        self.canvas_espectro.draw()
        self.canvas_espectro.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=2, pady=2)

        # Ensure toolbar and canvas refresh on resize
        def _on_resize_espectro(event):
            try:
                self.toolbar_espectro.update()
            except Exception:
                pass
            try:
                self.canvas_espectro.draw_idle()
            except Exception:
                pass

        aba_espectro.bind('<Configure>', _on_resize_espectro)

        # Configurar redimensionamento completo
        # Root
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Main frame
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)
        
        # Left frame - coluna e logs expansíveis verticalmente
        left_frame.columnconfigure(0, weight=1)
        left_frame.rowconfigure(3, weight=1)  # Logs expandem verticalmente
        
        # Right frame - gráficos expansíveis
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(0, weight=1)
        
        # Notebook (abas) - expansível
        notebook.columnconfigure(0, weight=1)
        notebook.rowconfigure(0, weight=1)
        
        # Abas individuais - expansíveis
        aba_forma_onda.columnconfigure(0, weight=1)
        aba_forma_onda.rowconfigure(0, weight=1)
        aba_espectro.columnconfigure(0, weight=1)
        aba_espectro.rowconfigure(0, weight=1)

    def _atualizar_label_ruido_desvio(self, valor):
        """
        Callback do slider de desvio padrão do ruído.
        
        Atualiza o label ao lado do slider para exibir o valor atual de σ (sigma)
        do ruído AWGN com 2 casas decimais.
        
        Args:
            valor (str): Valor atual do slider (convertido internamente para float)
        """
        self.label_ruido_desvio.config(text=f"{float(valor):.2f}")

    def _atualizar_label_ruido_media(self, valor):
        """
        Callback do slider de média do ruído.
        
        Atualiza o label ao lado do slider para exibir o valor atual de μ (mu)
        do ruído AWGN com 2 casas decimais.
        
        Args:
            valor (str): Valor atual do slider (convertido internamente para float)
        """
        self.label_ruido_media.config(text=f"{float(valor):.2f}")

    def _atualizar_label_tamanho_quadro(self, valor):
        """
        Callback do slider de tamanho máximo do quadro.
        
        Atualiza o label para exibir o tamanho máximo do quadro em bytes.
        
        Args:
            valor (str): Valor atual do slider (convertido internamente para int)
        """
        tamanho = int(float(valor))
        self.label_tamanho_quadro.config(text=f"{tamanho} bytes")

    def _atualizar_label_taxa_amostragem(self, valor):
        """
        Callback do slider de taxa de amostragem.
        
        Atualiza o label para exibir a taxa de amostragem em Hz.
        Deve respeitar o teorema de Nyquist: fs >= 2 * f_max.
        
        Args:
            valor (str): Valor atual do slider (convertido internamente para int)
        """
        taxa = int(float(valor))
        self.label_taxa_amostragem.config(text=f"{taxa} Hz")

    def _atualizar_label_taxa_bits(self, valor):
        """
        Callback do slider de taxa de bits.
        
        Atualiza o label para exibir a taxa de bits em bps (bits por segundo).
        
        Args:
            valor (str): Valor atual do slider (convertido internamente para int)
        """
        taxa = int(float(valor))
        self.label_taxa_bits.config(text=f"{taxa} bps")

    def _atualizar_label_freq_portadora(self, valor):
        """
        Callback do slider de frequência da portadora.
        
        Atualiza o label para exibir a frequência da portadora em Hz.
        Relevante apenas para modulações por portadora (ASK, FSK, QPSK, QAM16).
        
        Args:
            valor (str): Valor atual do slider (convertido internamente para int)
        """
        freq = int(float(valor))
        self.label_freq_portadora.config(text=f"{freq} Hz")

    def _atualizar_opcoes_modulacao(self, event=None):
        """
        Callback da combobox de tipo de modulação.
        
        Atualiza dinamicamente as opções disponíveis na combobox de modulação
        específica baseado no tipo selecionado (Digital ou Portadora).
        
        Args:
            event (tk.Event, optional): Evento de seleção da combobox. Defaults to None.
        
        Comportamento:
            - Se "Digital" selecionado:
                * Opções: NRZ-Polar, Manchester, Bipolar
                * Padrão: NRZ-Polar
            
            - Se "Portadora" selecionado:
                * Opções: ASK, FSK, QPSK, 16-QAM
                * Padrão: ASK
        
        Exemplos:
            # Usuário seleciona "Portadora" na interface
            # → Automaticamente atualiza para mostrar ASK, FSK, QPSK, 16-QAM
            
            # Usuário seleciona "Digital" na interface
            # → Automaticamente atualiza para mostrar NRZ-Polar, Manchester, Bipolar
        
        Notas:
            - Método vinculado ao evento <<ComboboxSelected>>
            - Sempre define um valor padrão para evitar seleção vazia
        """
        tipo = self.combo_tipo_modulacao.get()
        if tipo == 'Digital':
            self.combo_modulacao.config(values=['NRZ-Polar', 'Manchester', 'Bipolar'])
            self.combo_modulacao.set('NRZ-Polar')
        else:  # Portadora
            self.combo_modulacao.config(values=['ASK', 'FSK', 'QPSK', '16-QAM'])
            self.combo_modulacao.set('ASK')

    def _configurar_componentes(self):
        """
        Configura transmissor, receptor e canal baseado nas seleções da interface.
        
        Lê todos os valores dos widgets de configuração e:
        1. Atualiza configurações globais (Config singleton)
        2. Instancia moduladores apropriados
        3. Instancia enquadradores apropriados
        4. Instancia detectores de erro apropriados
        5. Cria transmissor e receptor com componentes selecionados
        6. Configura parâmetros do canal (ruído)
        7. Registra todas as configurações nos logs
        
        Ordem de Configuração (CRÍTICA):
            1. Configurações globais (Config) ANTES de criar componentes
            2. Moduladores (digital ou portadora)
            3. Enquadradores (após Config para respeitar tamanho máximo)
            4. Detectores de erro (com tamanho EDC apropriado)
            5. Transmissor e Receptor (orquestram tudo)
            6. Canal (parâmetros de ruído)
        
        Configurações Lidas:
            - Taxa de amostragem (100-10000 Hz)
            - Taxa de bits (1-1000 bps)
            - Frequência portadora (10-1000 Hz)
            - Tamanho máximo quadro (64-1024 bytes)
            - Tipo e método de modulação
            - Método de enquadramento
            - Método de detecção de erros
            - Tamanho do EDC (8/16/24/32 bits)
            - Uso de código de Hamming (sim/não)
            - Parâmetros de ruído (μ, σ)
        
        Validações:
            - Tamanho do EDC só é usado para Checksum e CRC
            - Paridade sempre usa 1 bit por byte
            - Config singleton garante valores válidos
        
        Efeitos Colaterais:
            - Atualiza self.transmissor
            - Atualiza self.receptor
            - Atualiza self.canal
            - Adiciona logs detalhados
        
        Exemplos:
            # Usuário ajusta sliders e clica "Aplicar Configurações"
            # → Método é chamado automaticamente
            # → Componentes são reconfigurados
            # → Logs mostram nova configuração
        
        Notas:
            - Chamado automaticamente no __init__ para configuração inicial
            - Pode ser chamado manualmente clicando "Aplicar Configurações"
            - Cálculo amostras_por_bit = taxa_amostragem / taxa_bits
            - Logs incluem todos os parâmetros importantes
        
        Avisos:
            - Config DEVE ser atualizado ANTES de criar enquadradores
            - Ordem incorreta pode causar uso de valores desatualizados
        
        Aplicações:
            - Reconfiguração dinâmica sem reiniciar aplicação
            - Experimentação com diferentes combinações
            - Validação de configurações antes da transmissão
        """
        self._log("=== CONFIGURANDO COMPONENTES ===")

        # PRIMEIRO: Configurar parâmetros globais (antes de criar componentes!)
        from config import Config
        config = Config()
        
        # Taxa de amostragem
        taxa_amostragem = int(self.slider_taxa_amostragem.get())
        config.set_taxa_amostragem(taxa_amostragem)
        
        # Taxa de bits
        taxa_bits = int(self.slider_taxa_bits.get())
        config.set_taxa_bits(taxa_bits)
        
        # Frequência da portadora
        freq_portadora = int(self.slider_freq_portadora.get())
        config.set_frequencia_portadora(freq_portadora)
        
        # Tamanho máximo do quadro
        tamanho_quadro = int(self.slider_tamanho_quadro.get())
        config.set_tamanho_max_quadro(tamanho_quadro)

        # Modulador
        tipo_mod = self.combo_tipo_modulacao.get()
        mod_tipo = self.combo_modulacao.get()
        
        if tipo_mod == 'Digital':
            if mod_tipo == 'NRZ-Polar':
                modulador_tx = NRZPolar()
                modulador_rx = NRZPolar()
            elif mod_tipo == 'Manchester':
                modulador_tx = Manchester()
                modulador_rx = Manchester()
            else:  # Bipolar
                modulador_tx = Bipolar()
                modulador_rx = Bipolar()
        else:  # Portadora
            if mod_tipo == 'ASK':
                modulador_tx = ASK()
                modulador_rx = ASK()
            elif mod_tipo == 'FSK':
                modulador_tx = FSK()
                modulador_rx = FSK()
            elif mod_tipo == 'QPSK':
                modulador_tx = QPSK()
                modulador_rx = QPSK()
            else:  # 16-QAM
                modulador_tx = QAM16()
                modulador_rx = QAM16()

        # Enquadrador (agora criado DEPOIS de atualizar o tamanho máximo)
        enq_tipo = self.combo_enquadramento.get()
        if enq_tipo == 'Contagem':
            enquadrador_tx = EnquadradorContagem()
            enquadrador_rx = EnquadradorContagem()
        else:  # FLAGS Bits
            enquadrador_tx = EnquadradorFlagsBits()
            enquadrador_rx = EnquadradorFlagsBits()

        # Detector (com tamanho de EDC configurável)
        det_tipo = self.combo_deteccao.get()
        tamanho_edc_str = self.combo_tamanho_edc.get()
        tamanho_edc = int(tamanho_edc_str.split()[0])  # Extrai número de "8 bits" -> 8
        
        if det_tipo == 'Paridade':
            # Paridade não tem tamanho configurável (sempre 1 bit por byte)
            detector_tx = DetectorParidade()
            detector_rx = DetectorParidade()
        elif det_tipo == 'Checksum (variável)':
            # Usa checksum variável
            detector_tx = DetectorChecksumVariavel(tamanho_edc)
            detector_rx = DetectorChecksumVariavel(tamanho_edc)
        else:  # CRC (variável)
            # Usa CRC variável
            detector_tx = DetectorCRCVariavel(tamanho_edc)
            detector_rx = DetectorCRCVariavel(tamanho_edc)

        # Hamming
        usar_hamming = self.var_hamming.get()

        # Criar transmissor e receptor (já com novo tamanho máximo)
        self.transmissor = Transmissor(modulador_tx, enquadrador_tx, detector_tx, usar_hamming)
        self.receptor = Receptor(modulador_rx, enquadrador_rx, detector_rx, usar_hamming)

        # Configurar canal (desvio e média do ruído)
        nivel_ruido_desvio = self.slider_ruido_desvio.get()
        nivel_ruido_media = self.slider_ruido_media.get()
        self.canal.set_nivel_ruido(nivel_ruido_desvio)
        self.canal.set_media_ruido(nivel_ruido_media)

        amostras_por_bit = int(taxa_amostragem / taxa_bits)
        self._log(f"Taxa de Amostragem: {taxa_amostragem} Hz")
        self._log(f"Taxa de Bits: {taxa_bits} bps")
        self._log(f"Frequência Portadora: {freq_portadora} Hz")
        self._log(f"Amostras por Bit: {amostras_por_bit}")
        self._log(f"Tipo: {tipo_mod}")
        self._log(f"Modulação: {mod_tipo}")
        self._log(f"Enquadramento: {enq_tipo}")
        
        # Log de detecção - só mostra tamanho EDC se não for Paridade
        if det_tipo == 'Paridade':
            self._log(f"Detecção: {det_tipo} (1 bit por byte)")
        else:
            self._log(f"Detecção: {det_tipo} (EDC: {tamanho_edc} bits)")
        
        self._log(f"Hamming: {'Sim' if usar_hamming else 'Não'}")
        self._log(f"Ruído: μ={nivel_ruido_media:.2f}, σ={nivel_ruido_desvio:.2f}")
        self._log(f"Tamanho Máx. Quadro: {tamanho_quadro} bytes ({tamanho_quadro * 8} bits)")
        self._log("Configuração concluída!\n")

    def _transmitir(self):
        """
        Inicia processo de transmissão de mensagem.
        
        Valida a mensagem e componentes, atualiza status e inicia uma thread separada
        para processar a transmissão sem bloquear a interface gráfica.
        
        Workflow:
            1. Lê mensagem do campo de entrada
            2. Valida mensagem não-vazia
            3. Valida componentes configurados
            4. Atualiza parâmetros de ruído do canal
            5. Atualiza status para "Transmitindo..."
            6. Adiciona header aos logs
            7. Inicia thread daemon para _processar_transmissao()
        
        Validações:
            - Mensagem não pode ser vazia
            - Transmissor e Receptor devem estar configurados
        
        Efeitos Colaterais:
            - Cria thread daemon
            - Atualiza label_status
            - Adiciona logs
            - Atualiza parâmetros do canal
        
        Raises:
            Não lança exceções diretamente. Erros são:
            - Logados na área de logs
            - Thread continua executando sem bloquear GUI
        
        Exemplos:
            # Usuário digita "Hello TR1!" e clica "Transmitir"
            # → Método valida e inicia thread
            # → Interface continua responsiva
            # → Logs mostram progresso em tempo real
        
        Notas:
            - Thread daemon termina automaticamente com o programa
            - Interface não trava durante transmissão
            - Múltiplas transmissões podem ocorrer simultaneamente
            - Logs são thread-safe (usando root.after())
        
        Avisos:
            - Configurar componentes antes de transmitir
            - Mensagens muito longas podem exceder tamanho do quadro
            - Verificar logs para mensagens de erro
        
        Thread Safety:
            - Usa threading.Thread com daemon=True
            - Atualizações de GUI via root.after()
            - Fila de recepção é thread-safe (queue.Queue)
        """
        mensagem = self.entry_mensagem.get()

        if not mensagem:
            self._log("ERRO: Mensagem vazia!")
            return

        if not self.transmissor or not self.receptor:
            self._log("ERRO: Configure os componentes primeiro!")
            return

        # Atualiza parâmetros de ruído
        self.canal.set_nivel_ruido(self.slider_ruido_desvio.get())
        self.canal.set_media_ruido(self.slider_ruido_media.get())

        # Executa transmissão
        self.label_status.config(text="Transmitindo...")
        self._log("\n" + "="*70)
        self._log("INICIANDO TRANSMISSÃO")
        self._log("="*70)

        # Thread para não travar a interface
        thread = threading.Thread(target=self._processar_transmissao, args=(mensagem,))
        thread.daemon = True
        thread.start()

    def _processar_transmissao(self, mensagem):
        """
        Processa a transmissão completa da mensagem (executado em thread separada).
        
        Realiza todo o pipeline de comunicação:
        TX → Canal → RX → Validação → Atualização de Gráficos
        
        Args:
            mensagem (str): Mensagem de texto a ser transmitida
        
        Pipeline Completo:
            1. TRANSMISSÃO:
               - Transmissor codifica mensagem
               - Retorna sinal analógico (numpy array)
               - Armazena em self.ultimo_sinal_tx
            
            2. CANAL:
               - Adiciona ruído AWGN ao sinal
               - Retorna sinal degradado
               - Armazena em self.ultimo_sinal_rx
            
            3. RECEPÇÃO:
               - Receptor decodifica sinal
               - Detecta e corrige erros
               - Retorna mensagem recuperada
            
            4. VALIDAÇÃO:
               - Compara mensagem TX vs RX
               - Obtém estatísticas (erros detectados, corrigidos)
               - Atualiza status (Sucesso/Erro)
            
            5. VISUALIZAÇÃO:
               - Atualiza gráficos de forma de onda
               - Atualiza gráficos de espectro
        
        Tratamento de Erros:
            - ValueError: Quadro muito grande (mensagem excessiva)
                * Mostra messagebox com sugestão
                * Atualiza status para "Erro - Mensagem muito grande!"
            
            - Exception genérica: Erro inesperado
                * Loga traceback completo
                * Mostra messagebox de erro
                * Atualiza status para "Erro!"
        
        Logs Gerados:
            - Separador visual (====)
            - "INICIANDO TRANSMISSÃO"
            - ">>> CANAL DE COMUNICAÇÃO <<<"
            - Nível de ruído aplicado
            - "RESULTADO" com comparação TX vs RX
            - Status de sucesso/erro
            - Estatísticas de erros
        
        Efeitos Colaterais:
            - Atualiza self.ultimo_sinal_tx
            - Atualiza self.ultimo_sinal_rx
            - Adiciona múltiplas linhas de log
            - Atualiza label_status (via root.after)
            - Atualiza gráficos (via root.after)
            - Pode mostrar messagebox de erro
        
        Thread Safety:
            - Todas as atualizações de GUI usam root.after(0, ...)
            - Garante execução na thread principal do Tkinter
            - Evita race conditions e crashes
        
        Exemplos:
            # Transmissão bem-sucedida:
            >>> # Mensagem TX: 'Hello'
            >>> # Mensagem RX: 'Hello'
            >>> # ✓ TRANSMISSÃO BEM-SUCEDIDA!
            >>> # Erros detectados: 0
            >>> # Erros corrigidos (Hamming): 0
            
            # Transmissão com erros:
            >>> # Mensagem TX: 'Test'
            >>> # Mensagem RX: 'Tast'
            >>> # ✗ ERRO NA TRANSMISSÃO!
            >>> # Erros detectados: 1
            >>> # Erros corrigidos (Hamming): 2
        
        Notas:
            - Método executado em thread daemon separada
            - Não bloqueia interface durante processamento
            - Logs aparecem em tempo real
            - Gráficos atualizam após conclusão
        
        Avisos:
            - Mensagens muito longas podem causar ValueError
            - Ruído alto (σ > 1.5) pode corromper completamente a mensagem
            - Sempre verificar logs para diagnóstico completo
        
        Aplicações:
            - Demonstração educacional de sistema de comunicação
            - Análise de impacto de ruído
            - Teste de técnicas de detecção/correção de erros
            - Visualização de sinais e espectros
        """
        try:
            # TX
            sinal_tx = self.transmissor.transmitir(mensagem)
            self.ultimo_sinal_tx = sinal_tx.copy()

            # Canal
            self._log("\n>>> CANAL DE COMUNICAÇÃO <<<")
            sinal_rx = self.canal.transmitir(sinal_tx)
            self.ultimo_sinal_rx = sinal_rx.copy()
            self._log(f"Sinal atravessou o canal (ruído σ={self.canal.nivel_ruido:.2f})")

            # RX
            self._log("\n")
            mensagem_rx = self.receptor.receber(sinal_rx)

            # Resultado
            self._log("\n" + "="*70)
            self._log("RESULTADO")
            self._log("="*70)
            self._log(f"Mensagem TX: '{mensagem}'")
            self._log(f"Mensagem RX: '{mensagem_rx}'")

            status = self.receptor.get_status()
            if mensagem == mensagem_rx:
                self._log("✓ TRANSMISSÃO BEM-SUCEDIDA!")
                self.root.after(0, lambda: self.label_status.config(text="Sucesso!"))
            else:
                self._log("✗ ERRO NA TRANSMISSÃO!")
                self.root.after(0, lambda: self.label_status.config(text="Erro!"))

            self._log(f"Erros detectados: {status['erro_detectado']}")
            self._log(f"Erros corrigidos (Hamming): {status['erros_corrigidos']}")
            self._log("="*70 + "\n")

            # Atualizar gráficos
            self.root.after(0, self._atualizar_graficos)

        except ValueError as e:
            # Erro específico de validação (ex: quadro muito grande)
            erro_str = str(e)
            self._log(f"\n{erro_str}")
            self.root.after(0, lambda: self.label_status.config(text="Erro - Mensagem muito grande!"))
            self.root.after(0, lambda: messagebox.showerror(
                "Mensagem muito grande",
                f"{erro_str}\n\nDica: Tente uma mensagem menor ou desative o código Hamming."
            ))
        except Exception as e:
            # Outros erros inesperados
            self._log(f"\nERRO DURANTE TRANSMISSÃO: {e}")
            import traceback
            self._log(traceback.format_exc())
            self.root.after(0, lambda: self.label_status.config(text="Erro!"))
            self.root.after(0, lambda: messagebox.showerror("Erro", f"Erro inesperado: {e}"))

    def _log(self, mensagem):
        """
        Adiciona mensagem à área de logs de forma thread-safe.
        
        Utiliza root.after() para garantir que a inserção de texto ocorra na thread
        principal do Tkinter, evitando problemas de concorrência quando chamado de
        threads separadas (como durante transmissão).
        
        Args:
            mensagem (str): Mensagem a ser adicionada aos logs
        
        Comportamento:
            - Adiciona mensagem ao final do widget ScrolledText
            - Adiciona quebra de linha automaticamente
            - Rola automaticamente para mostrar última mensagem
            - Thread-safe via root.after(0, ...)
        
        Thread Safety:
            - Pode ser chamado de qualquer thread
            - Sempre executa inserção na thread principal
            - Evita exceções de Tkinter em multi-threading
        
        Exemplos:
            >>> self._log("Configuração aplicada")
            >>> self._log("=== INICIANDO TRANSMISSÃO ===")
            >>> self._log(f"Taxa de bits: {taxa} bps")
        
        Notas:
            - Método usado extensivamente durante transmissão
            - Logs aparecem em tempo real na interface
            - Scroll automático mantém última mensagem visível
        """
        def adicionar():
            self.text_logs.insert(tk.END, mensagem + "\n")
            self.text_logs.see(tk.END)

        # Se chamado de thread, agenda para thread principal
        self.root.after(0, adicionar)

    def _limpar_logs(self):
        """
        Limpa completamente a área de logs e históricos dos componentes.
        
        Remove todo o texto da área de logs e limpa os históricos armazenados
        no transmissor e receptor (se existirem).
        
        Efeitos Colaterais:
            - Remove todo texto de self.text_logs
            - Chama transmissor.limpar_historico() se configurado
            - Chama receptor.limpar_historico() se configurado
        
        Exemplos:
            # Usuário clica no botão "Limpar Logs"
            # → Área de logs fica vazia
            # → Históricos internos são resetados
        
        Notas:
            - Útil antes de nova série de testes
            - Não afeta configurações ou últimos sinais
            - Apenas limpa visualização e históricos
        """
        self.text_logs.delete(1.0, tk.END)
        if self.transmissor:
            self.transmissor.limpar_historico()
        if self.receptor:
            self.receptor.limpar_historico()

    def _atualizar_graficos(self):
        """
        Atualiza os gráficos de formas de onda na aba principal.
        
        Cria três gráficos comparativos:
        1. Sinal transmitido (TX) - azul
        2. Sinal recebido (RX) - vermelho
        3. Comparação TX vs RX sobreposta - ambos
        
        Requer que uma transmissão tenha sido realizada anteriormente
        (self.ultimo_sinal_tx e self.ultimo_sinal_rx não-nulos).
        
        Informações Exibidas:
            - Tempo em milissegundos (eixo X)
            - Amplitude em Volts (eixo Y)
            - Número de amostras e duração
            - Estatísticas: Min, Max, Média (μ), Desvio Padrão (σ)
            - MSE (Mean Squared Error) entre TX e RX
            - SNR (Signal-to-Noise Ratio) em dB
        
        Cálculos Realizados:
            - Conversão amostras → tempo: t = n / fs * 1000 (ms)
            - Duração: amostras / taxa_amostragem * 1000 (ms)
            - Estatísticas: np.min, np.max, np.mean, np.std
            - MSE: mean((RX - TX)²)
            - SNR: 10 * log₁₀(P_sinal / P_ruído) dB
        
        Layout dos Gráficos:
            - 3 subplots verticais (ax1, ax2, ax3)
            - Grid para facilitar leitura
            - Legendas em cada gráfico
            - Caixas de texto com estatísticas
            - Tight layout para melhor uso de espaço
        
        Efeitos Colaterais:
            - Limpa gráficos anteriores (ax.clear())
            - Redesenha canvas matplotlib
            - Chama _atualizar_espectro() automaticamente
        
        Validações:
            - Retorna silenciosamente se sinais não existem
            - MSE/SNR só calculados se tamanhos forem iguais
        
        Exemplos:
            # Após transmissão bem-sucedida:
            # Gráfico 1: Mostra sinal digital modulado (TX)
            # Gráfico 2: Mostra sinal com ruído (RX)
            # Gráfico 3: Sobreposição revelando diferenças
            # Estatísticas: MSE=0.0823V², SNR=12.4dB
        
        Notas:
            - Chamado automaticamente após _processar_transmissao()
            - Usa root.after() para thread-safety
            - Matplotlib integrado permite zoom e pan
            - Cores consistentes: azul=TX, vermelho=RX
        
        Avisos:
            - Sinais muito longos podem demorar para renderizar
            - Zoom excessivo pode não mostrar detalhes úteis
        
        Aplicações:
            - Análise visual de modulação
            - Comparação de efeito do ruído
            - Medição de qualidade do sinal (SNR)
            - Diagnóstico de problemas de transmissão
        """
        if self.ultimo_sinal_tx is None or self.ultimo_sinal_rx is None:
            return

        # Limpar gráficos
        self.ax1.clear()
        self.ax2.clear()
        self.ax3.clear()

        # Dados
        amostras_tx = len(self.ultimo_sinal_tx)
        amostras_rx = len(self.ultimo_sinal_rx)
        
        # Converter amostras para tempo (em milissegundos)
        # Taxa de amostragem = 1000 Hz → período = 1ms
        from config import Config
        config = Config()
        taxa_amostragem = config.TAXA_AMOSTRAGEM  # Hz
        t_tx = np.arange(amostras_tx) / taxa_amostragem * 1000  # ms
        t_rx = np.arange(amostras_rx) / taxa_amostragem * 1000  # ms

        # Gráfico 1: Sinal transmitido
        self.ax1.plot(t_tx, self.ultimo_sinal_tx, 'b-', linewidth=1.0, label='TX')
        self.ax1.set_xlabel('Tempo (ms)', fontsize=9)
        self.ax1.set_ylabel('Amplitude (V)', fontsize=9)
        duracao_tx = amostras_tx / taxa_amostragem * 1000  # ms
        self.ax1.set_title(f'Sinal Transmitido ({amostras_tx} amostras, {duracao_tx:.1f} ms)', fontsize=10, fontweight='bold')
        self.ax1.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)
        self.ax1.legend(loc='upper right', fontsize=8)
        self.ax1.tick_params(labelsize=8)
        
        # Estatísticas TX
        stats_tx = f'Min:{np.min(self.ultimo_sinal_tx):.2f}V Max:{np.max(self.ultimo_sinal_tx):.2f}V ' \
                   f'μ:{np.mean(self.ultimo_sinal_tx):.2f}V σ:{np.std(self.ultimo_sinal_tx):.2f}V'
        self.ax1.text(0.02, 0.98, stats_tx, transform=self.ax1.transAxes, 
                fontsize=7, verticalalignment='top', 
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

        # Gráfico 2: Sinal recebido
        self.ax2.plot(t_rx, self.ultimo_sinal_rx, 'r-', linewidth=1.0, label='RX', alpha=0.8)
        self.ax2.set_xlabel('Tempo (ms)', fontsize=9)
        self.ax2.set_ylabel('Amplitude (V)', fontsize=9)
        duracao_rx = amostras_rx / taxa_amostragem * 1000  # ms
        self.ax2.set_title(f'Sinal Recebido (ruído σ={self.canal.nivel_ruido:.2f}) - {amostras_rx} amostras, {duracao_rx:.1f} ms', 
                     fontsize=10, fontweight='bold')
        self.ax2.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)
        self.ax2.legend(loc='upper right', fontsize=8)
        self.ax2.tick_params(labelsize=8)
        
        # Estatísticas RX
        stats_rx = f'Min:{np.min(self.ultimo_sinal_rx):.2f}V Max:{np.max(self.ultimo_sinal_rx):.2f}V ' \
                   f'μ:{np.mean(self.ultimo_sinal_rx):.2f}V σ:{np.std(self.ultimo_sinal_rx):.2f}V'
        self.ax2.text(0.02, 0.98, stats_rx, transform=self.ax2.transAxes, 
                fontsize=7, verticalalignment='top', 
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

        # Gráfico 3: Comparação TX vs RX (todas as amostras)
        max_amostras = min(amostras_tx, amostras_rx)
        t_max = min(len(t_tx), len(t_rx))
        self.ax3.plot(t_tx[:t_max], self.ultimo_sinal_tx[:max_amostras], 
                'b-', linewidth=1.2, label='TX', alpha=0.7)
        self.ax3.plot(t_rx[:t_max], self.ultimo_sinal_rx[:max_amostras], 
                'r-', linewidth=1.0, label='RX', alpha=0.6)
        self.ax3.set_xlabel('Tempo (ms)', fontsize=9)
        self.ax3.set_ylabel('Amplitude (V)', fontsize=9)
        duracao_comp = max_amostras / taxa_amostragem * 1000  # ms
        self.ax3.set_title(f'Comparação TX vs RX ({max_amostras} amostras, {duracao_comp:.1f} ms)', 
                     fontsize=10, fontweight='bold')
        self.ax3.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)
        self.ax3.legend(loc='upper right', fontsize=8)
        self.ax3.tick_params(labelsize=8)
        
        # Calcular MSE e SNR se tamanhos forem iguais
        if amostras_tx == amostras_rx:
            diferenca = self.ultimo_sinal_rx - self.ultimo_sinal_tx
            mse = np.mean(diferenca**2)
            snr = 10 * np.log10(np.mean(self.ultimo_sinal_tx**2) / mse) if mse > 0 else float('inf')
            stats_comp = f'MSE:{mse:.4f}V²  SNR:{snr:.1f}dB'
            self.ax3.text(0.02, 0.98, stats_comp, transform=self.ax3.transAxes, 
                    fontsize=7, verticalalignment='top', 
                    bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.5))

        plt.tight_layout()
        self.canvas.draw()

        # Atualizar também o espectro
        self._atualizar_espectro()

    def _atualizar_espectro(self):
        """
        Atualiza os gráficos de análise de espectro (FFT) na segunda aba.
        
        Calcula e exibe a Transformada Rápida de Fourier (FFT) dos sinais TX e RX,
        permitindo análise de componentes de frequência e características espectrais
        das modulações utilizadas.
        
        Requer que uma transmissão tenha sido realizada anteriormente
        (self.ultimo_sinal_tx e self.ultimo_sinal_rx não-nulos).
        
        Análise Realizada:
            1. TRANSFORMADA DE FOURIER:
               - Calcula FFT de ambos os sinais
               - Extrai frequências positivas (metade do espectro)
               - Calcula magnitudes complexas
               - Converte para escala dB: 20*log₁₀(magnitude)
            
            2. ESTATÍSTICAS:
               - Frequência dominante: freq com maior magnitude
               - Potência total: Σ(magnitude²) / N
               - Exibição em dB para melhor visualização
        
        Informações Exibidas:
            - Eixo X: Frequência (Hz)
            - Eixo Y: Magnitude (dB)
            - Frequência dominante de cada sinal
            - Potência total em dB
            - Grid para facilitar leitura
        
        Algoritmo FFT:
            1. fft = np.fft.fft(sinal)
            2. freqs = np.fft.fftfreq(N, 1/fs)
            3. Use metade positiva: freqs[:N//2]
            4. magnitude = |fft[:N//2]|
            5. dB = 20 * log₁₀(magnitude + ε)  # ε evita log(0)
        
        Layout dos Gráficos:
            - 2 subplots verticais
            - Espectro TX (topo)
            - Espectro RX (embaixo)
            - Caixas de texto com estatísticas
            - Tight layout
        
        Efeitos Colaterais:
            - Limpa gráficos anteriores (ax.clear())
            - Redesenha canvas_espectro matplotlib
        
        Validações:
            - Retorna silenciosamente se sinais não existem
            - Adiciona epsilon (1e-10) para evitar log(0)
        
        Exemplos:
            # Sinal NRZ-Polar:
            # Espectro mostra componentes em baixa frequência
            # Freq. Dominante: ~50Hz
            
            # Sinal ASK (100Hz portadora):
            # Espectro mostra pico em 100Hz
            # Freq. Dominante: 100Hz
            
            # Sinal Manchester:
            # Espectro mostra energia em frequências médias
            # Componente DC ausente
        
        Notas:
            - Chamado automaticamente por _atualizar_graficos()
            - FFT revela características da modulação
            - Ruído aparece como "piso" no espectro
            - Frequência dominante indica portadora (se houver)
        
        Avisos:
            - Sinais muito curtos podem ter resolução espectral baixa
            - Janelamento não é aplicado (pode haver vazamento espectral)
        
        Aplicações:
            - Identificação de modulação por portadora
            - Análise de largura de banda ocupada
            - Detecção de componentes DC
            - Comparação de densidade espectral de potência
        
        Conceitos de Telecomunicações:
            - FFT: Ferramenta fundamental para análise de sinais
            - Espectro: Representação no domínio da frequência
            - Magnitude dB: 20*log₁₀(|X(f)|) - escala logarítmica
            - Freq. Dominante: Componente com maior energia
            - Largura de banda: Faixa de frequências significativas
        """
        if self.ultimo_sinal_tx is None or self.ultimo_sinal_rx is None:
            return

        # Limpar gráficos
        self.ax_esp_tx.clear()
        self.ax_esp_rx.clear()

        # Configuração
        from config import Config
        config = Config()
        taxa_amostragem = config.TAXA_AMOSTRAGEM  # Hz

        # Calcular FFT do sinal TX
        fft_tx = np.fft.fft(self.ultimo_sinal_tx)
        frequencias_tx = np.fft.fftfreq(len(self.ultimo_sinal_tx), 1/taxa_amostragem)
        
        # Usar apenas metade do espectro (frequências positivas)
        n_tx = len(frequencias_tx) // 2
        freqs_tx = frequencias_tx[:n_tx]
        magnitude_tx = np.abs(fft_tx[:n_tx])
        
        # Converter para dB (evitar log de zero)
        magnitude_tx_db = 20 * np.log10(magnitude_tx + 1e-10)

        # Calcular FFT do sinal RX
        fft_rx = np.fft.fft(self.ultimo_sinal_rx)
        frequencias_rx = np.fft.fftfreq(len(self.ultimo_sinal_rx), 1/taxa_amostragem)
        
        n_rx = len(frequencias_rx) // 2
        freqs_rx = frequencias_rx[:n_rx]
        magnitude_rx = np.abs(fft_rx[:n_rx])
        magnitude_rx_db = 20 * np.log10(magnitude_rx + 1e-10)

        # Plotar espectro TX
        self.ax_esp_tx.plot(freqs_tx, magnitude_tx_db, 'b-', linewidth=0.8)
        self.ax_esp_tx.set_xlabel('Frequência (Hz)', fontsize=9)
        self.ax_esp_tx.set_ylabel('Magnitude (dB)', fontsize=9)
        self.ax_esp_tx.set_title('Espectro do Sinal Transmitido (TX)', fontsize=10, fontweight='bold')
        self.ax_esp_tx.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)
        self.ax_esp_tx.tick_params(labelsize=8)
        
        # Estatísticas TX
        freq_dominante_tx = freqs_tx[np.argmax(magnitude_tx)]
        potencia_tx = np.sum(magnitude_tx**2) / len(magnitude_tx)
        stats_esp_tx = f'Freq. Dominante: {freq_dominante_tx:.1f}Hz  Potência: {10*np.log10(potencia_tx):.1f}dB'
        self.ax_esp_tx.text(0.02, 0.98, stats_esp_tx, transform=self.ax_esp_tx.transAxes, 
                fontsize=7, verticalalignment='top', 
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

        # Plotar espectro RX
        self.ax_esp_rx.plot(freqs_rx, magnitude_rx_db, 'r-', linewidth=0.8, alpha=0.8)
        self.ax_esp_rx.set_xlabel('Frequência (Hz)', fontsize=9)
        self.ax_esp_rx.set_ylabel('Magnitude (dB)', fontsize=9)
        self.ax_esp_rx.set_title('Espectro do Sinal Recebido (RX)', fontsize=10, fontweight='bold')
        self.ax_esp_rx.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)
        self.ax_esp_rx.tick_params(labelsize=8)
        
        # Estatísticas RX
        freq_dominante_rx = freqs_rx[np.argmax(magnitude_rx)]
        potencia_rx = np.sum(magnitude_rx**2) / len(magnitude_rx)
        stats_esp_rx = f'Freq. Dominante: {freq_dominante_rx:.1f}Hz  Potência: {10*np.log10(potencia_rx):.1f}dB'
        self.ax_esp_rx.text(0.02, 0.98, stats_esp_rx, transform=self.ax_esp_rx.transAxes, 
                fontsize=7, verticalalignment='top', 
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

        plt.tight_layout()
        self.canvas_espectro.draw()

    def iniciar(self):
        """
        Inicia o loop principal da interface gráfica Tkinter.
        
        Este método bloqueia a execução até que a janela seja fechada pelo usuário.
        É o ponto de entrada para executar a aplicação GUI.
        
        Comportamento:
            - Entra no loop de eventos do Tkinter
            - Processa eventos de mouse, teclado, timers, etc.
            - Mantém a janela responsiva
            - Bloqueia até janela ser fechada
        
        Returns:
            None: Retorna quando a janela é fechada
        
        Exemplos:
            >>> from interface.gui import InterfaceGrafica
            >>> app = InterfaceGrafica()
            >>> app.iniciar()  # Bloqueia aqui até fechar janela
            >>> print("Aplicação encerrada")
        
        Notas:
            - Deve ser chamado após criação da InterfaceGrafica
            - Único método público que precisa ser chamado externamente
            - Loop principal do Tkinter processa callbacks, threads, etc.
        
        Avisos:
            - Código após este método só executa quando janela for fechada
            - Threads daemon criadas terminam automaticamente
        
        Aplicações:
            - Ponto de entrada padrão para aplicações Tkinter
            - Usado em main.py ou scripts de inicialização
        """
        self.root.mainloop()
