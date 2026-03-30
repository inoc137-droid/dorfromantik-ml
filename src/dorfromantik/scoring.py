from __future__ import annotations

from dorfromantik.state import State
from dorfromantik.tiles import TILES
import dorfromantik.tile_types as tt
import dorfromantik.tasks as tasks


def _aggregate_completed_tasks(s: State) -> dict[tt.TaskType, int]:
    agg: dict[tt.TaskType, int] = {}

    for marker in s.completed_task_markers:
        t = marker.task_type
        agg[t] = agg.get(t, 0) + marker.points

    return agg


def _closed_flag_region_points(s: State, edge_type: tt.EdgeType) -> int:
    """
    Punkte für Fahnen eines Landschaftstyps in abgeschlossenen Gebieten.

    Regel:
    - Nur Fahnen in abgeschlossenen Gebieten zählen.
    - Pro passender Fahne gibt es Punkte in Höhe der Größe des Gebiets.
    - Mehrere passende Fahnen in derselben Komponente zählen jeweils separat.
    """
    dsu = s.feature_dsu[edge_type]
    score = 0

    for root in dsu.parent:
        if dsu.find(root) != root:
            continue
        if not dsu.closed.get(root, False):
            continue

        n_flags = len(dsu.flag_positions[root].get(edge_type, set()))
        score += n_flags * dsu.size[root]

    return score


def _longest_component_members(s: State, edge_type: tt.EdgeType) -> set[tt.Pos]:
    dsu = s.feature_dsu[edge_type]

    best_root = None
    best_size = 0

    for root in dsu.parent:
        if dsu.find(root) != root:
            continue
        size = dsu.size[root]
        if size > best_size:
            best_size = size
            best_root = root

    if best_root is None:
        return set()

    return set(dsu.members[best_root])


def _longest_component_size(s: State, edge_type: tt.EdgeType) -> int:
    dsu = s.feature_dsu[edge_type]

    best_size = 0
    for root in dsu.parent:
        if dsu.find(root) != root:
            continue
        best_size = max(best_size, dsu.size[root])

    return best_size


def _rundum_bonus_on_longest(s: State) -> int:
    """
    Je 2 Punkte für erfüllte Rundumaufträge,
    die an die längste Straße oder den längsten Fluss angrenzen.
    """
    longest_road_members = _longest_component_members(s, tt.EdgeType.Strasse)
    longest_river_members = _longest_component_members(s, tt.EdgeType.Fluss)

    bonus = 0

    for active in s.active_tasks:
        # Nur noch aktive Aufträge sind hier irrelevant
        # Rundum-Bonus soll auf erfüllten Aufträgen basieren
        pass

    # Deshalb über die bereits erfüllten Rundum-Aufträge gehen:
    completed_rundum_positions = []

    for task in s.completed_task_markers:
        if task.task_type != tt.TaskType.Rundum:
            continue

    # Positionen stehen nicht in completed_task_markers, sondern in active_tasks.
    # Deshalb rekonstruierbar nur, wenn Rundum-Aufträge beim Erfüllen separat gespeichert würden.
    # Mit aktuellem State ist das nicht direkt möglich.
    return bonus


def score_rules(s: State) -> int:
    score = 0

    # Aufträge nach Typ
    task_points = _aggregate_completed_tasks(s)

    score += task_points.get(tt.TaskType.Sakura, 0)
    score += task_points.get(tt.TaskType.Reis, 0)
    score += task_points.get(tt.TaskType.Dorf, 0)
    score += task_points.get(tt.TaskType.Strasse, 0)
    score += task_points.get(tt.TaskType.Fluss, 0)
    score += task_points.get(tt.TaskType.Rundum, 0)

    # Fahnenwertung abgeschlossener Gebiete
    score += _closed_flag_region_points(s, tt.EdgeType.Sakura)
    score += _closed_flag_region_points(s, tt.EdgeType.Reis)
    score += _closed_flag_region_points(s, tt.EdgeType.Dorf)

    # Längste Strasse / längster Fluss
    score += _longest_component_size(s, tt.EdgeType.Strasse)
    score += _longest_component_size(s, tt.EdgeType.Fluss)

    return score