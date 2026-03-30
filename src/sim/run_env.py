import random
import matplotlib.pyplot as plt

# from dorfromantik.render_ascii import render_ascii
from dorfromantik.env import Env
import dorfromantik.tile_types as tt
from tile_digitalisierung.render_board import render_and_show
from sim.debug_checks import check_dsu_consistency, debug_print_dsus
from dorfromantik.scoring import score_rules

# Falls dein DSU-Update in env.step() noch nicht drin ist:
# from dorfromantik.dsu_update import update_all_dsus_after_place

TRACKED_TYPES = (
    tt.EdgeType.Sakura,
    tt.EdgeType.Reis,
    tt.EdgeType.Dorf,
    tt.EdgeType.Strasse,
    tt.EdgeType.Fluss,
    tt.EdgeType.Heisse_Quellen,
    tt.EdgeType.Vulkan
)

DETAIL_TYPES = (
    tt.EdgeType.Sakura,
    tt.EdgeType.Reis,
    tt.EdgeType.Dorf,
    tt.EdgeType.Strasse,
    tt.EdgeType.Fluss
)

CONTINUITY_TYPES = {
    tt.EdgeType.Strasse,
    tt.EdgeType.Fluss,
    tt.EdgeType.Heisse_Quellen,
    tt.EdgeType.Vulkan
}


def main():
    env = Env(seed=1)
    s = env.reset()

    step = 0
    max_steps = 100

    while True:
        acts = env.legal_actions(s)

        print(f"\nSTEP {step}")
        print("  current_tile:", s.current_tile)
        print("  board_size  :", len(s.board))
        print("  tasks_left    :", len(s.task_stack))
        print("  main_left    :", len(s.main_stack))
        print("  n_actions   :", len(acts))
        # print("  next_action_list:")
        # for a in acts:
        #     print("   ", a)

        if not acts:
            print("  TERMINAL: no legal actions")
            break

        # besser zum Testen: random statt immer acts[0]
        a = acts[random.randrange(len(acts))]
        # a = acts[0]

        try:
            s, r, done, info = env.step(s, a)
        except AssertionError as e:
            print("  [ERROR] AssertionError in step():", e)
            raise

        # Berechnung nach Score-Sheet
        score = score_rules(s)

        print("  action_kind :", info.last_action.kind)

        if info.last_action.choice is not None:
            print("  choice      :", info.last_action.choice)

        if info.placed_tile is not None:
            print("  placed      :", info.placed_tile, "at", info.placed_pos, "rot", info.placed_rot)

        if info.stored_tile is not None:
            print("  stored      :", info.stored_tile, "in", info.stored_in)

        if info.chosen_source is not None:
            print("  source      :", info.chosen_source)
            print("  drawn_tile  :", info.drawn_tile)

        if info.newly_completed_tasks:
            print("  completed   :", info.newly_completed_tasks)

        if info.newly_failed_tasks:
            print("  failed      :", info.newly_failed_tasks)

        print("  next_tile   :", info.next_tile)
        print("  next_phase  :", info.next_phase)
        print("  next_actions:", info.n_legal_next)
        print("  score_rules :", score)

        # -------------------------------
        # Board visualisieren
        # -------------------------------
        render_and_show(s.board)

        # Debug DSU nach jedem Schritt
        debug_print_dsus(s)
        check_dsu_consistency(s, verbose=True)

        step += 1

        if done:
            print("\nTERMINAL: done=True")
            break

        if step >= max_steps:
            print("\nSTOP: reached max_steps =", max_steps)
            break

    # finales Bild speichern
    final_img = render_and_show(s.board)
    final_img.save("final_board.png")
    print("\nSaved final board to final_board.png")

    # Fenster offen halten
    plt.ioff()
    plt.show()


if __name__ == "__main__":
    main()
