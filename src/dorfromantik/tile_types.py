from __future__ import annotations
from dataclasses import dataclass
from enum import IntEnum
from typing import Tuple

Pos = Tuple[int, int] # axial (q,r)


class EdgeType(IntEnum):
    Wiese = 0           # falls benötigt
    Sakura = 1
    Reis = 2
    Dorf = 3
    Strasse = 4
    Fluss = 5
    Heisse_Quellen = 6
    Wolken = 7
    Vulkan = 8
    Bunte_Fahne = 9


# Plättchentyp Landschaft = {Landschaft, Sonder, Auftrag, Tempel}
class TileGroup(IntEnum):
    Landschaft = 0
    Sonder = 1
    Auftrag = 2
    Tempel = 3


# Auftragstyp
class TaskType(IntEnum):
    Sakura = 1
    Reis = 2
    Dorf = 3
    Strasse = 4
    Fluss = 5
    Rundum = 6
    SakuraReis = 12
    SakuraDorf = 13
    ReisDorf = 23


CONTINUITY_TYPES = {
    EdgeType.Strasse,
    EdgeType.Fluss,
    EdgeType.Vulkan,
    EdgeType.Heisse_Quellen
}

Edges = Tuple[EdgeType, EdgeType, EdgeType, EdgeType, EdgeType, EdgeType]

# axiale Nachbarliste. 1. Position Waagrechte / x-Achse, 2. Position entlang der 60° Achse nach "rechts oben"
DIRS: Tuple[Pos, ...] = (
    (0, 1),    # 0: oben
    (1, 0),    # 1: oben rechts
    (1, -1),   # 2: unten rechts
    (0, -1),   # 3: unten
    (-1, 0),   # 4: unten links
    (-1, 1),   # 5: oben links
)

def add_pos(a: Pos, b: Pos) -> Pos:
    return (a[0] + b[0], a[1] + b[1])

def neighbor(a: Pos, edge_idx: int) -> Pos:
    dq, dr = DIRS[edge_idx]
    return (a[0]+dq, a[1]+dr)

def opposite_edge(edge_idx: int) -> int:
    return (edge_idx + 3) % 6
