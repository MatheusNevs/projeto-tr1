"""
Interface Gráfica com Tkinter
Thread separada para receptor
"""
import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import queue
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
        self.root.geometry("1000x800")

        # Componentes de comunicação
        self.transmissor = None
        self.receptor = None
        self.canal = CanalComunicacao()

        # Thread e fila para receptor
        self.fila_recepcao = queue.Queue()
        self.receptor_ativo = False

        self._criar_interface()
        self._configurar_componentes()

    def _criar_interface(self):
        """Cria todos os widgets da interface"""

        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Título
        titulo = ttk.Label(main_frame, text="Simulador de Comunicação - TR1", 
                          font=('Arial', 16, 'bold'))
        titulo.grid(row=0, column=0, columnspan=3, pady=10)

        # === CONFIGURAÇÕES ===
        config_frame = ttk.LabelFrame(main_frame, text="Configurações", padding="10")
        config_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)

        # Tipo de Modulação
        ttk.Label(config_frame, text="Tipo de Modulação:").grid(row=0, column=0, sticky=tk.W)
        self.combo_tipo_modulacao = ttk.Combobox(config_frame, width=20, state='readonly',
                                                 values=['Digital', 'Portadora'])
        self.combo_tipo_modulacao.set('Digital')
        self.combo_tipo_modulacao.grid(row=0, column=1, padx=5)
        self.combo_tipo_modulacao.bind('<<ComboboxSelected>>', self._atualizar_opcoes_modulacao)

        # Modulação Digital
        ttk.Label(config_frame, text="Modulação:").grid(row=0, column=2, sticky=tk.W, padx=(20,0))
        self.combo_modulacao = ttk.Combobox(config_frame, width=20, state='readonly',
                                            values=['NRZ-Polar', 'Manchester', 'Bipolar'])
        self.combo_modulacao.set('NRZ-Polar')
        self.combo_modulacao.grid(row=0, column=3, padx=5)

        # Enquadramento
        ttk.Label(config_frame, text="Enquadramento:").grid(row=1, column=0, sticky=tk.W)
        self.combo_enquadramento = ttk.Combobox(config_frame, width=20, state='readonly',
                                                values=['Contagem', 'FLAGS Bits'])
        self.combo_enquadramento.set('Contagem')
        self.combo_enquadramento.grid(row=1, column=1, padx=5)

        # Detecção de Erros
        ttk.Label(config_frame, text="Detecção:").grid(row=1, column=2, sticky=tk.W, padx=(20,0))
        self.combo_deteccao = ttk.Combobox(config_frame, width=20, state='readonly',
                                           values=['Paridade', 'Checksum', 'CRC-32'])
        self.combo_deteccao.set('CRC-32')
        self.combo_deteccao.grid(row=1, column=3, padx=5)

        # Hamming
        self.var_hamming = tk.BooleanVar(value=True)
        ttk.Checkbutton(config_frame, text="Usar Código de Hamming", 
                       variable=self.var_hamming).grid(row=2, column=0, columnspan=2, sticky=tk.W)

        # Nível de Ruído
        ttk.Label(config_frame, text="Ruído (σ):").grid(row=2, column=2, sticky=tk.W, padx=(20,0))
        self.slider_ruido = ttk.Scale(config_frame, from_=0, to=2, orient=tk.HORIZONTAL, length=150)
        self.slider_ruido.set(0.3)
        self.slider_ruido.grid(row=2, column=3, padx=5, sticky=(tk.W, tk.E))
        self.label_ruido = ttk.Label(config_frame, text="0.3")
        self.label_ruido.grid(row=2, column=4)
        self.slider_ruido.configure(command=self._atualizar_label_ruido)

        # Botão aplicar configurações
        ttk.Button(config_frame, text="Aplicar Configurações", 
                  command=self._configurar_componentes).grid(row=3, column=0, columnspan=5, pady=10)

        # === TRANSMISSÃO ===
        tx_frame = ttk.LabelFrame(main_frame, text="Transmissão", padding="10")
        tx_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)

        ttk.Label(tx_frame, text="Mensagem:").grid(row=0, column=0, sticky=tk.W)
        self.entry_mensagem = ttk.Entry(tx_frame, width=60)
        self.entry_mensagem.insert(0, "Hello World from TR1!")
        self.entry_mensagem.grid(row=0, column=1, padx=5)

        ttk.Button(tx_frame, text="Transmitir", 
                  command=self._transmitir).grid(row=0, column=2, padx=5)

        # === LOGS ===
        logs_frame = ttk.LabelFrame(main_frame, text="Logs da Comunicação", padding="10")
        logs_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)

        self.text_logs = scrolledtext.ScrolledText(logs_frame, width=100, height=25, 
                                                   font=('Courier', 9))
        self.text_logs.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Botão limpar
        ttk.Button(logs_frame, text="Limpar Logs", 
                  command=self._limpar_logs).grid(row=1, column=0, pady=5)

        # === STATUS ===
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E))

        self.label_status = ttk.Label(status_frame, text="Pronto", 
                                      font=('Arial', 10, 'bold'))
        self.label_status.grid(row=0, column=0, sticky=tk.W)

        # Configurar redimensionamento
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)

    def _atualizar_label_ruido(self, valor):
        """Atualiza label do slider de ruído"""
        self.label_ruido.config(text=f"{float(valor):.2f}")

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

        # Enquadrador
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

        # Criar transmissor e receptor
        self.transmissor = Transmissor(modulador_tx, enquadrador_tx, detector_tx, usar_hamming)
        self.receptor = Receptor(modulador_rx, enquadrador_rx, detector_rx, usar_hamming)

        # Configurar canal
        nivel_ruido = self.slider_ruido.get()
        self.canal.set_nivel_ruido(nivel_ruido)

        self._log(f"Tipo: {tipo_mod}")
        self._log(f"Modulação: {mod_tipo}")
        self._log(f"Enquadramento: {enq_tipo}")
        self._log(f"Detecção: {det_tipo}")
        self._log(f"Hamming: {'Sim' if usar_hamming else 'Não'}")
        self._log(f"Ruído: σ={nivel_ruido:.2f}")
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

        # Atualiza nível de ruído
        self.canal.set_nivel_ruido(self.slider_ruido.get())

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

            # Canal
            self._log("\n>>> CANAL DE COMUNICAÇÃO <<<")
            sinal_rx = self.canal.transmitir(sinal_tx)
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

        except Exception as e:
            self._log(f"\nERRO DURANTE TRANSMISSÃO: {e}")
            import traceback
            self._log(traceback.format_exc())
            self.root.after(0, lambda: self.label_status.config(text="Erro!"))

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

    def iniciar(self):
        """Inicia a interface gráfica"""
        self.root.mainloop()
