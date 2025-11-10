# Arquitetura Orientada a Objetos - Simulador TR1

## Estrutura de Classes

```
├── camada_fisica/
│   ├── __init__.py
│   ├── modulador_digital.py    # Classes abstratas e implementações
│   └── modulador_portadora.py  # ASK, FSK, QPSK, QAM
│
├── camada_enlace/
│   ├── __init__.py
│   ├── enquadrador.py          # Classes de enquadramento
│   ├── detector_erros.py       # Paridade, Checksum, CRC
│   └── corretor_erros.py       # Hamming
│
├── comunicacao/
│   ├── __init__.py
│   ├── canal.py                # Canal com ruído
│   ├── transmissor.py          # Classe Transmissor
│   └── receptor.py             # Classe Receptor
│
├── interface/
│   ├── __init__.py
│   └── gui.py                  # Interface Gráfica
│
├── utils/
│   ├── __init__.py
│   └── conversor.py            # Funções de conversão
│
├── config.py                   # Configurações
└── main.py                     # Ponto de entrada
```

## Diagrama de Classes (UML Simplificado)

```
┌─────────────────────────────────────────────────────────────┐
│                    InterfaceGrafica                          │
├─────────────────────────────────────────────────────────────┤
│ - transmissor: Transmissor                                   │
│ - receptor: Receptor                                         │
│ - canal: CanalComunicacao                                    │
│ - thread_receptor: Thread                                    │
├─────────────────────────────────────────────────────────────┤
│ + iniciar()                                                  │
│ + enviar_mensagem(texto)                                     │
│ + processar_recepcao()                                       │
└─────────────────────────────────────────────────────────────┘
                    │                    │
        ┌───────────┘                    └───────────┐
        │                                            │
        ▼                                            ▼
┌──────────────────┐                        ┌──────────────────┐
│  Transmissor     │                        │    Receptor      │
├──────────────────┤                        ├──────────────────┤
│ - modulador      │                        │ - demodulador    │
│ - enquadrador    │                        │ - desenquadrador │
│ - detector       │                        │ - verificador    │
│ - corretor       │                        │ - corretor       │
├──────────────────┤                        ├──────────────────┤
│ + transmitir()   │                        │ + receber()      │
└──────────────────┘                        └──────────────────┘
        │                                            │
        └────────────────┐      ┌──────────────────┘
                         ▼      ▼
                  ┌──────────────────┐
                  │ CanalComunicacao │
                  ├──────────────────┤
                  │ - nivel_ruido    │
                  ├──────────────────┤
                  │ + transmitir()   │
                  └──────────────────┘
```

## Padrões de Design Utilizados

1. **Strategy Pattern**: Para diferentes algoritmos de modulação/enquadramento
2. **Abstract Factory**: Para criar famílias de objetos relacionados
3. **Observer Pattern**: Para notificar a GUI sobre eventos
4. **Singleton**: Para configurações globais
