from __future__ import annotations

import argparse
import time
from pathlib import Path
import os
import sys

from dorfromantik.action import Action
from dorfromantik.env import Env
from dorfromantik.scoring import score_rules
from mcts.core import MCTS
from mcts.dorfromantik_adapter import DorfromantikAdapter
from tile_digitalisierung.render_board import render_board, show_board_image


def format_action(a: Action | None) -> str:
    if a is None:
        return "None"

    parts: list[str] = [f"kind={a.kind}"]

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
    print("\n" + "=" * 100)
    print("VERLAUF")
    print("=" * 100)
    print(f"{'Schritt':>6} | {'Gewählte Aktion':<72} | {'score_rules':>11}")
    print("-" * 100)

    for i, (action_str, score) in enumerate(history, start=0):
        print(f"{i:>6} | {action_str[:72]:<72} | {score:>11}")

    print("-" * 100)


def save_history_tsv(history: list[tuple[str, int]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8", newline="") as f:
        f.write("step\taction\tscore_rules\n")
        for i, (action_str, score) in enumerate(history, start=1):
            safe_action = action_str.replace("\t", " ").replace("\n", " ")
            f.write(f"{i}\t{safe_action}\t{score}\n")


from pathlib import Path
import os
import sys

def render_final_board(
    state,
    output_path: Path | None,
    show_window: bool,
) -> None:
    img = render_board(state.board)

    if output_path is None:
        output_path = Path("board_final.png")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path)
    print(f"Board-Rendering gespeichert: {output_path.resolve()}")

    if show_window:
        try:
            if os.name == "nt":
                os.startfile(str(output_path.resolve()))
            elif sys.platform == "darwin":
                import subprocess
                subprocess.Popen(["open", str(output_path.resolve())])
            else:
                import subprocess
                subprocess.Popen(["xdg-open", str(output_path.resolve())])
        except Exception as e:
            print(f"Board-Bild konnte nicht automatisch geöffnet werden: {e}")


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
        print("best_action :", format_action(best_action))
        print("root_value :", result.root_value)
        print("root_visits :", result.root_visits)
        print("iterations :", result.n_iterations)

    if best_action is None:
        return state, True, result, None, score_rules(state)

    state, done = env.step_fast(state, best_action)
    current_score = score_rules(state)

    if verbose:
        print("score_rules :", current_score)

    return state, done, result, best_action, current_score


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Dorfromantik Sakura MCTS smoke runner"
    )

    parser.add_argument(
        "--mode",
        choices=("fast", "interactive"),
        default="fast",
        help="Ausführungsmodus",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=1,
        help="Seed für Env.reset / Spielzustand",
    )
    parser.add_argument(
        "--rng-seed",
        type=int,
        default=1,
        help="Seed für MCTS-RNG",
    )
    parser.add_argument(
        "--n-iterations",
        type=int,
        default=250,
        help="MCTS-Iterationen pro Entscheidungszeitpunkt",
    )
    parser.add_argument(
        "--rollout-depth",
        type=int,
        default=6,
        help="Maximale Rollout-Tiefe; <= 0 bedeutet unbegrenzt",
    )
    parser.add_argument(
        "--exploration-constant",
        type=float,
        default=1.4,
        help="UCT-Explorationskonstante",
    )
    parser.add_argument(
        "--max-steps",
        type=int,
        default=300,
        help="Sicherheitslimit für maximale Schrittzahl",
    )
    parser.add_argument(
        "--save-history",
        type=str,
        default="",
        help="Optionaler Pfad zum Speichern des Verlaufs als TSV",
    )
    parser.add_argument(
        "--no-history-print",
        action="store_true",
        help="Verlaufstabelle am Ende nicht ausgeben",
    )

    parser.add_argument(
        "--no-render-final-board",
        action="store_false",
        dest="render_final_board",
        help="Finalen Boardstate nicht rendern",
    )
    parser.set_defaults(render_final_board=True)

    parser.add_argument(
        "--render-output",
        type=str,
        default="",
        help="Optionaler PNG-Pfad für den finalen Boardstate",
    )
    parser.add_argument(
        "--no-show-render-window",
        action="store_false",
        dest="show_render_window",
        help="Gerendertes Board nicht in einem Fenster anzeigen",
    )
    parser.set_defaults(show_render_window=True)
    return parser


def main() -> None:
    args = build_arg_parser().parse_args()

    print("Parameter:")
    print("mode :", args.mode)
    print("seed :", args.seed)
    print("rng_seed :", args.rng_seed)
    print("n_iterations :", args.n_iterations)
    print("rollout_depth :", args.rollout_depth)
    print("exploration_constant:", args.exploration_constant)
    print("max_steps :", args.max_steps)
    print("save_history :", args.save_history)
    print("no_history_print :", args.no_history_print)
    print("render_final_board :", args.render_final_board)
    print("render_output :", args.render_output)
    print("show_render_window :", args.show_render_window)

    rollout_depth_limit = None if args.rollout_depth <= 0 else args.rollout_depth

    env = Env(seed=args.seed)
    state = env.reset(seed=args.seed)
    adapter = DorfromantikAdapter(env)

    history: list[tuple[str, int]] = []
    start_tile_history_entry = (
        f"kind=place_tile, tile_id={state.board[(0, 0)].tile_id}, pos=(0, 0), rot=0",
        score_rules(state),
    )
    history.append(start_tile_history_entry)

    step_idx = 0

    if args.mode == "interactive":
        print("Startzustand")
        print("board_size :", len(state.board))
        print("phase :", state.phase)
        print("current_tile :", state.current_tile)
        print("current_tile_src :", getattr(state, "current_tile_source", None))
        print("main_stack_left :", len(state.main_stack))
        print("task_stack_left :", len(state.task_stack))
        print("score_rules :", score_rules(state))

        if (0, 0) in state.board:
            start_tile = state.board[(0, 0)]
            print("start_tile :", f"tile_id={start_tile.tile_id}, rot={start_tile.rot}")

    fast_t0 = time.perf_counter() if args.mode == "fast" else None

    while True:
        if adapter.is_terminal(state):
            if args.mode == "interactive":
                print("\nTERMINAL erreicht.")
            break

        if step_idx >= args.max_steps:
            print(f"\nAbbruch: max_steps={args.max_steps} erreicht.")
            break

        if args.mode == "interactive":
            print("\n" + "=" * 70)
            print(f"STEP {step_idx}")
            print("=" * 70)
            print("board_size :", len(state.board))
            print("phase :", state.phase)
            print("current_tile :", state.current_tile)
            print("current_tile_src :", getattr(state, "current_tile_source", None))
            print("storehouse_tile :", state.storehouse_tile)
            print("kontor_tile :", state.kontor_tile)
            print("main_stack_left :", len(state.main_stack))
            print("task_stack_left :", len(state.task_stack))
            print("active_tasks :", len(state.active_tasks))
            print("completed_tasks :", len(state.completed_task_markers))
            print("failed_tasks :", len(state.failed_task_markers))
            print("score_rules :", score_rules(state))

        state, done, result, chosen_action, current_score = run_one_step(
            env=env,
            adapter=adapter,
            state=state,
            n_iterations=args.n_iterations,
            exploration_constant=args.exploration_constant,
            rollout_depth_limit=rollout_depth_limit,
            rng_seed=args.rng_seed,
            step_idx=step_idx,
            verbose=(args.mode == "interactive"),
        )

        history.append((format_action(chosen_action), current_score))
        step_idx += 1

        if done:
            if args.mode == "interactive":
                print("\nDONE=True nach step_fast.")
            break

        if args.mode == "interactive":
            user_input = input("\nEnter = nächster Schritt | q = abbrechen\n> ").strip().lower()
            if user_input == "q":
                print("Abbruch durch Nutzer.")
                break

    final_score = score_rules(state)
    print("\nFinal score_rules :", final_score)

    if args.mode == "fast" and fast_t0 is not None:
        elapsed_sec = time.perf_counter() - fast_t0
        print(f"Laufzeit : {elapsed_sec:.3f} Sekunden")

    if not args.no_history_print:
        print_history(history)

    if args.save_history:
        output_path = Path(args.save_history)
        save_history_tsv(history, output_path)
        print(f"Verlauf gespeichert: {output_path}")

    if args.render_final_board:
        render_output_path = Path(args.render_output) if args.render_output else None
        render_final_board(
            state=state,
            output_path=render_output_path,
            show_window=args.show_render_window,
        )


if __name__ == "__main__":
    main()