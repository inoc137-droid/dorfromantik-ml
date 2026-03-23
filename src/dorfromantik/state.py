from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Optional, Set, List
from . import tile_types as tt
from . import tasks as tasks
from dorfromantik.dsu import DSU
from .tiles import ROT_EDGES


@dataclass
class PlacedTile:
    tile_id: int
    rot: int
    edge_overrides: dict[int, tt.EdgeType] = field(default_factory=dict)


@dataclass
class State:
    board: Dict[tt.Pos, PlacedTile] = field(default_factory=dict)
    current_tile: Optional[int] = None
    frontier: Set[tt.Pos] = field(default_factory=lambda: {(0, 0)})

    #  "place_tile", "choose_next_tile_source", "choose_task_tile", "choose_special_effect", "place_structure"
    phase: str = "place_tile"

    feature_dsu: Dict[tt.EdgeType, DSU] = field(default_factory=lambda: {
        tt.EdgeType.Sakura: DSU(),
        tt.EdgeType.Reis: DSU(),
        tt.EdgeType.Dorf: DSU(),
        tt.EdgeType.Strasse: DSU(),
        tt.EdgeType.Fluss: DSU(),
        tt.EdgeType.Heisse_Quellen: DSU(),
        tt.EdgeType.Vulkan: DSU(),
        tt.EdgeType.Wolken: DSU()
    })

    main_stack: List[int] = field(default_factory=list)
    task_stack: List[int] = field(default_factory=list)
    temple_tiles: List[int] = field(default_factory=list)
    temple_hidden_stack: List[int] = field(default_factory=list)

    task_marker_stack: list[tasks.TaskMarker] = field(default_factory=list)
    completed_task_markers: list[tasks.TaskMarker] = field(default_factory=list)
    active_tasks: list[tasks.ActiveTask] = field(default_factory=list)
    failed_task_markers: list[tasks.TaskMarker] = field(default_factory=list)

    storehouse_tile: Optional[int] = None
    kontor_tile: Optional[int] = None

    sackgasse_available: bool = True
    staudamm_available: bool = True

    def is_empty(self) -> bool:
        return len(self.board) == 0

    def place_tile(self, pos: tt.Pos, tile_id: int, rot: int):
        self.board[pos] = PlacedTile(tile_id, rot)

        # pos ist belegt -> entfernen
        self.frontier.discard(pos)

        # Nachbarn hinzufügen
        for edge in range(6):
            npos = tt.neighbor(pos, edge)
            if npos not in self.board:
                self.frontier.add(npos)

    def occupied_positions(self) -> Set[tt.Pos]:
        return set(self.board.keys())

    def effective_edges(placed: PlacedTile) -> tuple[tt.EdgeType, ...]:
        edges = list(ROT_EDGES[placed.tile_id][placed.rot])
        for edge_idx, edge_type in placed.edge_overrides.items():
            edges[edge_idx] = edge_type
        return tuple(edges)
