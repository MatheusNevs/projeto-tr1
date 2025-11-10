#!/usr/bin/env python3
"""
Ponto de entrada do simulador TR1
Inicia a interface gráfica
"""
from interface import InterfaceGrafica

def main():
    """Função principal"""
    print("="*70)
    print("SIMULADOR DE CAMADAS DE REDE - TR1")
    print("Arquitetura Orientada a Objetos")
    print("="*70)
    print()

    # Cria e inicia interface
    app = InterfaceGrafica()
    app.iniciar()

if __name__ == "__main__":
    main()
