from __future__ import annotations

import copy
import random
from typing import Sequence

from dorfromantik.action import Action
from dorfromantik.env import Env
from dorfromantik.scoring import score_rules
from dorfromantik.state import State

from .interfaces import SearchAdapter


class DorfromantikAdapter(SearchAdapter[State, Action]):
    """
    Adapter zwischen bestehender Dorfromantik-Engine und generischem MCTS.
    """

    def __init__(self, env: Env):
        self.env = env

    def clone_state(self, state: State) -> State:
        # V1: bewusst simpel und korrekt.
        # Später wahrscheinlich durch manuelles Clone ersetzen.
        return copy.deepcopy(state)

    def legal_actions(self, state: State) -> Sequence[Action]:
        return self.env.legal_actions(state)

    def apply_action(self, state: State, action: Action) -> tuple[State, bool]:
        """
        Erwartet einen bereits geklonten State oder einen State,
        der mutiert werden darf.
        """
        next_state, done = self.env.step_fast(state, action)
        return next_state, done

    def is_terminal(self, state: State) -> bool:
        # 1. Ein aktuell aktives Tile bedeutet: Partie läuft noch.
        if state.current_tile is not None:
            return False

        # 2. Ein gelagertes Tile bedeutet ebenfalls: Partie läuft noch.
        if state.storehouse_tile is not None or state.kontor_tile is not None:
            return False

        # 3. Wenn nach deinem aktuellen Engine-Modell noch ein Auftragsplättchen
        #    nachkommen darf, ist die Partie noch nicht zu Ende.
        if len(state.active_tasks) < (3 + self.env._fujiyama_task_solved(state)) and state.task_stack:
            return False

        # 4. Wenn noch Landschaftsplättchen vorhanden sind, ist ebenfalls nicht terminal.
        if state.main_stack:
            return False

        # 5. Sonst ist Ende.
        return True

    def evaluate_terminal(self, state: State) -> float:
        return float(score_rules(state))

    def rollout_action(self, state: State, actions: Sequence[Action], rng: random.Random) -> Action:
        return actions[rng.randrange(len(actions))]