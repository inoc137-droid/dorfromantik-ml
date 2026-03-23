from __future__ import annotations

from typing import Set, Tuple

import dorfromantik.tile_types as tt
from dorfromantik.tiles import ROT_EDGES


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


def naive_open_edges(state, et: tt.EdgeType) -> Set[Tuple[tt.Pos, int]]:
    """
    Naive Referenz-Implementierung für offene Kanten.

    Regeln:
    - Kontinuitätstypen: offen, wenn kein Nachbar da ist
      oder (eigentlich illegal) Gegenkante nicht derselbe Typ ist.
    - Sakura/Reis/Dorf: offen nur, wenn kein Nachbarplättchen existiert.
      Sobald irgendein Nachbarplättchen anliegt, ist die Kante nicht mehr offen.
    """
    open_set: Set[Tuple[tt.Pos, int]] = set()

    for pos, placed in state.board.items():
        edges = ROT_EDGES[placed.tile_id][placed.rot]

        for side in range(6):
            if edges[side] != et:
                continue

            npos = tt.neighbor(pos, side)
            opp = tt.opposite_edge(side)

            # Kein Nachbarplättchen -> offen
            if npos not in state.board:
                open_set.add((pos, side))
                continue

            nplaced = state.board[npos]
            nedges = ROT_EDGES[nplaced.tile_id][nplaced.rot]

            if et in tt.CONTINUITY_TYPES:
                # anderer Typ wäre eigentlich illegal, gilt hier aber als "offen"
                if nedges[opp] != et:
                    open_set.add((pos, side))
            else:
                # Sakura/Reis/Dorf:
                # Nachbarplättchen vorhanden => nicht offen
                pass

    return open_set


def check_dsu_consistency(state, verbose: bool = False) -> None:
    """
    Prüft:
    - DSU vorhanden
    - open_edges der DSU stimmen mit naive_open_edges überein
    - closed-Flag stimmt zu open_edges
    """
    if not hasattr(state, "feature_dsu"):
        raise AssertionError("state.feature_dsu fehlt")

    dsu_map = state.feature_dsu

    for et in TRACKED_TYPES:
        dsu = dsu_map.get(et)
        if dsu is None:
            continue

        dsu_open = set().union(*dsu.open_edges.values()) if dsu.open_edges else set()
        naive = naive_open_edges(state, et)

        if dsu_open != naive:
            missing = naive - dsu_open
            extra = dsu_open - naive

            if verbose:
                print(f"[DSU][MISMATCH] {et.name}: DSU_open != naive_open")
                if missing:
                    print("  missing (should be open):", sorted(missing))
                if extra:
                    print("  extra (should be closed):", sorted(extra))

            raise AssertionError(f"Open-edge mismatch for {et.name}")

        # closed-Flags prüfen
        for root, members in dsu.members.items():
            expected_closed = len(dsu.open_edges.get(root, set())) == 0
            actual_closed = dsu.closed.get(root, False)

            if expected_closed != actual_closed:
                if verbose:
                    print(f"[DSU][MISMATCH] {et.name}: closed-Flag falsch")
                    print(f"  root          : {root}")
                    print(f"  members       : {sorted(members)}")
                    print(f"  open_edges    : {sorted(dsu.open_edges.get(root, set()))}")
                    print(f"  expected      : {expected_closed}")
                    print(f"  actual        : {actual_closed}")

                raise AssertionError(f"Closed-flag mismatch for {et.name}, root={root}")


def debug_print_dsus(state) -> None:
    if not hasattr(state, "feature_dsu"):
        print("  [DSU] state.feature_dsu fehlt")
        return

    dsu_map = state.feature_dsu

    print("  [DSU] Summary:")
    for et in TRACKED_TYPES:
        dsu = dsu_map.get(et)
        if dsu is None:
            print(f"    - {et.name}: (no dsu)")
            continue

        n_comp = len(dsu.members)
        open_total = sum(len(s) for s in dsu.open_edges.values())
        print(
            f"    - {et.name:15s} comps={n_comp:3d} "
            f"max={dsu.max_size:3d} open_total={open_total:3d}"
        )

        if n_comp > 0:
            print(f"      Komponenten {et.name}:")
            for root in sorted(dsu.members.keys()):
                members = sorted(dsu.members[root])
                open_edges = sorted(dsu.open_edges.get(root, set()))
                closed = dsu.closed.get(root, False)

                print(
                    f"        root={root} "
                    f"size={dsu.size[root]:2d} "
                    f"closed={closed}"
                )
                print(f"          members   : {members}")
                print(f"          open_edges: {open_edges}")