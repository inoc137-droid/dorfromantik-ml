from __future__ import annotations
from dataclasses import dataclass
from collections import defaultdict
from typing import Dict, Tuple
from . import tile_types as tt


@dataclass(frozen=True)
class TileDef:
    edges: tt.Edges
    tile_group: tt.TileGroup
    flower_type: tt.EdgeType | None = None
    flag_type: tt.EdgeType | None = None
    task_type: tt.TaskType | None = None
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
    return tuple(edges[(i - rot) % 6] for i in range(6))  # ignoriere Typ


# Start: oben, Rotation: Uhrzeigersinn
# 46 Landschaft, 25 Sonder, 39 Auftrag
TILES: Dict[int, TileDef] = {
    0: TileDef((tt.EdgeType.Reis, tt.EdgeType.Strasse, tt.EdgeType.Wiese,
                tt.EdgeType.Strasse, tt.EdgeType.Reis, tt.EdgeType.Reis),
                tile_group=tt.TileGroup.Landschaft),
    1: TileDef((tt.EdgeType.Strasse, tt.EdgeType.Dorf, tt.EdgeType.Dorf,
                tt.EdgeType.Wiese, tt.EdgeType.Reis, tt.EdgeType.Reis),
                tile_group=tt.TileGroup.Landschaft),
    2: TileDef((tt.EdgeType.Sakura, tt.EdgeType.Sakura, tt.EdgeType.Dorf,
                tt.EdgeType.Dorf, tt.EdgeType.Dorf, tt.EdgeType.Sakura),
                tile_group=tt.TileGroup.Landschaft),
    3: TileDef((tt.EdgeType.Dorf, tt.EdgeType.Dorf, tt.EdgeType.Reis,
                tt.EdgeType.Reis, tt.EdgeType.Reis, tt.EdgeType.Dorf),
                tile_group=tt.TileGroup.Landschaft),
    4: TileDef((tt.EdgeType.Sakura, tt.EdgeType.Sakura, tt.EdgeType.Reis,
                tt.EdgeType.Reis, tt.EdgeType.Dorf, tt.EdgeType.Dorf),
                tile_group=tt.TileGroup.Landschaft),
    5: TileDef((tt.EdgeType.Fluss, tt.EdgeType.Wiese, tt.EdgeType.Reis,
                tt.EdgeType.Fluss, tt.EdgeType.Sakura, tt.EdgeType.Sakura),
                tile_group=tt.TileGroup.Landschaft),
    6: TileDef((tt.EdgeType.Reis, tt.EdgeType.Wiese, tt.EdgeType.Reis,
                tt.EdgeType.Reis, tt.EdgeType.Reis, tt.EdgeType.Reis),
                tile_group=tt.TileGroup.Landschaft),
    7: TileDef((tt.EdgeType.Reis, tt.EdgeType.Reis, tt.EdgeType.Wiese,
                tt.EdgeType.Dorf, tt.EdgeType.Wiese, tt.EdgeType.Reis),
                tile_group=tt.TileGroup.Landschaft, flower_type=tt.EdgeType.Reis),  # Reis Blüte 1
    8: TileDef((tt.EdgeType.Wiese, tt.EdgeType.Sakura, tt.EdgeType.Sakura,
                tt.EdgeType.Fluss, tt.EdgeType.Reis, tt.EdgeType.Reis),
                tile_group=tt.TileGroup.Landschaft),
    9: TileDef((tt.EdgeType.Fluss, tt.EdgeType.Sakura, tt.EdgeType.Sakura,
                tt.EdgeType.Wiese, tt.EdgeType.Dorf, tt.EdgeType.Dorf),
                tile_group=tt.TileGroup.Landschaft),
    10: TileDef((tt.EdgeType.Strasse, tt.EdgeType.Wiese, tt.EdgeType.Reis,
                tt.EdgeType.Strasse, tt.EdgeType.Dorf, tt.EdgeType.Dorf),
                tile_group=tt.TileGroup.Landschaft),
    11: TileDef((tt.EdgeType.Wiese, tt.EdgeType.Sakura, tt.EdgeType.Wiese,
                tt.EdgeType.Sakura, tt.EdgeType.Wiese, tt.EdgeType.Sakura),
                tile_group=tt.TileGroup.Landschaft, flower_type=tt.EdgeType.Sakura),  # Sakura Blüte 1
    12: TileDef((tt.EdgeType.Strasse, tt.EdgeType.Wiese, tt.EdgeType.Strasse,
                tt.EdgeType.Sakura, tt.EdgeType.Sakura, tt.EdgeType.Sakura),
                tile_group=tt.TileGroup.Landschaft),
    13: TileDef((tt.EdgeType.Sakura, tt.EdgeType.Sakura, tt.EdgeType.Wiese,
                tt.EdgeType.Reis, tt.EdgeType.Wiese, tt.EdgeType.Sakura),
                tile_group=tt.TileGroup.Landschaft, flower_type=tt.EdgeType.Sakura),  # Sakura Blüte 2
    14: TileDef((tt.EdgeType.Wiese, tt.EdgeType.Dorf, tt.EdgeType.Dorf,
                tt.EdgeType.Dorf, tt.EdgeType.Dorf, tt.EdgeType.Dorf),
                tile_group=tt.TileGroup.Landschaft),
    15: TileDef((tt.EdgeType.Sakura, tt.EdgeType.Sakura, tt.EdgeType.Dorf,
                tt.EdgeType.Dorf, tt.EdgeType.Reis, tt.EdgeType.Reis),
                tile_group=tt.TileGroup.Landschaft),
    16: TileDef((tt.EdgeType.Fluss, tt.EdgeType.Fluss, tt.EdgeType.Dorf,
                tt.EdgeType.Dorf, tt.EdgeType.Dorf, tt.EdgeType.Dorf),
                tile_group=tt.TileGroup.Landschaft, flower_type=tt.EdgeType.Dorf),  # Dorf Blüte 1
    17: TileDef((tt.EdgeType.Strasse, tt.EdgeType.Sakura, tt.EdgeType.Wiese,
                tt.EdgeType.Strasse, tt.EdgeType.Dorf, tt.EdgeType.Dorf),
                tile_group=tt.TileGroup.Landschaft, flower_type=tt.EdgeType.Strasse),  # Strassen Blüte 1
    18: TileDef((tt.EdgeType.Fluss, tt.EdgeType.Reis, tt.EdgeType.Wiese,
                tt.EdgeType.Fluss, tt.EdgeType.Dorf, tt.EdgeType.Dorf),
                tile_group=tt.TileGroup.Landschaft, flower_type=tt.EdgeType.Fluss),  # Fluss Blüte 1
    19: TileDef((tt.EdgeType.Dorf, tt.EdgeType.Dorf, tt.EdgeType.Wiese,
                tt.EdgeType.Sakura, tt.EdgeType.Wiese, tt.EdgeType.Dorf),
                tile_group=tt.TileGroup.Landschaft, flower_type=tt.EdgeType.Dorf),  # Dorf Blüte 2
    20: TileDef((tt.EdgeType.Strasse, tt.EdgeType.Dorf, tt.EdgeType.Wiese,
                tt.EdgeType.Strasse, tt.EdgeType.Sakura, tt.EdgeType.Sakura),
                tile_group=tt.TileGroup.Landschaft, flower_type=tt.EdgeType.Strasse),  # Strassen Blüte 2
    21: TileDef((tt.EdgeType.Strasse, tt.EdgeType.Strasse, tt.EdgeType.Sakura,
                tt.EdgeType.Sakura, tt.EdgeType.Sakura, tt.EdgeType.Sakura),
                tile_group=tt.TileGroup.Landschaft, flower_type=tt.EdgeType.Sakura),  # Sakura Blüte 3
    22: TileDef((tt.EdgeType.Sakura, tt.EdgeType.Sakura, tt.EdgeType.Reis,
                tt.EdgeType.Reis, tt.EdgeType.Reis, tt.EdgeType.Sakura),
                tile_group=tt.TileGroup.Landschaft),
    23: TileDef((tt.EdgeType.Fluss, tt.EdgeType.Wiese, tt.EdgeType.Sakura,
                tt.EdgeType.Fluss, tt.EdgeType.Dorf, tt.EdgeType.Dorf),
                tile_group=tt.TileGroup.Landschaft),
    24: TileDef((tt.EdgeType.Strasse, tt.EdgeType.Strasse, tt.EdgeType.Wiese,
                tt.EdgeType.Dorf, tt.EdgeType.Dorf, tt.EdgeType.Wiese),
                tile_group=tt.TileGroup.Landschaft),
    25: TileDef((tt.EdgeType.Fluss, tt.EdgeType.Sakura, tt.EdgeType.Wiese,
                tt.EdgeType.Fluss, tt.EdgeType.Reis, tt.EdgeType.Reis),
                tile_group=tt.TileGroup.Landschaft, flower_type=tt.EdgeType.Fluss),  # Fluss Blüte 2
    26: TileDef((tt.EdgeType.Strasse, tt.EdgeType.Strasse, tt.EdgeType.Reis,
                tt.EdgeType.Reis, tt.EdgeType.Reis, tt.EdgeType.Reis),
                tile_group=tt.TileGroup.Landschaft, flower_type=tt.EdgeType.Reis),  # Reis Blüte 2
    27: TileDef((tt.EdgeType.Fluss, tt.EdgeType.Wiese, tt.EdgeType.Fluss,
                tt.EdgeType.Reis, tt.EdgeType.Reis, tt.EdgeType.Reis),
                tile_group=tt.TileGroup.Landschaft),
    28: TileDef((tt.EdgeType.Fluss, tt.EdgeType.Fluss, tt.EdgeType.Wiese,
                tt.EdgeType.Sakura, tt.EdgeType.Sakura, tt.EdgeType.Wiese),
                tile_group=tt.TileGroup.Landschaft),
    29: TileDef((tt.EdgeType.Fluss, tt.EdgeType.Dorf, tt.EdgeType.Wiese,
                tt.EdgeType.Fluss, tt.EdgeType.Sakura, tt.EdgeType.Sakura),
                tile_group=tt.TileGroup.Landschaft, flower_type=tt.EdgeType.Fluss),  # Fluss Blüte 3
    30: TileDef((tt.EdgeType.Sakura, tt.EdgeType.Wiese, tt.EdgeType.Sakura,
                tt.EdgeType.Sakura, tt.EdgeType.Sakura, tt.EdgeType.Sakura),
                tile_group=tt.TileGroup.Landschaft),
    31: TileDef((tt.EdgeType.Wiese, tt.EdgeType.Dorf, tt.EdgeType.Wiese,
                tt.EdgeType.Dorf, tt.EdgeType.Wiese, tt.EdgeType.Dorf),
                tile_group=tt.TileGroup.Landschaft, flower_type=tt.EdgeType.Dorf),  # Dorf Blüte 3
    32: TileDef((tt.EdgeType.Wiese, tt.EdgeType.Reis, tt.EdgeType.Wiese,
                tt.EdgeType.Reis, tt.EdgeType.Wiese, tt.EdgeType.Reis),
                tile_group=tt.TileGroup.Landschaft, flower_type=tt.EdgeType.Reis),  # Reis Blüte 3
    33: TileDef((tt.EdgeType.Strasse, tt.EdgeType.Wiese, tt.EdgeType.Dorf,
                tt.EdgeType.Strasse, tt.EdgeType.Sakura, tt.EdgeType.Sakura),
                tile_group=tt.TileGroup.Landschaft),
    34: TileDef((tt.EdgeType.Strasse, tt.EdgeType.Reis, tt.EdgeType.Wiese,
                tt.EdgeType.Strasse, tt.EdgeType.Sakura, tt.EdgeType.Sakura),
                tile_group=tt.TileGroup.Landschaft, flower_type=tt.EdgeType.Strasse),  # Strassen Blüte 3
    35: TileDef((tt.EdgeType.Strasse, tt.EdgeType.Wiese, tt.EdgeType.Strasse,
                tt.EdgeType.Dorf, tt.EdgeType.Dorf, tt.EdgeType.Dorf),
                tile_group=tt.TileGroup.Landschaft),
    36: TileDef((tt.EdgeType.Fluss, tt.EdgeType.Wiese, tt.EdgeType.Dorf,
                tt.EdgeType.Fluss, tt.EdgeType.Sakura, tt.EdgeType.Sakura),
                tile_group=tt.TileGroup.Landschaft),
    37: TileDef((tt.EdgeType.Fluss, tt.EdgeType.Wiese, tt.EdgeType.Fluss,
                tt.EdgeType.Sakura, tt.EdgeType.Sakura, tt.EdgeType.Sakura),
                tile_group=tt.TileGroup.Landschaft),
    38: TileDef((tt.EdgeType.Fluss, tt.EdgeType.Fluss, tt.EdgeType.Wiese,
                tt.EdgeType.Reis, tt.EdgeType.Reis, tt.EdgeType.Wiese),
                tile_group=tt.TileGroup.Landschaft),
    39: TileDef((tt.EdgeType.Strasse, tt.EdgeType.Reis, tt.EdgeType.Reis,
                tt.EdgeType.Strasse, tt.EdgeType.Wiese, tt.EdgeType.Sakura),
                tile_group=tt.TileGroup.Landschaft),
    40: TileDef((tt.EdgeType.Dorf, tt.EdgeType.Dorf, tt.EdgeType.Wiese,
                tt.EdgeType.Wiese, tt.EdgeType.Sakura, tt.EdgeType.Wiese),
                tile_group=tt.TileGroup.Landschaft, flag_type=tt.EdgeType.Sakura),  # Fahne Sakura 1
    41: TileDef((tt.EdgeType.Reis, tt.EdgeType.Wiese, tt.EdgeType.Sakura,
                tt.EdgeType.Sakura, tt.EdgeType.Wiese, tt.EdgeType.Wiese),
                tile_group=tt.TileGroup.Landschaft, flag_type=tt.EdgeType.Reis),  # Fahne Reis 1
    42: TileDef((tt.EdgeType.Wiese, tt.EdgeType.Dorf, tt.EdgeType.Wiese,
                tt.EdgeType.Reis, tt.EdgeType.Reis, tt.EdgeType.Wiese),
                tile_group=tt.TileGroup.Landschaft, flag_type=tt.EdgeType.Dorf),  # Fahne Dorf 1
    ##### Bis hier sind Standard Tiles. Ohne See, Weggabelung, 2. Fahnen etc..
    43: TileDef((tt.EdgeType.Sakura, tt.EdgeType.Wiese, tt.EdgeType.Wiese,
                tt.EdgeType.Reis, tt.EdgeType.Reis, tt.EdgeType.Wiese),
                tile_group=tt.TileGroup.Landschaft, flag_type=tt.EdgeType.Sakura),  # Fahne Sakura 2
    44: TileDef((tt.EdgeType.Sakura, tt.EdgeType.Wiese, tt.EdgeType.Wiese,
                tt.EdgeType.Dorf, tt.EdgeType.Dorf, tt.EdgeType.Wiese),
                tile_group=tt.TileGroup.Landschaft, flag_type=tt.EdgeType.Reis),  # Fahne Reis 2
    45: TileDef((tt.EdgeType.Dorf, tt.EdgeType.Wiese, tt.EdgeType.Wiese,
                tt.EdgeType.Sakura, tt.EdgeType.Sakura, tt.EdgeType.Wiese),
                tile_group=tt.TileGroup.Landschaft, flag_type=tt.EdgeType.Dorf),  # Fahne Dorf 2
    46: TileDef((tt.EdgeType.Strasse, tt.EdgeType.Strasse, tt.EdgeType.Wiese,
                tt.EdgeType.Wiese, tt.EdgeType.Strasse, tt.EdgeType.Wiese),
                tile_group=tt.TileGroup.Sonder, name="Strassenkreuzung"),
    47: TileDef((tt.EdgeType.Wiese, tt.EdgeType.Fluss, tt.EdgeType.Wiese,
                tt.EdgeType.Wiese, tt.EdgeType.Fluss, tt.EdgeType.Fluss),
                tile_group=tt.TileGroup.Sonder, name="See"),
    # 48: TileDef((tt.EdgeType.Sakura, tt.EdgeType.Sakura, tt.EdgeType.Sakura,
    #             tt.EdgeType.Sakura, tt.EdgeType.Sakura, tt.EdgeType.Sakura),
    #             tile_group=tt.TileGroup.Sonder, name="Moossammlerin"),
    # 49: TileDef((tt.EdgeType.Reis, tt.EdgeType.Reis, tt.EdgeType.Reis,
    #             tt.EdgeType.Reis, tt.EdgeType.Reis, tt.EdgeType.Reis),
    #             tile_group=tt.TileGroup.Sonder, name="Reisbäuerin"),
    # 50: TileDef((tt.EdgeType.Dorf, tt.EdgeType.Dorf, tt.EdgeType.Dorf,
    #             tt.EdgeType.Dorf, tt.EdgeType.Dorf, tt.EdgeType.Dorf),
    #             tile_group=tt.TileGroup.Sonder, name="Sumoringer"),
    # 51: TileDef((tt.EdgeType.Heisse_Quellen, tt.EdgeType.Wiese, tt.EdgeType.Wiese,
    #             tt.EdgeType.Wiese, tt.EdgeType.Wiese, tt.EdgeType.Wiese),
    #             tile_group=tt.TileGroup.Sonder, name="Einsiedler"),
    # 52: TileDef((tt.EdgeType.Vulkan, tt.EdgeType.Vulkan, tt.EdgeType.Wiese,
    #             tt.EdgeType.Sakura, tt.EdgeType.Sakura, tt.EdgeType.Wiese),
    #             tile_group=tt.TileGroup.Sonder, name="Fujiyama", flag_type=tt.EdgeType.Sakura),
    # 53: TileDef((tt.EdgeType.Vulkan, tt.EdgeType.Vulkan, tt.EdgeType.Wiese,
    #             tt.EdgeType.Reis, tt.EdgeType.Reis, tt.EdgeType.Wiese),
    #             tile_group=tt.TileGroup.Sonder, name="Fujiyama", flag_type=tt.EdgeType.Reis),
    # 54: TileDef((tt.EdgeType.Vulkan, tt.EdgeType.Vulkan, tt.EdgeType.Wiese,
    #             tt.EdgeType.Dorf, tt.EdgeType.Dorf, tt.EdgeType.Wiese),
    #             tile_group=tt.TileGroup.Sonder, name="Fujiyama", flag_type=tt.EdgeType.Dorf),
    # 55: TileDef((tt.EdgeType.Heisse_Quellen, tt.EdgeType.Wiese, tt.EdgeType.Dorf,
    #             tt.EdgeType.Sakura, tt.EdgeType.Sakura, tt.EdgeType.Wiese),
    #             tile_group=tt.TileGroup.Sonder, name="Heiße Quellen"),
    # 56: TileDef((tt.EdgeType.Wiese, tt.EdgeType.Reis, tt.EdgeType.Reis,
    #             tt.EdgeType.Dorf, tt.EdgeType.Wiese, tt.EdgeType.Heisse_Quellen),
    #             tile_group=tt.TileGroup.Sonder, name="Heiße Quellen"),
    # 57: TileDef((tt.EdgeType.Strasse, tt.EdgeType.Strasse, tt.EdgeType.Wiese,
    #             tt.EdgeType.Dorf, tt.EdgeType.Wiese, tt.EdgeType.Wiese),
    #             tile_group=tt.TileGroup.Sonder, name="Kalligraph"),
    # 58: TileDef((tt.EdgeType.Sakura, tt.EdgeType.Wiese, tt.EdgeType.Reis,
    #             tt.EdgeType.Wiese, tt.EdgeType.Dorf, tt.EdgeType.Wiese),
    #             tile_group=tt.TileGroup.Sonder, name="Kartograph"),
    # 59: TileDef((tt.EdgeType.Reis, tt.EdgeType.Wiese, tt.EdgeType.Sakura,
    #             tt.EdgeType.Wiese, tt.EdgeType.Dorf, tt.EdgeType.Wiese),
    #             tile_group=tt.TileGroup.Sonder, name="Sternwarte"),
    # 60: TileDef((tt.EdgeType.Bunte_Fahne, tt.EdgeType.Fluss, tt.EdgeType.Fluss,
    #             tt.EdgeType.Wiese, tt.EdgeType.Strasse, tt.EdgeType.Wiese),
    #             tile_group=tt.TileGroup.Sonder, flag_type=tt.EdgeType.Bunte_Fahne, name="Bunte_Fahne"),
    # 61: TileDef((tt.EdgeType.Fluss, tt.EdgeType.Wiese, tt.EdgeType.Wiese,
    #             tt.EdgeType.Wiese, tt.EdgeType.Wiese, tt.EdgeType.Wiese),
    #             tile_group=tt.TileGroup.Sonder, name="Daimyo"),
    # 62: TileDef((tt.EdgeType.Wolken, tt.EdgeType.Wolken, tt.EdgeType.Wiese,
    #            tt.EdgeType.Wolken, tt.EdgeType.Wolken, tt.EdgeType.Wiese),
    #            tile_group=tt.TileGroup.Sonder, name="Kleine Wolken"),
    # 63: TileDef((tt.EdgeType.Strasse, tt.EdgeType.Sakura, tt.EdgeType.Sakura,
    #             tt.EdgeType.Strasse, tt.EdgeType.Reis, tt.EdgeType.Wiese),
    #             tile_group=tt.TileGroup.Sonder, name="Ochsenkarren"),
    # 64: TileDef((tt.EdgeType.Strasse, tt.EdgeType.Dorf, tt.EdgeType.Dorf,
    #             tt.EdgeType.Strasse, tt.EdgeType.Wiese, tt.EdgeType.Reis),
    #             tile_group=tt.TileGroup.Sonder, name="Handelsposten"),
    # 65: TileDef((tt.EdgeType.Wolken, tt.EdgeType.Wolken, tt.EdgeType.Wiese,
    #             tt.EdgeType.Wiese, tt.EdgeType.Wiese, tt.EdgeType.Wiese),
    #             tile_group=tt.TileGroup.Sonder, name="Poet"),
    # 66: TileDef((tt.EdgeType.Fluss, tt.EdgeType.Reis, tt.EdgeType.Reis,
    #             tt.EdgeType.Fluss, tt.EdgeType.Wiese, tt.EdgeType.Sakura),
    #             tile_group=tt.TileGroup.Sonder, name="Schiff"),
    # 67: TileDef((tt.EdgeType.Fluss, tt.EdgeType.Dorf, tt.EdgeType.Dorf,
    #             tt.EdgeType.Fluss, tt.EdgeType.Sakura, tt.EdgeType.Wiese),
    #             tile_group=tt.TileGroup.Sonder, name="Anlegestelle"),
    68: TileDef((tt.EdgeType.Wiese, tt.EdgeType.Sakura, tt.EdgeType.Wiese,
                tt.EdgeType.Reis, tt.EdgeType.Wiese, tt.EdgeType.Sakura),
                tile_group=tt.TileGroup.Tempel, name="Sakura_Tempel"),
    69: TileDef((tt.EdgeType.Wiese, tt.EdgeType.Reis, tt.EdgeType.Wiese,
                tt.EdgeType.Dorf, tt.EdgeType.Wiese, tt.EdgeType.Reis),
                tile_group=tt.TileGroup.Tempel, name="Reis_Tempel"),
    70: TileDef((tt.EdgeType.Wiese, tt.EdgeType.Dorf, tt.EdgeType.Wiese,
                tt.EdgeType.Sakura, tt.EdgeType.Wiese, tt.EdgeType.Dorf),
                tile_group=tt.TileGroup.Tempel, name="Dorf_Tempel"),
    #################   Ab hier sind Auftragsplättchen   #################
    71: TileDef((tt.EdgeType.Sakura, tt.EdgeType.Sakura, tt.EdgeType.Sakura,
                tt.EdgeType.Sakura, tt.EdgeType.Sakura, tt.EdgeType.Sakura),
                tile_group=tt.TileGroup.Auftrag, task_type=tt.TaskType.Sakura),
    72: TileDef((tt.EdgeType.Sakura, tt.EdgeType.Wiese, tt.EdgeType.Wiese,
                tt.EdgeType.Sakura, tt.EdgeType.Wiese, tt.EdgeType.Wiese),
                tile_group=tt.TileGroup.Auftrag, task_type=tt.TaskType.Sakura),
    73: TileDef((tt.EdgeType.Wiese, tt.EdgeType.Wiese, tt.EdgeType.Sakura,
                tt.EdgeType.Sakura, tt.EdgeType.Wiese, tt.EdgeType.Wiese),
                tile_group=tt.TileGroup.Auftrag, task_type=tt.TaskType.Sakura),
    74: TileDef((tt.EdgeType.Wiese, tt.EdgeType.Sakura, tt.EdgeType.Sakura,
                tt.EdgeType.Sakura, tt.EdgeType.Wiese, tt.EdgeType.Reis),
                tile_group=tt.TileGroup.Auftrag, task_type=tt.TaskType.Sakura),
    75: TileDef((tt.EdgeType.Dorf, tt.EdgeType.Wiese, tt.EdgeType.Sakura,
                tt.EdgeType.Sakura, tt.EdgeType.Wiese, tt.EdgeType.Dorf),
                tile_group=tt.TileGroup.Auftrag, task_type=tt.TaskType.Sakura),
    76: TileDef((tt.EdgeType.Fluss, tt.EdgeType.Fluss, tt.EdgeType.Sakura,
                tt.EdgeType.Sakura, tt.EdgeType.Sakura, tt.EdgeType.Sakura),
                tile_group=tt.TileGroup.Auftrag, task_type=tt.TaskType.Sakura),
    77: TileDef((tt.EdgeType.Wiese, tt.EdgeType.Reis, tt.EdgeType.Reis,
                tt.EdgeType.Wiese, tt.EdgeType.Sakura, tt.EdgeType.Sakura),
                tile_group=tt.TileGroup.Auftrag, task_type=tt.TaskType.Reis),
    78: TileDef((tt.EdgeType.Reis, tt.EdgeType.Reis, tt.EdgeType.Reis,
                tt.EdgeType.Reis, tt.EdgeType.Reis, tt.EdgeType.Reis),
                tile_group=tt.TileGroup.Auftrag, task_type=tt.TaskType.Reis),
    79: TileDef((tt.EdgeType.Reis, tt.EdgeType.Wiese, tt.EdgeType.Wiese,
                tt.EdgeType.Reis, tt.EdgeType.Wiese, tt.EdgeType.Wiese),
                tile_group=tt.TileGroup.Auftrag, task_type=tt.TaskType.Reis),
    80: TileDef((tt.EdgeType.Reis, tt.EdgeType.Wiese, tt.EdgeType.Wiese,
                tt.EdgeType.Wiese, tt.EdgeType.Wiese, tt.EdgeType.Reis),
                tile_group=tt.TileGroup.Auftrag, task_type=tt.TaskType.Reis),
    81: TileDef((tt.EdgeType.Dorf, tt.EdgeType.Wiese, tt.EdgeType.Reis,
                tt.EdgeType.Reis, tt.EdgeType.Reis, tt.EdgeType.Wiese),
                tile_group=tt.TileGroup.Auftrag, task_type=tt.TaskType.Reis),
    82: TileDef((tt.EdgeType.Fluss, tt.EdgeType.Reis, tt.EdgeType.Reis,
                tt.EdgeType.Reis, tt.EdgeType.Reis, tt.EdgeType.Fluss),
                tile_group=tt.TileGroup.Auftrag, task_type=tt.TaskType.Reis),
    83: TileDef((tt.EdgeType.Dorf, tt.EdgeType.Dorf, tt.EdgeType.Wiese,
                tt.EdgeType.Sakura, tt.EdgeType.Wiese, tt.EdgeType.Dorf),
                tile_group=tt.TileGroup.Auftrag, task_type=tt.TaskType.Dorf),
    84: TileDef((tt.EdgeType.Dorf, tt.EdgeType.Wiese, tt.EdgeType.Reis,
                tt.EdgeType.Reis, tt.EdgeType.Wiese, tt.EdgeType.Dorf),
                tile_group=tt.TileGroup.Auftrag, task_type=tt.TaskType.Dorf),
    85: TileDef((tt.EdgeType.Dorf, tt.EdgeType.Dorf, tt.EdgeType.Dorf,
                tt.EdgeType.Dorf, tt.EdgeType.Dorf, tt.EdgeType.Dorf),
                tile_group=tt.TileGroup.Auftrag, task_type=tt.TaskType.Dorf),
    86: TileDef((tt.EdgeType.Wiese, tt.EdgeType.Wiese, tt.EdgeType.Dorf,
                tt.EdgeType.Wiese, tt.EdgeType.Wiese, tt.EdgeType.Dorf),
                tile_group=tt.TileGroup.Auftrag, task_type=tt.TaskType.Dorf),
    87: TileDef((tt.EdgeType.Dorf, tt.EdgeType.Dorf, tt.EdgeType.Wiese,
                tt.EdgeType.Wiese, tt.EdgeType.Wiese, tt.EdgeType.Wiese),
                tile_group=tt.TileGroup.Auftrag, task_type=tt.TaskType.Dorf),
    88: TileDef((tt.EdgeType.Dorf, tt.EdgeType.Dorf, tt.EdgeType.Strasse,
                tt.EdgeType.Strasse, tt.EdgeType.Dorf, tt.EdgeType.Dorf),
                tile_group=tt.TileGroup.Auftrag, task_type=tt.TaskType.Dorf),
    89: TileDef((tt.EdgeType.Strasse, tt.EdgeType.Strasse, tt.EdgeType.Wiese,
                tt.EdgeType.Sakura, tt.EdgeType.Sakura, tt.EdgeType.Wiese),
                tile_group=tt.TileGroup.Auftrag, task_type=tt.TaskType.Strasse),
    90: TileDef((tt.EdgeType.Strasse, tt.EdgeType.Strasse, tt.EdgeType.Wiese,
                tt.EdgeType.Reis, tt.EdgeType.Reis, tt.EdgeType.Wiese),
                tile_group=tt.TileGroup.Auftrag, task_type=tt.TaskType.Strasse),
    91: TileDef((tt.EdgeType.Strasse, tt.EdgeType.Wiese, tt.EdgeType.Wiese,
                tt.EdgeType.Strasse, tt.EdgeType.Wiese, tt.EdgeType.Wiese),
                tile_group=tt.TileGroup.Auftrag, task_type=tt.TaskType.Strasse),
    92: TileDef((tt.EdgeType.Strasse, tt.EdgeType.Wiese, tt.EdgeType.Strasse,
                tt.EdgeType.Wiese, tt.EdgeType.Wiese, tt.EdgeType.Wiese),
                tile_group=tt.TileGroup.Auftrag, task_type=tt.TaskType.Strasse),
    93: TileDef((tt.EdgeType.Strasse, tt.EdgeType.Wiese, tt.EdgeType.Fluss,
                tt.EdgeType.Strasse, tt.EdgeType.Fluss, tt.EdgeType.Wiese),
                tile_group=tt.TileGroup.Auftrag, task_type=tt.TaskType.Strasse),
    94: TileDef((tt.EdgeType.Fluss, tt.EdgeType.Wiese, tt.EdgeType.Fluss,
                tt.EdgeType.Strasse, tt.EdgeType.Wiese, tt.EdgeType.Strasse),
                tile_group=tt.TileGroup.Auftrag, task_type=tt.TaskType.Strasse),
    95: TileDef((tt.EdgeType.Fluss, tt.EdgeType.Wiese, tt.EdgeType.Fluss,
                tt.EdgeType.Dorf, tt.EdgeType.Dorf, tt.EdgeType.Dorf),
                tile_group=tt.TileGroup.Auftrag, task_type=tt.TaskType.Fluss),
    96: TileDef((tt.EdgeType.Fluss, tt.EdgeType.Fluss, tt.EdgeType.Wiese,
                tt.EdgeType.Dorf, tt.EdgeType.Dorf, tt.EdgeType.Wiese),
                tile_group=tt.TileGroup.Auftrag, task_type=tt.TaskType.Fluss),
    97: TileDef((tt.EdgeType.Fluss, tt.EdgeType.Wiese, tt.EdgeType.Strasse,
                tt.EdgeType.Fluss, tt.EdgeType.Strasse, tt.EdgeType.Wiese),
                tile_group=tt.TileGroup.Auftrag, task_type=tt.TaskType.Fluss),
    98: TileDef((tt.EdgeType.Fluss, tt.EdgeType.Fluss, tt.EdgeType.Wiese,
                tt.EdgeType.Strasse, tt.EdgeType.Strasse, tt.EdgeType.Wiese),
                tile_group=tt.TileGroup.Auftrag, task_type=tt.TaskType.Fluss),
    99: TileDef((tt.EdgeType.Fluss, tt.EdgeType.Wiese, tt.EdgeType.Wiese,
                tt.EdgeType.Fluss, tt.EdgeType.Wiese, tt.EdgeType.Wiese),
                tile_group=tt.TileGroup.Auftrag, task_type=tt.TaskType.Fluss),
    100: TileDef((tt.EdgeType.Fluss, tt.EdgeType.Wiese, tt.EdgeType.Fluss,
                tt.EdgeType.Wiese, tt.EdgeType.Wiese, tt.EdgeType.Wiese),
                tile_group=tt.TileGroup.Auftrag, task_type=tt.TaskType.Fluss),
    101: TileDef((tt.EdgeType.Strasse, tt.EdgeType.Wiese, tt.EdgeType.Sakura,
                tt.EdgeType.Sakura, tt.EdgeType.Sakura, tt.EdgeType.Wiese),
                tile_group=tt.TileGroup.Auftrag, task_type=tt.TaskType.Rundum),
    102: TileDef((tt.EdgeType.Strasse, tt.EdgeType.Wiese, tt.EdgeType.Reis,
                tt.EdgeType.Reis, tt.EdgeType.Reis, tt.EdgeType.Wiese),
                tile_group=tt.TileGroup.Auftrag, task_type=tt.TaskType.Rundum),
    103: TileDef((tt.EdgeType.Strasse, tt.EdgeType.Wiese, tt.EdgeType.Dorf,
                tt.EdgeType.Dorf, tt.EdgeType.Dorf, tt.EdgeType.Wiese),
                tile_group=tt.TileGroup.Auftrag, task_type=tt.TaskType.Rundum),
    104: TileDef((tt.EdgeType.Fluss, tt.EdgeType.Wiese, tt.EdgeType.Sakura,
                tt.EdgeType.Sakura, tt.EdgeType.Sakura, tt.EdgeType.Wiese),
                tile_group=tt.TileGroup.Auftrag, task_type=tt.TaskType.Rundum),
    105: TileDef((tt.EdgeType.Fluss, tt.EdgeType.Wiese, tt.EdgeType.Reis,
                tt.EdgeType.Reis, tt.EdgeType.Reis, tt.EdgeType.Wiese),
                tile_group=tt.TileGroup.Auftrag, task_type=tt.TaskType.Rundum),
    106: TileDef((tt.EdgeType.Fluss, tt.EdgeType.Wiese, tt.EdgeType.Dorf,
                tt.EdgeType.Dorf, tt.EdgeType.Dorf, tt.EdgeType.Wiese),
                tile_group=tt.TileGroup.Auftrag, task_type=tt.TaskType.Rundum),
    # 107: TileDef((tt.EdgeType.Sakura, tt.EdgeType.Wiese, tt.EdgeType.Reis,
    #             tt.EdgeType.Wiese, tt.EdgeType.Heisse_Quellen, tt.EdgeType.Wiese),
    #             tile_group=tt.TileGroup.Auftrag, task_type=tt.TaskType.SakuraReis),
    # 108: TileDef((tt.EdgeType.Dorf, tt.EdgeType.Wiese, tt.EdgeType.Sakura,
    #             tt.EdgeType.Wiese, tt.EdgeType.Heisse_Quellen, tt.EdgeType.Wiese),
    #             tile_group=tt.TileGroup.Auftrag, task_type=tt.TaskType.SakuraDorf),
    # 109: TileDef((tt.EdgeType.Reis, tt.EdgeType.Wiese, tt.EdgeType.Dorf,
    #             tt.EdgeType.Wiese, tt.EdgeType.Heisse_Quellen, tt.EdgeType.Wiese),
    #             tile_group=tt.TileGroup.Auftrag, task_type=tt.TaskType.ReisDorf)
}

# Vorberechnung von Sets von rotierten Tiles

# alle Tiles
ROT_EDGES = {
    tid: [rotate_edges(t.edges, r) for r in range(6)]
    for tid, t in TILES.items()
}

# alle Tiles die entweder Strasse oder Fluss enthalten (benötigt für Staudamm / Sackgasse)
ROAD_EDGE_INDICES_BY_TILE_ROT = dict()
RIVER_EDGE_INDICES_BY_TILE_ROT = dict()

for tile_id, rots in ROT_EDGES.items():
    for rot, edges in enumerate(rots):
        road = tuple(i for i, e in enumerate(edges) if e == tt.EdgeType.Strasse)
        river = tuple(i for i, e in enumerate(edges) if e == tt.EdgeType.Fluss)

        if road:
            ROAD_EDGE_INDICES_BY_TILE_ROT[(tile_id, rot)] = road
        if river:
            RIVER_EDGE_INDICES_BY_TILE_ROT[(tile_id, rot)] = river


from collections import defaultdict


def report_rot_edge_duplicates(rot_edge: dict):
    # 1) Alle Rotationen in eine Map: edges -> [(tid, ridx), ...]
    rot_map = defaultdict(list)
    for tid, rots in rot_edge.items():
        for ridx, edges in enumerate(rots):
            rot_map[edges].append((tid, ridx))

    # Nur Einträge, die mehr als einmal vorkommen
    duplicates = {edges: infos for edges, infos in rot_map.items() if len(infos) > 1}

    # 2) Auswerten: innerhalb eines Tiles vs zwischen Tiles
    within_tile = []
    across_tiles = []

    for edges, infos in duplicates.items():
        tids = [tid for tid, _ in infos]
        if len(set(tids)) == 1:
            within_tile.append((edges, infos))  # Symmetrie innerhalb eines Tiles
        else:
            across_tiles.append((edges, infos))  # Theoretische Duplikate zwischen Tiles

    within_tile_ids = sorted({
        tid
        for _, infos in within_tile
        for tid, _ in infos
    })

    across_tile_ids = sorted({
        tid
        for _, infos in across_tiles
        for tid, _ in infos
    })

    # 3) Tile-Äquivalenz (rotationsunabhängig): canon = min(rotations)
    canon_map = defaultdict(list)
    for tid, rots in rot_edge.items():
        canon = min(rots)
        canon_map[canon].append(tid)

    tile_equiv = {canon: tids for canon, tids in canon_map.items() if len(tids) > 1}

    # 4) Report drucken
    print("=== ROT_EDGE Duplicate Report ===")
    print(f"Total unique rotation-edge patterns: {len(rot_map)}")
    print(f"Total duplicate patterns (appear >1x): {len(duplicates)}")
    print(f"  - duplicates within same tile (symmetry): {len(within_tile)}")
    print(f"  - duplicates across different tiles:      {len(across_tiles)}")
    print()
    print(f"Tile equivalence groups (same up to rotation): {len(tile_equiv)}")

    # Optional: Details
    if across_tiles:
        print("\n--- Details: duplicates across different tiles ---")
        for edges, infos in sorted(across_tiles, key=lambda x: -len(x[1])):
            print(f"Pattern occurs {len(infos)}x: {edges}")
            for tid, ridx in infos:
                print(f"  Tile {tid}, rot {ridx}")
            print()

    if tile_equiv:
        print("\n--- Details: tile equivalence groups (rotation-invariant) ---")
        for canon, tids in sorted(tile_equiv.items(), key=lambda x: -len(x[1])):
            print(f"Tiles {tids} share same canonical rotation: {canon}")

    print(f"Tiles with internal symmetry duplicates: {within_tile_ids}")
    print(f"Tiles involved in cross-tile duplicates: {across_tile_ids}")
    print()

    print(f"Tile equivalence groups (same up to rotation): {len(tile_equiv)}")
