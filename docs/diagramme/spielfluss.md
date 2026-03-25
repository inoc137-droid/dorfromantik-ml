# Spielfluss-Diagramm

Dieses Dokument beschreibt den aktuell implementierten Spielfluss aus [`src/dorfromantik/env.py`](/C:/Users/Kevin/PycharmProjects/dorfromantik-ml/src/dorfromantik/env.py).

## Mermaid

```mermaid
flowchart TD
    A[Reset] --> B[Stacks aufbauen]
    B --> C[_advance_after_turn]
    C --> D{Tile gespeichert?}

    D -- Ja --> E[Phase: choose_next_tile_source]
    D -- Nein --> F{Weniger als 3 aktive Auftraege<br/>und Task-Stack nicht leer?}

    F -- Ja --> G[Task-Tile ziehen]
    F -- Nein --> H[Main-Tile ziehen]

    G --> I[Phase: place_tile]
    H --> I

    E --> J{Quelle waehlen}
    J -- storehouse --> K[Tile aus Lagerhaus nehmen]
    J -- kontor --> L[Tile aus Kontor nehmen]
    J -- task --> G
    J -- main --> H

    K --> I
    L --> I

    I --> M{Aktion}
    M -- store_tile --> N{Tile-Typ?}
    M -- place_tile --> O{Platzierung legal?}
    M -- andere Aktion --> X[Illegal: Reward -1, Done]

    N -- Landschaft --> P[In storehouse oder kontor ablegen]
    N -- Sonder --> Q[Nur in kontor ablegen]
    N -- Auftrag/Tempel --> X

    P --> R[current_tile = None]
    Q --> R
    R --> C

    O -- Nein --> X
    O -- Ja --> S[Tile auf Board legen]
    S --> T[Frontier aktualisieren]
    T --> U[DSU und Feature-Gebiete aktualisieren]

    U --> V{Auftragsplaettchen?}
    V -- Ja --> W[Passenden Task-Marker ziehen<br/>und Auftrag aktivieren]
    V -- Nein --> Y[Aktive Auftraege pruefen]

    W --> Y
    Y --> Z[Erfuellte oder verlorene Auftraege verbuchen]
    Z --> AA[current_tile = None]
    AA --> C

    C --> AC{Legale Folgeaktionen vorhanden?}
    AC -- Ja --> AD[Spiel laeuft weiter]
    AC -- Nein --> AE[Done]
```

## Dateien

- Mermaid-Quelle: [`docs/diagramme/spielfluss.mmd`](/C:/Users/Kevin/PycharmProjects/dorfromantik-ml/docs/diagramme/spielfluss.mmd)
- SVG-Ausgabe: [`docs/diagramme/spielfluss.svg`](/C:/Users/Kevin/PycharmProjects/dorfromantik-ml/docs/diagramme/spielfluss.svg)
