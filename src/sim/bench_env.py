import time
import random

def run_many(EnvCls, n_episodes=500, seed0=0):
    t0 = time.perf_counter()
    steps_total = 0
    for s in range(seed0, seed0 + n_episodes):
        env = EnvCls(seed=s)
        st = env.reset(seed=s)
        rng = random.Random(s)
        while True:
            acts = env.legal_actions(st)
            if not acts:
                break
            a = acts[rng.randrange(len(acts))]
            st, r, done, info = env.step(st, a)
            steps_total += 1
            if done:
                break
    dt = time.perf_counter() - t0
    return dt, steps_total

def main():
    # vorher
    from dorfromantik.env_slow import Env as EnvSlow
    # nachher
    from dorfromantik.env import Env as EnvFast

    dt1, steps1 = run_many(EnvSlow, n_episodes=200, seed0=0)
    dt2, steps2 = run_many(EnvFast, n_episodes=200, seed0=0)

    print("SLOW:", dt1, "seconds.", "Steps:", steps1, ", steps/sec:", steps1/dt1)
    print("FAST:", dt2, "seconds.", "Steps:", steps2, ", steps/sec", steps2/dt2)
    print("speedup:", dt1/dt2)

if __name__ == "__main__":
    main()