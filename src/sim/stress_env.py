from __future__ import annotations
from concurrent.futures import ProcessPoolExecutor
import os

import random
import statistics
import traceback
import time

from dorfromantik.env import Env
from sim.debug_checks import check_dsu_consistency
from dorfromantik.scoring import score_rules
from dorfromantik import tile_types as tt


def _run_one_episode_from_args(args):
    seed, do_consistency_checks, do_scoring, use_fast_step = args
    return run_one_episode(
        seed,
        do_consistency_checks=do_consistency_checks,
        do_scoring=do_scoring,
        use_fast_step=use_fast_step,
    )


def run_one_episode(
        seed: int,
        do_consistency_checks: bool = False,
        do_scoring: bool = False,
        use_fast_step: bool = False,
):
    env = Env(seed=seed)
    s = env.reset(seed=seed)
    rng = random.Random(seed)

    steps = 0
    error = None

    try:
        while True:
            acts = env.legal_actions(s)

            if not acts:
                end_reason = "no_legal_actions"
                break

            action = acts[rng.randrange(len(acts))]

            if use_fast_step:
                s, done = env.step_fast(s, action)
            else:
                s, reward, done, info = env.step(s, action)

            steps += 1

            if do_consistency_checks:
                check_dsu_consistency(s, verbose=False)

            if done:
                if s.current_tile is None:
                    end_reason = "bag_empty"
                else:
                    end_reason = "done_other"
                break

    except Exception as e:
        error = {
            "seed": seed,
            "step": steps,
            "exception_type": type(e).__name__,
            "message": str(e),
            "traceback": traceback.format_exc(),
        }
        end_reason = "error"

    road_max = 0
    river_max = 0

    feature_dsu = getattr(s, "feature_dsu", None)

    if feature_dsu is not None:
        road_dsu = feature_dsu.get(tt.EdgeType.Strasse)
        river_dsu = feature_dsu.get(tt.EdgeType.Fluss)

        if road_dsu:
            road_max = road_dsu.max_size
        if river_dsu:
            river_max = river_dsu.max_size

    # Berechnung Punkte nach Score-Sheet
    rules_score = score_rules(s) if do_scoring else None

    return {
        "seed": seed,
        "steps": steps,
        "end_reason": end_reason,
        "road_max": road_max,
        "river_max": river_max,
        "rules_score": rules_score,
        "error": error,
    }


def run_many_serial(
        n_runs: int,
        start_seed: int,
        progress_every: int,
        do_consistency_checks: bool,
        do_scoring: bool,
        use_fast_step: bool,
):
    results = []

    for i in range(n_runs):
        seed = start_seed + i

        if i % progress_every == 0:
            print(f"Run {i}/{n_runs}")

        result = run_one_episode(
            seed,
            do_consistency_checks=do_consistency_checks,
            do_scoring=do_scoring,
            use_fast_step=use_fast_step,
        )
        results.append(result)

        if result["error"] is not None:
            err = result["error"]
            print("\n===== ERROR DETECTED =====")
            print(f"seed      : {err['seed']}")
            print(f"step      : {err['step']}")
            print(f"type      : {err['exception_type']}")
            print(f"message   : {err['message']}")
            print("\nTraceback:")
            print(err["traceback"])

    return results


def run_many_parallel(
        n_runs: int,
        start_seed: int,
        progress_every: int,
        do_consistency_checks: bool,
        do_scoring: bool,
        use_fast_step: bool,
        max_workers: int | None = None,
):
    results = []

    args_list = [
        (start_seed + i, do_consistency_checks, do_scoring, use_fast_step)
        for i in range(n_runs)
    ]

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        for i, result in enumerate(executor.map(_run_one_episode_from_args, args_list), start=0):
            if i % progress_every == 0:
                print(f"Run {i}/{n_runs}")

            results.append(result)

            if result["error"] is not None:
                err = result["error"]
                print("\n===== ERROR DETECTED =====")
                print(f"seed      : {err['seed']}")
                print(f"step      : {err['step']}")
                print(f"type      : {err['exception_type']}")
                print(f"message   : {err['message']}")
                print("\nTraceback:")
                print(err["traceback"])

    return results


def summarize(results: list[dict]):
    steps = [r["steps"] for r in results]
    road_maxes = [r["road_max"] for r in results]
    river_maxes = [r["river_max"] for r in results]
    rules_scores = [r["rules_score"] for r in results if r["rules_score"] is not None]

    end_reason_counts = {}
    for r in results:
        end_reason_counts[r["end_reason"]] = end_reason_counts.get(r["end_reason"], 0) + 1

    errors = [r for r in results if r["error"] is not None]

    print("\n===== STRESS TEST SUMMARY =====")
    print("runs                 :", len(results))
    print("successful_runs      :", len(results) - len(errors))
    print("error_runs           :", len(errors))

    if steps:
        print("steps_mean           :", round(statistics.mean(steps), 3))
        print("steps_min            :", min(steps))
        print("steps_max            :", max(steps))

    if road_maxes:
        print("road_max_mean        :", round(statistics.mean(road_maxes), 3))
        print("road_max_best        :", max(road_maxes))

    if river_maxes:
        print("river_max_mean       :", round(statistics.mean(river_maxes), 3))
        print("river_max_best       :", max(river_maxes))

    if rules_scores:
        print("rules_score_mean     :", round(statistics.mean(rules_scores), 3))
        print("rules_score_best     :", max(rules_scores))

    print("end_reasons          :", end_reason_counts)

    if errors:
        print("\n===== ERRORS =====")
        for err_run in errors[:10]:
            err = err_run["error"]
            print(
                f"seed={err['seed']} step={err['step']} "
                f"{err['exception_type']}: {err['message']}"
            )


def main():
    n_runs = 100000
    start_seed = 0
    progress_every = 20000

    do_consistency_checks = False
    do_scoring = False
    use_fast_step = True

    use_multiprocessing = True
    max_workers = os.cpu_count()

    t0 = time.perf_counter()

    if use_multiprocessing:
        results = run_many_parallel(
            n_runs=n_runs,
            start_seed=start_seed,
            progress_every=progress_every,
            do_consistency_checks=do_consistency_checks,
            do_scoring=do_scoring,
            use_fast_step=use_fast_step,
            max_workers=max_workers,
        )
    else:
        results = run_many_serial(
            n_runs=n_runs,
            start_seed=start_seed,
            progress_every=progress_every,
            do_consistency_checks=do_consistency_checks,
            do_scoring=do_scoring,
            use_fast_step=use_fast_step,
        )

    t_total = time.perf_counter() - t0
    runs_per_second = n_runs / t_total if t_total > 0 else 0
    summarize(results)

    print("\n===== PERFORMANCE =====")
    print("total_runtime_sec     :", round(t_total, 3))
    print("runs_per_second       :", round(runs_per_second, 2))


def profile_main():
    import cProfile
    import pstats

    profiler = cProfile.Profile()
    profiler.enable()

    main()

    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats("cumtime").print_stats(40)


if __name__ == "__main__":
    do_profile = False

    if do_profile:
        profile_main()
    else:
        main()

