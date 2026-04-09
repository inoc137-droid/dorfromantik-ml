from __future__ import annotations

import argparse
import csv
import inspect
import json
import math
import random
import statistics
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Iterable

from dorfromantik.action import Action
from dorfromantik.env import Env
from dorfromantik.scoring import score_rules
from mcts.core import MCTS
from mcts.dorfromantik_adapter import DorfromantikAdapter


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------


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


def parse_int_list(text: str) -> list[int]:
    text = text.strip()
    if not text:
        return []
    return [int(part.strip()) for part in text.split(",") if part.strip()]


def linspace_int(start: int, stop: int, num: int) -> list[int]:
    if num <= 1:
        return [int(round(start))]
    if start == stop:
        return [int(start)]
    vals = [start + (stop - start) * i / (num - 1) for i in range(num)]
    return dedupe_preserve_order(int(round(v)) for v in vals)


def logspace_int(start: int, stop: int, num: int) -> list[int]:
    if start <= 0 or stop <= 0:
        raise ValueError("Für logspace müssen start und stop > 0 sein.")
    if num <= 1:
        return [int(round(start))]
    if start == stop:
        return [int(start)]
    log_start = math.log10(start)
    log_stop = math.log10(stop)
    vals = [10 ** (log_start + (log_stop - log_start) * i / (num - 1)) for i in range(num)]
    return dedupe_preserve_order(max(1, int(round(v))) for v in vals)


def dedupe_preserve_order(values: Iterable[int]) -> list[int]:
    out: list[int] = []
    seen: set[int] = set()
    for value in values:
        if value not in seen:
            out.append(value)
            seen.add(value)
    return out


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def safe_mean(values: list[float]) -> float:
    return statistics.fmean(values) if values else float("nan")


def safe_stdev(values: list[float]) -> float:
    return statistics.stdev(values) if len(values) >= 2 else 0.0


def quantize_float(x: float, digits: int = 6) -> float:
    return round(float(x), digits)


# -----------------------------------------------------------------------------
# Runtime adaptation to different MCTS APIs
# -----------------------------------------------------------------------------


_MCTS_INIT_SIGNATURE = inspect.signature(MCTS.__init__)
_MCTS_SEARCH_SIGNATURE = inspect.signature(MCTS.search)


def _set_first_matching_name(target: dict[str, Any], value: Any, candidate_names: list[str]) -> bool:
    for name in candidate_names:
        if name in target:
            target[name] = value
            return True
    return False


@dataclass(slots=True)
class MCTSApiSupport:
    root_param_name: str | None
    leaf_param_name: str | None
    init_param_names: tuple[str, ...]
    search_param_names: tuple[str, ...]


def detect_mcts_api_support() -> MCTSApiSupport:
    init_names = tuple(_MCTS_INIT_SIGNATURE.parameters.keys())
    search_names = tuple(_MCTS_SEARCH_SIGNATURE.parameters.keys())

    root_candidates = [
        "root_parallelization",
        "root_parallelism",
        "root_workers",
        "n_root_workers",
        "root_rollout_workers",
        "num_root_workers",
        "root_processes",
    ]
    leaf_candidates = [
        "leaf_parallelization",
        "leaf_parallelism",
        "leaf_rollouts",
        "leaf_rollout_batch_size",
        "leaf_batch_size",
        "n_leaf_rollouts",
        "num_leaf_rollouts",
    ]

    root_name = next((name for name in root_candidates if name in init_names or name in search_names), None)
    leaf_name = next((name for name in leaf_candidates if name in init_names or name in search_names), None)

    return MCTSApiSupport(
        root_param_name=root_name,
        leaf_param_name=leaf_name,
        init_param_names=init_names,
        search_param_names=search_names,
    )


def build_mcts(
    adapter: DorfromantikAdapter,
    exploration_constant: float,
    rollout_depth_limit: int | None,
    rng_seed: int,
    root_parallelization: int,
    leaf_rollouts: int,
) -> tuple[MCTS, dict[str, Any], MCTSApiSupport]:
    support = detect_mcts_api_support()

    init_kwargs: dict[str, Any] = {}
    for name in _MCTS_INIT_SIGNATURE.parameters.keys():
        if name == "self":
            continue
        if name == "adapter":
            init_kwargs[name] = adapter
        elif name == "exploration_constant":
            init_kwargs[name] = exploration_constant
        elif name == "rollout_depth_limit":
            init_kwargs[name] = rollout_depth_limit
        elif name == "rng_seed":
            init_kwargs[name] = rng_seed

    if support.root_param_name and support.root_param_name in init_kwargs:
        init_kwargs[support.root_param_name] = root_parallelization
    if support.leaf_param_name and support.leaf_param_name in init_kwargs:
        init_kwargs[support.leaf_param_name] = leaf_rollouts

    mcts = MCTS(**init_kwargs)

    search_kwargs: dict[str, Any] = {}
    for name in _MCTS_SEARCH_SIGNATURE.parameters.keys():
        if name == "self":
            continue
        if name == "root_state":
            # Later, when calling search.
            continue
        if name == "n_iterations":
            continue
        if support.root_param_name and name == support.root_param_name:
            search_kwargs[name] = root_parallelization
        if support.leaf_param_name and name == support.leaf_param_name:
            search_kwargs[name] = leaf_rollouts

    return mcts, search_kwargs, support


# -----------------------------------------------------------------------------
# Simulation
# -----------------------------------------------------------------------------


@dataclass(slots=True)
class RunResult:
    config_id: str
    repeat_idx: int
    env_seed: int
    mcts_seed: int
    n_iterations: int
    rollout_depth: int
    root_parallelization: int
    leaf_rollouts: int
    exploration_constant: float
    final_score: int
    total_steps: int
    terminated: bool
    aborted_by_max_steps: bool
    runtime_sec: float
    score_history_json: str
    action_history_json: str
    start_tile_id: int | None
    mcts_root_param_supported: bool
    mcts_leaf_param_supported: bool
    mcts_root_param_name: str
    mcts_leaf_param_name: str


@dataclass(slots=True)
class AggregateResult:
    config_id: str
    repeats: int
    n_iterations: int
    rollout_depth: int
    root_parallelization: int
    leaf_rollouts: int
    exploration_constant: float
    mean_final_score: float
    std_final_score: float
    min_final_score: int
    max_final_score: int
    mean_total_steps: float
    std_total_steps: float
    mean_runtime_sec: float
    std_runtime_sec: float
    terminated_runs: int
    aborted_runs: int


class SmokeGridRunner:
    def __init__(self, args: argparse.Namespace):
        self.args = args
        self.master_rng = random.Random(args.master_seed)
        self.output_dir = Path(args.output_dir)
        ensure_dir(self.output_dir)

    def iter_configs(self) -> list[dict[str, Any]]:
        if self.args.n_iterations_values:
            n_iterations_values = parse_int_list(self.args.n_iterations_values)
        else:
            n_iterations_values = logspace_int(
                self.args.n_iterations_min,
                self.args.n_iterations_max,
                self.args.n_iterations_count,
            )

        if self.args.rollout_depth_values:
            rollout_depth_values = parse_int_list(self.args.rollout_depth_values)
        else:
            rollout_depth_values = linspace_int(
                self.args.rollout_depth_min,
                self.args.rollout_depth_max,
                self.args.rollout_depth_count,
            )

        root_values = parse_int_list(self.args.root_parallelization_values)
        leaf_values = parse_int_list(self.args.leaf_rollouts_values)

        configs: list[dict[str, Any]] = []
        config_idx = 0
        for n_iterations in n_iterations_values:
            for rollout_depth in rollout_depth_values:
                for root_parallelization in root_values:
                    for leaf_rollouts in leaf_values:
                        config_id = (
                            f"cfg_{config_idx:04d}"
                            f"_it{n_iterations}"
                            f"_depth{rollout_depth}"
                            f"_root{root_parallelization}"
                            f"_leaf{leaf_rollouts}"
                        )
                        configs.append(
                            {
                                "config_id": config_id,
                                "n_iterations": n_iterations,
                                "rollout_depth": rollout_depth,
                                "root_parallelization": root_parallelization,
                                "leaf_rollouts": leaf_rollouts,
                            }
                        )
                        config_idx += 1
        return configs

    def run(self) -> None:
        configs = self.iter_configs()
        run_results: list[RunResult] = []

        meta = {
            "created_at_epoch_sec": time.time(),
            "master_seed": self.args.master_seed,
            "repeats": self.args.repeats,
            "n_configs": len(configs),
            "exploration_constant": self.args.exploration_constant,
            "max_steps": self.args.max_steps,
            "n_iterations_values": [cfg["n_iterations"] for cfg in configs],
        }
        (self.output_dir / "meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")

        total_runs = len(configs) * self.args.repeats
        run_counter = 0

        for cfg in configs:
            for repeat_idx in range(self.args.repeats):
                run_counter += 1
                result = self.run_single(cfg, repeat_idx)
                run_results.append(result)
                if not self.args.quiet:
                    print(
                        f"[{run_counter:>4}/{total_runs}] {result.config_id} "
                        f"rep={repeat_idx:02d} score={result.final_score:>4} "
                        f"steps={result.total_steps:>3} time={result.runtime_sec:.3f}s"
                    )

        self.write_run_results(run_results)
        self.write_aggregate_results(run_results)

    def run_single(self, cfg: dict[str, Any], repeat_idx: int) -> RunResult:
        env_seed = self.master_rng.randrange(0, 2**31 - 1)
        mcts_seed = self.master_rng.randrange(0, 2**31 - 1)

        env = Env(seed=env_seed)
        state = env.reset(seed=env_seed)
        adapter = DorfromantikAdapter(env)

        score_history: list[int] = [score_rules(state)]
        action_history: list[str] = [
            f"kind=place_tile, tile_id={state.board[(0, 0)].tile_id}, pos=(0, 0), rot=0"
            if (0, 0) in state.board
            else "start_state"
        ]
        start_tile_id = state.board[(0, 0)].tile_id if (0, 0) in state.board else None

        rollout_depth_limit = None if cfg["rollout_depth"] <= 0 else cfg["rollout_depth"]

        t0 = time.perf_counter()
        total_steps = 0
        terminated = False
        aborted_by_max_steps = False
        support_snapshot: MCTSApiSupport | None = None

        while True:
            if adapter.is_terminal(state):
                terminated = True
                break
            if total_steps >= self.args.max_steps:
                aborted_by_max_steps = True
                break

            mcts, search_kwargs, support = build_mcts(
                adapter=adapter,
                exploration_constant=self.args.exploration_constant,
                rollout_depth_limit=rollout_depth_limit,
                rng_seed=mcts_seed + total_steps,
                root_parallelization=cfg["root_parallelization"],
                leaf_rollouts=cfg["leaf_rollouts"],
            )
            support_snapshot = support

            search_kwargs = dict(search_kwargs)
            search_kwargs["root_state"] = state
            search_kwargs["n_iterations"] = cfg["n_iterations"]
            result = mcts.search(**search_kwargs)
            best_action = result.best_action

            if best_action is None:
                terminated = True
                break

            state, done = env.step_fast(state, best_action)
            total_steps += 1
            action_history.append(format_action(best_action))
            score_history.append(score_rules(state))

            if done:
                terminated = True
                break

        runtime_sec = time.perf_counter() - t0
        final_score = score_rules(state)

        if support_snapshot is None:
            support_snapshot = detect_mcts_api_support()

        return RunResult(
            config_id=cfg["config_id"],
            repeat_idx=repeat_idx,
            env_seed=env_seed,
            mcts_seed=mcts_seed,
            n_iterations=cfg["n_iterations"],
            rollout_depth=cfg["rollout_depth"],
            root_parallelization=cfg["root_parallelization"],
            leaf_rollouts=cfg["leaf_rollouts"],
            exploration_constant=self.args.exploration_constant,
            final_score=final_score,
            total_steps=total_steps,
            terminated=terminated,
            aborted_by_max_steps=aborted_by_max_steps,
            runtime_sec=quantize_float(runtime_sec),
            score_history_json=json.dumps(score_history, ensure_ascii=False),
            action_history_json=json.dumps(action_history, ensure_ascii=False),
            start_tile_id=start_tile_id,
            mcts_root_param_supported=bool(support_snapshot.root_param_name),
            mcts_leaf_param_supported=bool(support_snapshot.leaf_param_name),
            mcts_root_param_name=support_snapshot.root_param_name or "",
            mcts_leaf_param_name=support_snapshot.leaf_param_name or "",
        )

    def write_run_results(self, run_results: list[RunResult]) -> None:
        path = self.output_dir / "smoke_grid_runs.csv"
        with path.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(asdict(run_results[0]).keys()))
            writer.writeheader()
            for result in run_results:
                writer.writerow(asdict(result))

    def write_aggregate_results(self, run_results: list[RunResult]) -> None:
        grouped: dict[str, list[RunResult]] = {}
        for result in run_results:
            grouped.setdefault(result.config_id, []).append(result)

        aggregates: list[AggregateResult] = []
        for config_id, results in grouped.items():
            scores = [r.final_score for r in results]
            steps = [r.total_steps for r in results]
            runtimes = [r.runtime_sec for r in results]
            first = results[0]
            aggregates.append(
                AggregateResult(
                    config_id=config_id,
                    repeats=len(results),
                    n_iterations=first.n_iterations,
                    rollout_depth=first.rollout_depth,
                    root_parallelization=first.root_parallelization,
                    leaf_rollouts=first.leaf_rollouts,
                    exploration_constant=first.exploration_constant,
                    mean_final_score=quantize_float(safe_mean(scores)),
                    std_final_score=quantize_float(safe_stdev(scores)),
                    min_final_score=min(scores),
                    max_final_score=max(scores),
                    mean_total_steps=quantize_float(safe_mean(steps)),
                    std_total_steps=quantize_float(safe_stdev(steps)),
                    mean_runtime_sec=quantize_float(safe_mean(runtimes)),
                    std_runtime_sec=quantize_float(safe_stdev(runtimes)),
                    terminated_runs=sum(1 for r in results if r.terminated),
                    aborted_runs=sum(1 for r in results if r.aborted_by_max_steps),
                )
            )

        aggregates.sort(
            key=lambda x: (
                x.n_iterations,
                x.rollout_depth,
                x.root_parallelization,
                x.leaf_rollouts,
            )
        )

        path = self.output_dir / "smoke_grid_summary.csv"
        with path.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(asdict(aggregates[0]).keys()))
            writer.writeheader()
            for row in aggregates:
                writer.writerow(asdict(row))

        txt_path = self.output_dir / "smoke_grid_summary_top.txt"
        ranked = sorted(
            aggregates,
            key=lambda x: (x.mean_final_score, -x.mean_runtime_sec),
            reverse=True,
        )
        lines = [
            "Top-Konfigurationen nach mean_final_score\n",
            "rank | config_id | mean_score | std_score | mean_runtime | iters | depth | root | leaf\n",
            "-" * 100 + "\n",
        ]
        for rank, row in enumerate(ranked[: min(20, len(ranked))], start=1):
            lines.append(
                f"{rank:>4} | {row.config_id} | {row.mean_final_score:>10.3f} | "
                f"{row.std_final_score:>9.3f} | {row.mean_runtime_sec:>12.3f} | "
                f"{row.n_iterations:>5} | {row.rollout_depth:>5} | "
                f"{row.root_parallelization:>4} | {row.leaf_rollouts:>4}\n"
            )
        txt_path.write_text("".join(lines), encoding="utf-8")


# -----------------------------------------------------------------------------
# CLI
# -----------------------------------------------------------------------------


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Grid-Wrapper für den Dorfromantik-Sakura MCTS smoke test."
    )
    parser.add_argument("--output-dir", type=str, default="smoke_grid_results")
    parser.add_argument("--master-seed", type=int, default=None)
    parser.add_argument("--repeats", type=int, default=10, help="Anzahl Wiederholungen pro Konfiguration.")
    parser.add_argument("--exploration-constant", type=float, default=1.4)
    parser.add_argument("--max-steps", type=int, default=300)
    parser.add_argument("--quiet", action="store_true")

    parser.add_argument("--n-iterations-min", type=int, default=50)
    parser.add_argument("--n-iterations-max", type=int, default=5000)
    parser.add_argument("--n-iterations-count", type=int, default=6)
    parser.add_argument(
        "--n-iterations-values",
        type=str,
        default="",
        help="Explizite Liste statt logspace, z. B. '50,100,250,500,1000'.",
    )

    parser.add_argument("--rollout-depth-min", type=int, default=2)
    parser.add_argument("--rollout-depth-max", type=int, default=10)
    parser.add_argument("--rollout-depth-count", type=int, default=5)
    parser.add_argument(
        "--rollout-depth-values",
        type=str,
        default="",
        help="Explizite Liste statt linspace, z. B. '2,4,6,8,10'.",
    )

    parser.add_argument(
        "--root-parallelization-values",
        type=str,
        default="1,2,4",
        help="Liste zu testender Root-Parallelisierungen.",
    )
    parser.add_argument(
        "--leaf-rollouts-values",
        type=str,
        default="1,4,8,20",
        help="Liste zu testender Leaf-Rollout-Batches.",
    )
    return parser


def validate_args(args: argparse.Namespace) -> argparse.Namespace:
    if args.repeats <= 0:
        raise SystemExit("--repeats muss > 0 sein.")
    if args.n_iterations_count <= 0:
        raise SystemExit("--n-iterations-count muss > 0 sein.")
    if args.rollout_depth_count <= 0:
        raise SystemExit("--rollout-depth-count muss > 0 sein.")
    if args.master_seed is None:
        args.master_seed = random.SystemRandom().randrange(0, 2**31 - 1)
    return args


def main() -> None:
    args = validate_args(build_arg_parser().parse_args())
    runner = SmokeGridRunner(args)
    runner.run()


if __name__ == "__main__":
    main()
