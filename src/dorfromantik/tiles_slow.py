from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Tuple
from . import tile_types as tt


@dataclass(frozen=True)
class TileDef:
    edges: tt.Edges
    name: str = "generic_tile"  # Default

    # Definieren von TileDef durch 6-Tupel mit int: TileDef((1,2,0,0,1,2))
    def __post_init__(self):
        object.__setattr__(
            self,
            "edges",
            tuple(tt.EdgeType(e) for e in self.edges)
        )


def rotate_edges(edges: tt.Edges, rot: int) -> tt.Edges:
    rot %= 6
    # Rotation mit dem Uhrzeigersinn drehend Alte 0 -> Neue 1
    return tuple(edges[(i + rot) % 6] for i in range(6))  # ignoriere Typ


# Start: oben, Rotation: Uhrzeigersinn
TILES: Dict[int, TileDef] = {
    0: TileDef((
        tt.EdgeType.Reis, tt.EdgeType.Strasse, tt.EdgeType.Wiese, tt.EdgeType.Strasse, tt.EdgeType.Reis,
        tt.EdgeType.Reis
    )),
    1: TileDef((
        4, 3, 3, 0, 2, 2
    )),
    2: TileDef((
        1, 1, 3, 3, 3, 1
    )),
    3: TileDef((
        3, 3, 2, 2, 2, 3
    )),
    4: TileDef((
        1, 1, 2, 2, 3, 3
    )),
    5: TileDef((
        5, 0, 2, 5, 1, 1
    )),
    6: TileDef((
        2, 0, 2, 2, 2, 2
    ))
}
