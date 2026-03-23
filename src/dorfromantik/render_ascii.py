from typing import Dict, Tuple
from dorfromantik.state import State


def render_ascii(state: State) -> None:
    if not state.board:
        print("(empty board)")
        return

    positions = list(state.board.keys())
    qs = [p[0] for p in positions]
    rs = [p[1] for p in positions]

    min_q, max_q = min(qs), max(qs)
    min_r, max_r = min(rs), max(rs)

    print("\nBOARD:")

    for r in range(min_r, max_r + 1):
        line = []

        # leichte Einrückung für Hex-Optik
        indent = " " * (max_r - r)
        line.append(indent)

        for q in range(min_q, max_q + 1):
            if (q, r) in state.board:
                tile_id = state.board[(q, r)].tile_id
                line.append(f"{tile_id:2d}")
            else:
                line.append(" .")

        print(" ".join(line))

    print()
