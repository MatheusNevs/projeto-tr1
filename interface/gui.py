"""
Interface Gráfica com Tkinter
Thread separada para receptor
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
from camada_enlace.detector_erros import DetectorParidade, DetectorChecksum, DetectorCRC32

class InterfaceGrafica:
    """Interface gráfica principal do simulador"""

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
        """Cria todos os widgets da interface"""

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
                                           values=['Paridade', 'Checksum', 'CRC-32'])
        self.combo_deteccao.set('CRC-32')
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

        # Linha 3: Média do Ruído (μ)
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

        # Linha 5: Botão aplicar
        ttk.Button(config_frame, text="Aplicar Configurações", 
                  command=self._configurar_componentes).grid(row=5, column=0, columnspan=4, pady=(10, 0))

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
        self.canvas = FigureCanvasTkAgg(self.fig, master=aba_forma_onda)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        # Adicionar barra de ferramentas de navegação
        toolbar_frame = ttk.Frame(aba_forma_onda)
        toolbar_frame.pack(fill=tk.X, padx=2, pady=(0, 2))
        
        self.toolbar = NavigationToolbar2Tk(self.canvas, toolbar_frame)
        self.toolbar.update()

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

        # Incorporar matplotlib no tkinter
        self.canvas_espectro = FigureCanvasTkAgg(self.fig_espectro, master=aba_espectro)
        self.canvas_espectro.draw()
        self.canvas_espectro.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        # Adicionar barra de ferramentas de navegação para espectro
        toolbar_esp_frame = ttk.Frame(aba_espectro)
        toolbar_esp_frame.pack(fill=tk.X, padx=2, pady=(0, 2))
        
        self.toolbar_espectro = NavigationToolbar2Tk(self.canvas_espectro, toolbar_esp_frame)
        self.toolbar_espectro.update()

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
        """Atualiza label do slider de desvio do ruído"""
        self.label_ruido_desvio.config(text=f"{float(valor):.2f}")

    def _atualizar_label_ruido_media(self, valor):
        """Atualiza label do slider de média do ruído"""
        self.label_ruido_media.config(text=f"{float(valor):.2f}")

    def _atualizar_label_tamanho_quadro(self, valor):
        """Atualiza label do slider de tamanho máximo do quadro"""
        tamanho = int(float(valor))
        self.label_tamanho_quadro.config(text=f"{tamanho} bytes")

    def _atualizar_opcoes_modulacao(self, event=None):
        """Atualiza as opções de modulação baseado no tipo selecionado"""
        tipo = self.combo_tipo_modulacao.get()
        if tipo == 'Digital':
            self.combo_modulacao.config(values=['NRZ-Polar', 'Manchester', 'Bipolar'])
            self.combo_modulacao.set('NRZ-Polar')
        else:  # Portadora
            self.combo_modulacao.config(values=['ASK', 'FSK', 'QPSK', '16-QAM'])
            self.combo_modulacao.set('ASK')

    def _configurar_componentes(self):
        """Configura TX, RX e Canal com base nas seleções"""
        self._log("=== CONFIGURANDO COMPONENTES ===")

        # PRIMEIRO: Configurar tamanho máximo do quadro (antes de criar enquadradores!)
        tamanho_quadro = int(self.slider_tamanho_quadro.get())
        from config import Config
        config = Config()
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

        # Detector
        det_tipo = self.combo_deteccao.get()
        if det_tipo == 'Paridade':
            detector_tx = DetectorParidade()
            detector_rx = DetectorParidade()
        elif det_tipo == 'Checksum':
            detector_tx = DetectorChecksum()
            detector_rx = DetectorChecksum()
        else:  # CRC-32
            detector_tx = DetectorCRC32()
            detector_rx = DetectorCRC32()

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

        self._log(f"Tipo: {tipo_mod}")
        self._log(f"Modulação: {mod_tipo}")
        self._log(f"Enquadramento: {enq_tipo}")
        self._log(f"Detecção: {det_tipo}")
        self._log(f"Hamming: {'Sim' if usar_hamming else 'Não'}")
        self._log(f"Ruído: μ={nivel_ruido_media:.2f}, σ={nivel_ruido_desvio:.2f}")
        self._log(f"Tamanho Máx. Quadro: {tamanho_quadro} bytes ({tamanho_quadro * 8} bits)")
        self._log("Configuração concluída!\n")

    def _transmitir(self):
        """Executa transmissão em thread separada"""
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
        """Processa transmissão (roda em thread separada)"""
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
        """Adiciona mensagem aos logs (thread-safe)"""
        def adicionar():
            self.text_logs.insert(tk.END, mensagem + "\n")
            self.text_logs.see(tk.END)

        # Se chamado de thread, agenda para thread principal
        self.root.after(0, adicionar)

    def _limpar_logs(self):
        """Limpa área de logs"""
        self.text_logs.delete(1.0, tk.END)
        if self.transmissor:
            self.transmissor.limpar_historico()
        if self.receptor:
            self.receptor.limpar_historico()

    def _atualizar_graficos(self):
        """Atualiza os gráficos na interface principal"""
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
        """Atualiza os gráficos de espectro (FFT)"""
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
        """Inicia a interface gráfica"""
        self.root.mainloop()
