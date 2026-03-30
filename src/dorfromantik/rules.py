from __future__ import annotations
from typing import List, Tuple, Set
from . import tile_types as tt
from .tiles import ROT_EDGES
from .state import State

def frontier_positions(state: State) -> Set[tt.Pos]:
    """
    Alle in Frage kommenden Positionen zum Legen eines neuen Plättchens
        =    Menge aller Nachbarpositionen aller bereits gelegten Plättchen.

    :param state: Aktueller State des Spiels.
    :return: Liste aller Nachbarn der bereits platzierten Plättchen.
    """
    return state.frontier


def is_legal_placement(
        state: State,
        pos: tt.Pos,
        tile_id: int,
        rot: int,
        edge_overrides: dict[int, tt.EdgeType] | None = None
) -> bool:
    """
    Zu gegebenem State, wird geprüft, ob das Plättchen mit tile_id an der Stelle pos mit Rotation
    rot gelegt werden kann. Berücksichtigt werden nur Kontinuitätsregeln durch Strasse, Fluss,
    Heiße Quellen, Vulkan.

    :param state: Aktueller State des Spiels.
    :param pos: Hex-Koordinaten der zu prüfenden Stelle
    :param tile_id: Tile-Nummer des zu prüfenden Plättchens
    :param rot:  Rotation des zu prüfenden Plättchens
    :param edge_overrides: Dictionary mit Kanten-Replacements (0..5, tt.EdgeType)
    :return: True/False, ob das Plättchen gesetzt werden kann.
    """
    edges = list(ROT_EDGES[tile_id][rot])

    # zunächst Overrides anwenden
    if edge_overrides:
        for idx, new_type in edge_overrides.items():
            edges[idx] = new_type

    has_neighbor = False

    for edge_idx in range(6):
        npos = tt.neighbor(pos, edge_idx)

        if npos in state.board:
            has_neighbor = True

            neighbor_tile = state.board[npos]
            neighbor_edges = State.effective_edges(neighbor_tile)

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


def legal_actions(state: State, tile_id) -> List[Tuple[tt.Pos, int]]:
    """
    Gibt zum State alle möglichen (pos, rot) an, durch die das aktuelle Tile gelegt werden kann.

    :param state: Aktuelles Frontier wird benötigt als Liste mit allen zum State verfügbaren Positionen pos.
    :param tile_id: Plättchen, welches in Frontier gelegt werden kann.
    :return: Eine Liste aller (pos, rot) an denen das Plättchen mit tile_id gelegt werden kann.
    """
    actions = []
    frontier = sorted(frontier_positions(state))
    for pos in frontier:
        for rot in range(6):
            if is_legal_placement(state, pos, tile_id, rot):
                actions.append((pos, rot))
    return actions
