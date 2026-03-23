from __future__ import annotations
from typing import List, Tuple, Set
from . import tile_types as tt
from .tiles import TILES, ROT_EDGES
from .state import State

def frontier_positions(state: State) -> Set[tt.Pos]:
    return state.frontier


def is_legal_placement(state:State, pos: tt.Pos, tile_id: int, rot: int) -> bool:
    tile = TILES[tile_id]
    edges = ROT_EDGES[tile_id][rot]

    has_neighbor = False

    for edge_idx in range(6):
        npos = tt.neighbor(pos, edge_idx)

        if npos in state.board:
            has_neighbor = True

            neighbor_tile = state.board[npos]
            neighbor_edges = ROT_EDGES[neighbor_tile.tile_id][neighbor_tile.rot]

            my_edge = edges[edge_idx]
            other_edge = neighbor_edges[tt.opposite_edge(edge_idx)]

            # Regeln Kontinuität für Fluss, Strasse, Heiße Quellen, Vulkan
            if my_edge in tt.CONTINUITY_TYPES or other_edge in tt.CONTINUITY_TYPES:
                if my_edge != other_edge:
                    return False

    # darf nicht isoliert liegen (außer erstes Tile)
    if not has_neighbor and not state.is_empty():
        return False

    return True

def legal_actions(state: State, tile_id) -> List[tt.Action]:
    actions = []
    frontier = sorted(frontier_positions(state))
    for pos in frontier:
        for rot in range(6):
            if is_legal_placement(state, pos, tile_id, rot):
                actions.append((pos, rot))
    return actions
