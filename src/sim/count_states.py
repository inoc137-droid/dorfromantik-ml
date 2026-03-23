from __future__ import annotations
from dataclasses import replace
from typing import Tuple, Set, Dict

from dorfromantik.state import State, PlacedTile
from dorfromantik.rules import legal_actions

# 7 feste Tiles (in genau dieser Zugreihenfolge!)
FIXED_TILES: Tuple[int, ...] = (0, 1, 2, 3, 4)

def state_key(s: State) -> Tuple[Tuple[int, int, int, int], ...]:
    """
    Eindeutige, hashbare Repräsentation des Boards.
    Zählt Zustände als 'genau diese Positionen + tile_id + rotation'.
    """
    items = []
    for (q, r), pt in s.board.items():
        items.append((q, r, pt.tile_id, pt.rot))
    items.sort()
    return tuple(items)

def copy_and_place(s: State, pos, tile_id: int, rot: int) -> State:
    s2 = State(board=dict(s.board), current_tile=s.current_tile)
    s2.place_tile(pos, tile_id, rot)
    return s2

def main():
    # pro Tiefe: Menge an eindeutigen Zuständen (Board-Konfigurationen)
    states_at_depth: Dict[int, Set[Tuple[Tuple[int,int,int,int], ...]]] = {0: {state_key(State())}}

    for depth, tile_id in enumerate(FIXED_TILES, start=1):
        prev = states_at_depth[depth - 1]
        cur: Set[Tuple[Tuple[int,int,int,int], ...]] = set()

        # Wir iterieren über Keys -> bauen State wieder auf.
        # Für depth<=7 ist das schnell genug.
        for key in prev:
            s = State()
            for q, r, tid, rot in key:
                s.place_tile((q, r), tid, rot)

            for (pos, rot) in legal_actions(s, tile_id):
                s2 = copy_and_place(s, pos, tile_id, rot)
                cur.add(state_key(s2))

        states_at_depth[depth] = cur
        print(f"Depth {depth}: {len(cur)} states")

    print(f"FINAL (after {len(FIXED_TILES)}): {len(states_at_depth[len(FIXED_TILES)])}")

if __name__ == "__main__":
    main()