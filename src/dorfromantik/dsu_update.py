from __future__ import annotations

from typing import Dict

from . import tile_types as tt
from dorfromantik.dsu import DSU
from dorfromantik.state import State, PlacedTile
from dorfromantik.tiles import ROT_EDGES
from .tiles import TILES

TRACKED_TYPES = (
    tt.EdgeType.Sakura,
    tt.EdgeType.Reis,
    tt.EdgeType.Dorf,
    tt.EdgeType.Strasse,
    tt.EdgeType.Fluss,
    tt.EdgeType.Heisse_Quellen,
    tt.EdgeType.Vulkan,
    tt.EdgeType.Wolken
)
TRACKED_TYPES_SET = frozenset(TRACKED_TYPES)


def update_all_dsus_after_place(state: State, pos: tt.Pos) -> None:
    """
    Nach state.place_tile(pos, tile_id, rot) aufrufen.
    Aktualisiert für alle 7 Typen:
        - DSU Komponenten
        - offene Kanten (open_edges) pro Komponente
    """
    placed = state.board[pos]
    edges = placed.edges

    for et in TRACKED_TYPES_SET.intersection(edges):
        update_one_dsu_after_place(state, pos, et, placed=placed, edges=edges)


def update_neighbor_dsus_after_place(state: State, pos: tt.Pos) -> None:
    for side in range(6):
        npos = tt.neighbor(pos, side)
        if npos not in state.board:
            continue

        opp = tt.opposite_edge(side)
        nplaced = state.board[npos]
        nedges = nplaced.edges

        neighbor_type = nedges[opp]
        if neighbor_type in TRACKED_TYPES_SET:
            update_one_dsu_after_place(state, npos, neighbor_type, placed=nplaced, edges=nedges)


def update_one_dsu_after_place(
        state: State,
        pos: tt.Pos,
        et: tt.EdgeType,
        placed: PlacedTile | None = None,
        edges: tuple[tt.EdgeType, ...] | None = None,
) -> None:
    """
    Aktualisiert genau eine DSU für einen Typ et an Position pos.

    Logik:
    - Hat das Tile den Typ et nicht -> nichts tun
    - Kante ohne Nachbar -> offen
    - Kante mit Nachbar gleichen Typs -> union + Kante schließen
    - Kante mit Nachbar anderen Typs:
        * bei Kontinuitätstypen -> Fehler
        * bei Sakura/Reis/Dorf -> Kante ist geschlossen
    """
    d: Dict[tt.EdgeType, DSU] = state.feature_dsu  # type: ignore[attr-defined]
    dsu = d[et]

    if placed is None:
        placed = state.board[pos]
    if edges is None:
        edges = placed.edges

    if et not in edges:
        return

    dsu.add(pos)

    for side, edge_type in enumerate(edges):
        if edge_type != et:
            continue

        npos = tt.neighbor(pos, side)
        opp = tt.opposite_edge(side)

        # Diese HalfEdge immer zuerst zurücksetzen,
        # damit die Funktion idempotent bleibt.
        dsu.open_edges[dsu.find(pos)].discard((pos, side))
        dsu.refresh_closed(pos)

        # Kein Nachbar -> offene Kante
        if npos not in state.board:
            dsu.add_open_edge(pos, side)
            continue

        nplaced = state.board[npos]
        nedges = nplaced.edges

        # Gleicher Typ -> verbinden und Innenkante schließen
        if nedges[opp] == et:
            dsu.close_between(pos, side, npos, opp)
            continue

        # Anderer Typ am Nachbarn
        if et in tt.CONTINUITY_TYPES:
            raise AssertionError(
                f"Kontinuitätsverletzung: {et.name} bei {pos}[{side}] "
                f"grenzt an {nedges[opp].name} bei {npos}[{opp}]"
            )

        # Sakura/Reis/Dorf:
        # Nachbar vorhanden => Kante ist nicht offen, also nichts mehr tun.

    # Fahne des neu gelegten Tiles in die passende DSU eintragen
    tile_flag_type = TILES[placed.tile_id].flag_type
    if tile_flag_type == et:
        dsu.add_flag(pos, tile_flag_type)

    dsu.refresh_closed(pos)
