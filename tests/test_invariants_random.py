# tests/test_invariants_random.py
#
# Property-Tests über viele Episoden:
# (2) Kontinuität für Strasse & Fluss
# (3) Frontier-Korrektheit (Start + allgemeine Definition)

from __future__ import annotations

import random
from typing import Set, Tuple

import dorfromantik.tile_types as tt
from dorfromantik.tiles import TILES, rotate_edges
from dorfromantik.env import Env
from dorfromantik.rules import frontier_positions


# --- Konfiguration ---
N_EPISODES = 1000          # auf 10000 erhöhen, wenn es schnell genug läuft
MAX_STEPS_PER_EPISODE = 999  # effektiv begrenzt durch bag length


def _edges(tile_id: int, rot: int):
    return rotate_edges(TILES[tile_id].edges, rot)


def assert_continuity_road_river(state) -> None:
    """
    Für jedes benachbarte Tile-Paar:
    Wenn eine der beiden Kanten Strasse oder Fluss ist, müssen beide exakt gleich sein.
    """
    for pos, placed in state.board.items():
        my_edges = _edges(placed.tile_id, placed.rot)

        for e_idx in range(6):
            npos = tt.neighbor(pos, e_idx)
            if npos not in state.board:
                continue

            other = state.board[npos]
            other_edges = _edges(other.tile_id, other.rot)

            my_e = my_edges[e_idx]
            other_e = other_edges[tt.opposite_edge(e_idx)]

            if (my_e in (tt.EdgeType.Strasse, tt.EdgeType.Fluss)) or (
                other_e in (tt.EdgeType.Strasse, tt.EdgeType.Fluss)
            ):
                assert my_e == other_e, (
                    f"Continuity violation at {pos} edge {e_idx} vs neighbor {npos}: "
                    f"{my_e} != {other_e}"
                )


def expected_frontier(state) -> Set[Tuple[int, int]]:
    """
    Definition:
    - Wenn board leer: {(0,0)}
    - Sonst: alle leeren Nachbarfelder (6-neighborhood) von belegten Feldern
    """
    if not state.board:
        return {(0, 0)}

    occ = set(state.board.keys())
    fr: Set[Tuple[int, int]] = set()
    for pos in occ:
        for e in range(6):
            npos = tt.neighbor(pos, e)
            if npos not in occ:
                fr.add(npos)
    return fr


def assert_frontier_correct(state) -> None:
    fr1 = frontier_positions(state)
    fr2 = expected_frontier(state)
    assert fr1 == fr2

    # Zusätzlich: Frontier enthält nie belegte Felder, und ist (außer Start) adjacent zu mindestens einem belegten
    occ = set(state.board.keys())
    assert fr1.isdisjoint(occ)

    if state.board:
        for p in fr1:
            assert any(tt.neighbor(p, e) in occ for e in range(6))


# --- Tests ---
def test_frontier_start_state():
    env = Env(seed=0)
    s = env.reset(seed=0)
    # Reset zieht schon ein current_tile, board ist aber leer.
    assert_frontier_correct(s)
    assert frontier_positions(s) == {(0, 0)}


def test_random_episodes_frontier_and_continuity():
    # feste Bag-Form, damit Laufzeit & Variabilität kontrollierbar bleibt
    # (Anpassen falls du andere Tile-IDs hast)
    bag = [0, 1, 2, 3, 4, 5, 6] * 5  # 35 steps max
    env = Env(bag=bag, seed=123)

    for episode_seed in range(N_EPISODES):
        if episode_seed % 10 == 0:
            print(f"Episode {episode_seed}/{N_EPISODES}")
        s = env.reset(seed=episode_seed)

        # Invarianten im Startzustand
        assert_frontier_correct(s)
        assert_continuity_road_river(s)

        steps = 0
        rng = random.Random(episode_seed)

        while steps < MAX_STEPS_PER_EPISODE:
            acts = env.legal_actions(s)
            if not acts:
                break

            # Random policy
            a = acts[rng.randrange(len(acts))]
            s, r, done, info = env.step(s, a)

            # Invarianten nach jedem Schritt
            assert_frontier_correct(s)
            assert_continuity_road_river(s)

            steps += 1
            if done:
                break