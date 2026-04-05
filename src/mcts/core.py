from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import Generic, TypeVar

from .interfaces import SearchAdapter, SearchResult

S = TypeVar("S")
A = TypeVar("A")


@dataclass(slots=True)
class Node(Generic[S, A]):
    state: S
    parent: "Node[S, A] | None" = None
    action_from_parent: A | None = None

    visits: int = 0
    value_sum: float = 0.0

    is_terminal: bool = False
    expanded: bool = False

    untried_actions: list[A] = field(default_factory=list)
    children: dict[A, "Node[S, A]"] = field(default_factory=dict)

    def mean_value(self) -> float:
        if self.visits == 0:
            return 0.0
        return self.value_sum / self.visits


class MCTS(Generic[S, A]):
    def __init__(
        self,
        adapter: SearchAdapter[S, A],
        exploration_constant: float = math.sqrt(2.0),
        rollout_depth_limit: int | None = None,
        rng_seed: int = 0,
    ):
        self.adapter = adapter
        self.c = exploration_constant
        self.rollout_depth_limit = rollout_depth_limit
        self.rng = random.Random(rng_seed)

    def search(self, root_state: S, n_iterations: int) -> SearchResult[A]:
        root_clone = self.adapter.clone_state(root_state)
        root = Node[S, A](
            state=root_clone,
            parent=None,
            action_from_parent=None,
        )
        self._initialize_node(root)

        for _ in range(n_iterations):
            leaf = self._select(root)
            child = self._expand(leaf)
            value = self._simulate(child)
            self._backpropagate(child, value)

        best_action = self._best_action(root)

        return SearchResult(
            best_action=best_action,
            n_iterations=n_iterations,
            root_value=root.mean_value(),
            root_visits=root.visits,
        )

    def _initialize_node(self, node: Node[S, A]) -> None:
        node.is_terminal = self.adapter.is_terminal(node.state)
        if node.is_terminal:
            node.untried_actions = []
            node.expanded = True
            return

        actions = list(self.adapter.legal_actions(node.state))
        node.untried_actions = actions
        node.expanded = (len(actions) == 0)

    def _select(self, node: Node[S, A]) -> Node[S, A]:
        current = node

        while True:
            if current.is_terminal:
                return current

            #### Hier Möglichkeit des Prunings. Nicht alle untried_actions ausprobieren,
            #### sondern wenn möglich einschränken?
            if current.untried_actions:
                return current

            if not current.children:
                return current

            current = self._best_uct_child(current)

    def _expand(self, node: Node[S, A]) -> Node[S, A]:
        if node.is_terminal:
            return node

        if not node.untried_actions:
            return node

        action = node.untried_actions.pop()

        next_state = self.adapter.clone_state(node.state)
        next_state, done = self.adapter.apply_action(next_state, action)

        child = Node[S, A](
            state=next_state,
            parent=node,
            action_from_parent=action,
        )
        child.is_terminal = done or self.adapter.is_terminal(next_state)

        if not child.is_terminal:
            child.untried_actions = list(self.adapter.legal_actions(next_state))
        else:
            child.untried_actions = []

        child.expanded = True
        node.children[action] = child
        return child

    def _simulate(self, node: Node[S, A]) -> float:
        if node.is_terminal:
            return self.adapter.evaluate_terminal(node.state)

        rollout_state = self.adapter.clone_state(node.state)
        depth = 0

        while True:
            if self.adapter.is_terminal(rollout_state):
                return self.adapter.evaluate_terminal(rollout_state)

            if self.rollout_depth_limit is not None and depth >= self.rollout_depth_limit:
                # V1: noch keine Heuristik.
                # Deshalb vorerst ebenfalls terminale Näherung.
                return self.adapter.evaluate_terminal(rollout_state)

            actions = list(self.adapter.legal_actions(rollout_state))
            if not actions:
                return self.adapter.evaluate_terminal(rollout_state)

            action = self.adapter.rollout_action(rollout_state, actions, self.rng)
            rollout_state, done = self.adapter.apply_action(rollout_state, action)

            depth += 1

            if done:
                return self.adapter.evaluate_terminal(rollout_state)

    def _backpropagate(self, node: Node[S, A], value: float) -> None:
        current = node
        while current is not None:
            current.visits += 1
            current.value_sum += value
            current = current.parent

    def _best_uct_child(self, node: Node[S, A]) -> Node[S, A]:
        assert node.children, "_best_uct_child called on node without children"
        assert node.visits > 0, "Parent node must have visits > 0 for UCT"

        best_child = None
        best_score = float("-inf")

        log_parent_visits = math.log(node.visits)

        for child in node.children.values():
            if child.visits == 0:
                uct = float("inf")
            else:
                exploit = child.value_sum / child.visits
                explore = self.c * math.sqrt(log_parent_visits / child.visits)
                uct = exploit + explore

            if uct > best_score:
                best_score = uct
                best_child = child

        assert best_child is not None
        return best_child

    def _best_action(self, root: Node[S, A]) -> A | None:
        if not root.children:
            return None

        ### Robust max child ebenso möglich: Hohe Besuche + hoher Mittelwert
        best_child = max(root.children.values(), key=lambda child: child.visits)
        return best_child.action_from_parent
