from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, Protocol, Sequence, TypeVar

S = TypeVar("S")   # State
A = TypeVar("A")   # Action


@dataclass(frozen=True, slots=True)
class SearchResult(Generic[A]):
    best_action: A | None
    n_iterations: int
    root_value: float
    root_visits: int


class SearchAdapter(Protocol[S, A]):
    """
    Minimale Schnittstelle zwischen Spiel-Engine und MCTS.
    """

    def clone_state(self, state: S) -> S:
        ...

    def legal_actions(self, state: S) -> Sequence[A]:
        """
        Hier werden alle legalen Aktionen A zum State S ausgegeben.
        Allerdings ist die Auswahl ohne Pruning -> Optimierung!
        :param state:
        :return:
        """
        ...

    def apply_action(self, state: S, action: A) -> tuple[S, bool]:
        """
        Führt die Aktion auf einem State aus und gibt
        (next_state, done) zurück.
        """
        ...

    def is_terminal(self, state: S) -> bool:
        ...

    def evaluate_terminal(self, state: S) -> float:
        """
        Terminale Bewertung des Zustands.
        Für Dorfromantik zunächst score_rules(state).
        """
        ...

    def rollout_action(self, state: S, actions: Sequence[A], rng) -> A:
        """
        Policy für Rollouts.
        V1: uniform random.
        """
        ...