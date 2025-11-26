#!/usr/bin/env python3
"""
Simulador de Comunicação Digital - Projeto TR1

Este é o ponto de entrada principal do simulador de comunicação digital
desenvolvido para a disciplina de Transmissão de Dados (TR1). O simulador
implementa um sistema completo de comunicação digital com interface gráfica.

Funcionalidades Principais:
    - Modulação Digital: NRZ-Polar, Manchester, Bipolar
    - Modulação por Portadora: ASK, FSK, QPSK, 16-QAM
    - Detecção de Erros: Paridade, Checksum, CRC (8/16/24/32 bits)
    - Correção de Erros: Código de Hamming (SECDED)
    - Enquadramento: Contagem de bytes, Byte stuffing
    - Simulação de Canal: Ruído AWGN configurável
    - Visualização: Gráficos de sinal no tempo e espectro (FFT)

Arquitetura:
    O simulador segue arquitetura em camadas inspirada no modelo OSI:
    
    Camada de Aplicação: Interface gráfica (Tkinter + Matplotlib)
           ↓
    Camada de Enlace: Enquadramento + Detecção/Correção de erros
           ↓
    Camada Física: Modulação Digital/Portadora
           ↓
    Canal: Transmissão com ruído AWGN
           ↓
    [Processo inverso no receptor]

Uso:
    $ python3 main.py
    
    A interface gráfica permite:
    - Configurar todos os parâmetros de transmissão
    - Enviar mensagens de texto
    - Visualizar sinais e espectros
    - Analisar desempenho (SNR, BER, erros detectados/corrigidos)

Configurações Principais:
    - Taxa de Amostragem: 100-10000 Hz
    - Taxa de Bits: 1-1000 bps
    - Frequência Portadora: 10-1000 Hz (para modulações por portadora)
    - Amplitude: 5V (padrão)
    - Ruído: μ e σ configuráveis
    - Tamanho do Quadro: 64-1024 bytes
    - Tamanho do EDC: 8/16/24/32 bits

Autores:
    Desenvolvido como projeto da disciplina TR1

Versão:
    1.0 - Implementação completa com todas as funcionalidades
"""
from interface import InterfaceGrafica

def main():
    """
    Função principal do simulador.
    
    Inicializa e executa a interface gráfica do simulador de comunicação
    digital. A interface permanece ativa até ser fechada pelo usuário.
    
    O simulador carrega configurações padrão de Config() que podem ser
    ajustadas através da interface gráfica.
    
    Fluxo de Execução:
        1. Imprime cabeçalho no console
        2. Cria instância da InterfaceGrafica
        3. Inicia loop principal da interface (Tkinter mainloop)
        4. Aguarda interação do usuário
        5. Finaliza quando janela é fechada
    
    Raises:
        Exception: Erros críticos são capturados e exibidos na interface.
    
    Exemplos:
        $ python3 main.py
        ======================================================================
        SIMULADOR DE CAMADAS DE REDE - TR1
        Arquitetura Orientada a Objetos
        ======================================================================
        [Interface gráfica é aberta]
    """
    print("="*70)
    print("SIMULADOR DE CAMADAS DE REDE - TR1")
    print("Arquitetura Orientada a Objetos")
    print("="*70)
    print()

    # Cria e inicia interface gráfica
    app = InterfaceGrafica()
    app.iniciar()

if __name__ == "__main__":
    main()
