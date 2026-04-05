from dataclasses import dataclass
from typing import Optional
import dorfromantik.tile_types as tt


@dataclass(frozen=True, slots=True)
class Action:
    # "place_tile", "store_tile", "choose_source" (,"adjust_task_goal", "choose_from_3_task_tiles","place_structure")
    kind: str
    tile_id: Optional[int] = None
    pos: Optional[tt.Pos] = None
    rot: Optional[int] = None
    # "storehouse", "kontor", "plus_one", "minus_one", "draw_2_more_tasks", "bridge", "gate", "temple"
    choice: Optional[str] = None
    # wird genutzt für "place_structure", "bridge", (1,0)
    target_pos: Optional[tt.Pos] = None
    #  choose task_tile 0, 1, 2
    value: Optional[int] = None

    # Speichert veränderte Kanten durch Sackgasse, Staudamm oder Wolken
    edge_override_edge: Optional[int] = None
    edge_override_from: Optional[tt.EdgeType] = None
    edge_override_to: Optional[tt.EdgeType] = None