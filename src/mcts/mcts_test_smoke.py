from __future__ import annotations
import time

from dorfromantik.env import Env
from dorfromantik.action import Action
from dorfromantik.scoring import score_rules
from mcts.core import MCTS
from mcts.dorfromantik_adapter import DorfromantikAdapter



def format_action(a: Action | None) -> str:
    if a is None:
        return "None"

    parts = [f"kind={a.kind}"]

    if a.tile_id is not None:
        parts.append(f"tile_id={a.tile_id}")
    if a.pos is not None:
        parts.append(f"pos={a.pos}")
    if a.rot is not None:
        parts.append(f"rot={a.rot}")
    if a.choice is not None:
        parts.append(f"choice={a.choice}")
    if a.edge_override_edge is not None:
        parts.append(
            f"override=edge {a.edge_override_edge}: "
            f"{a.edge_override_from} -> {a.edge_override_to}"
        )

    return ", ".join(parts)


def print_history(history: list[tuple[str, int]]) -> None:
    print("\n" + "=" * 90)
    print("VERLAUF")
    print("=" * 90)
    print(f"{'Schritt':>6} | {'Gewählte Aktion':<65} | {'score_rules':>11}")
    print("-" * 90)

    for i, (action_str, score) in enumerate(history, start=0):
        action_short = action_str[:65]
        print(f"{i:>6} | {action_short:<65} | {score:>11}")

    print("-" * 90)


def run_one_step(
    env: Env,
    adapter: DorfromantikAdapter,
    state,
    n_iterations: int,
    exploration_constant: float,
    rollout_depth_limit: int | None,
    rng_seed: int,
    step_idx: int,
    verbose: bool,
):
    mcts = MCTS(
        adapter=adapter,
        exploration_constant=exploration_constant,
        rollout_depth_limit=rollout_depth_limit,
        rng_seed=rng_seed + step_idx,
    )

    result = mcts.search(state, n_iterations=n_iterations)
    best_action = result.best_action

    if verbose:
        print("\nMCTS")
        print("best_action       :", format_action(best_action))
        print("root_value        :", result.root_value)
        print("root_visits       :", result.root_visits)
        print("iterations        :", result.n_iterations)

    if best_action is None:
        return state, True, result, None, score_rules(state)

    state, done = env.step_fast(state, best_action)
    current_score = score_rules(state)

    if verbose:
        print("score_rules       :", current_score)

    return state, done, result, best_action, current_score


def main():
    # ---------------------------------
    # Parameter zum Herumspielen
    # ---------------------------------
    seed = 1
    n_iterations = 1000
    exploration_constant = 1.4
    rollout_depth_limit = 5   # z.B. 10
    rng_seed = 1

    # Modus:
    # "interactive" -> Enter für nächsten Schritt
    # "fast"        -> automatisch bis zum Ende
    mode = "fast"

    env = Env(seed=seed)
    state = env.reset(seed=seed)
    adapter = DorfromantikAdapter(env)

    history: list[tuple[str, int]] = []
    start_tile_history_entry = (
        f"kind=place_tile, tile_id={state.board[(0, 0)].tile_id}, pos=(0, 0), rot=0",
        score_rules(state),
    )
    history.append(start_tile_history_entry)
    step_idx = 0

    if mode == "interactive":
        print("Startzustand")
        print("board_size        :", len(state.board))
        print("phase             :", state.phase)
        print("current_tile      :", state.current_tile)
        print("main_stack_left   :", len(state.main_stack))
        print("task_stack_left   :", len(state.task_stack))
        print("score_rules       :", score_rules(state))

        if (0, 0) in state.board:
            start_tile = state.board[(0, 0)]
            print("start_tile        :", f"tile_id={start_tile.tile_id}, rot={start_tile.rot}")

    fast_t0 = None
    if mode == "fast":
        fast_t0 = time.perf_counter()

    while True:
        if adapter.is_terminal(state):
            if mode == "interactive":
                print("\nTERMINAL erreicht.")
            break

        if mode == "interactive":
            print("\n" + "=" * 70)
            print(f"STEP {step_idx}")
            print("=" * 70)
            print("board_size        :", len(state.board))
            print("phase             :", state.phase)
            print("current_tile      :", state.current_tile)
            print("current_tile_source :", state.current_tile_source)
            print("storehouse_tile   :", state.storehouse_tile)
            print("kontor_tile       :", state.kontor_tile)
            print("main_stack_left   :", len(state.main_stack))
            print("task_stack_left   :", len(state.task_stack))
            print("active_tasks      :", len(state.active_tasks))
            print("completed_tasks   :", len(state.completed_task_markers))
            print("failed_tasks      :", len(state.failed_task_markers))
            print("score_rules       :", score_rules(state))

        state, done, result, chosen_action, current_score = run_one_step(
            env=env,
            adapter=adapter,
            state=state,
            n_iterations=n_iterations,
            exploration_constant=exploration_constant,
            rollout_depth_limit=rollout_depth_limit,
            rng_seed=rng_seed,
            step_idx=step_idx,
            verbose=(mode == "interactive"),
        )

        if chosen_action is not None:
            history.append((format_action(chosen_action), current_score))
        else:
            history.append(("None", current_score))

        step_idx += 1

        if done:
            if mode == "interactive":
                print("\nDONE=True nach step_fast.")
            break

        if mode == "interactive":
            user_input = input("\nEnter = nächster Schritt | q = abbrechen\n> ").strip().lower()
            if user_input == "q":
                print("Abbruch durch Nutzer.")
                break

    final_score = score_rules(state)
    print("\nFinal score_rules :", final_score)
    print_history(history)

    if mode == "fast" and fast_t0 is not None:
        elapsed_sec = time.perf_counter() - fast_t0
        print(f"Fast-Modus Laufzeit : {elapsed_sec:.3f} Sekunden")

if __name__ == "__main__":
    main()