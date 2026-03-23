from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, List
import random

from dorfromantik.state import State
from dorfromantik.rules import legal_actions, is_legal_placement
from dorfromantik.tiles import TILES, ROT_EDGES, ROAD_EDGE_INDICES_BY_TILE_ROT, RIVER_EDGE_INDICES_BY_TILE_ROT
from dorfromantik.dsu_update import update_all_dsus_after_place, update_neighbor_dsus_after_place
from dorfromantik.action import Action
from dorfromantik.stepinfo import StepInfo
import dorfromantik.tile_types as tt
import dorfromantik.tasks as tasks


class Env:
    def __init__(
            self,
            main_stack: Optional[List[int]] = None,
            task_stack: Optional[List[int]] = None,
            seed: int = 0
    ):
        self.rng = random.Random(seed)

        # Optional zum Hinterlegen von fixen Stacks bei Tests
        self.initial_main_stack = main_stack
        self.initial_task_stack = task_stack

# Erstellen der Stapel Landschafts+Sonderplättchen, Auftragsplättchen, Tempelplättchen

    def _build_stacks(self):
        landscape_tiles = []
        special_tiles = []
        task_tiles = []
        temple_tiles = []

        for tile_id, tile in TILES.items():
            if tile.tile_group == tt.TileGroup.Landschaft:
                landscape_tiles.append(tile_id)
            elif tile.tile_group == tt.TileGroup.Sonder:
                special_tiles.append(tile_id)
            elif tile.tile_group == tt.TileGroup.Auftrag:
                task_tiles.append(tile_id)
            elif tile.tile_group == tt.TileGroup.Tempel:
                temple_tiles.append(tile_id)

        self.rng.shuffle(landscape_tiles)
        self.rng.shuffle(special_tiles)
        self.rng.shuffle(task_tiles)
        self.rng.shuffle(temple_tiles)

        # 3 verdeckte Landschaftsplättchen für den Tempelbereich
        temple_hidden_stack = []
        for _ in range(min(3, len(landscape_tiles))):
            temple_hidden_stack.append(landscape_tiles.pop())

        # Restliche Landschaft + Sonder in einen gemeinsamen Stack
        main_stack = landscape_tiles + special_tiles
        self.rng.shuffle(main_stack)

        # keine Veränderung der Task-Tiles zum Task-Stack
        task_stack = task_tiles

        return main_stack, task_stack, temple_tiles, temple_hidden_stack

    def _build_task_marker_stack(self) -> list[tasks.TaskMarker]:
        markers = []
        for task_type in (
            tt.TaskType.Sakura,
            tt.TaskType.Reis,
            tt.TaskType.Dorf,
            tt.TaskType.Strasse,
            tt.TaskType.Fluss,
            tt.TaskType.Rundum,
        ):
            for target in (4, 4, 5, 5, 6, 6):
                markers.append(tasks.TaskMarker(
                    task_type=task_type,
                    target=target,
                    points=target
                ))

        self.rng.shuffle(markers)
        return markers

#########################################
# Zug Logik: Phase > action.kind > choice
#########################################

# Phase: place_tile -> action.kind = store_tile, place_tile, illegal

    def step(self, s: State, action: Action):
        if s.phase == "choose_next_tile_source":
            return self._step_choose_next_tile_source(s, action)

        if s.phase == "place_tile":
            return self._step_place_tile(s, action)

        return self._illegal_action_result(s, action)

    def _step_place_tile(self, s: State, action: Action):
        if s.current_tile is None:
            return self._illegal_action_result(s, action)

        tile_id = s.current_tile
        tile = TILES[tile_id]

        # -------------------------------------------------
        # Fall A: aktuelles Tile in Lagerhaus / Kontor parken
        # -------------------------------------------------
        if action.kind == "store_tile":
            if action.choice is None:
                return self._illegal_action_result(s, action)

            stored_in = None

            # Landschaftsplättchen: Lagerhaus ODER Kontor
            if tile.tile_group == tt.TileGroup.Landschaft:
                if action.choice == "storehouse":
                    if s.storehouse_tile is not None:
                        return self._illegal_action_result(s, action)
                    s.storehouse_tile = tile_id
                    stored_in = "storehouse"

                elif action.choice == "kontor":
                    if s.kontor_tile is not None:
                        return self._illegal_action_result(s, action)
                    s.kontor_tile = tile_id
                    stored_in = "kontor"

                else:
                    return self._illegal_action_result(s, action)

            # Sonderplättchen: nur Kontor
            elif tile.tile_group == tt.TileGroup.Sonder:
                if action.choice != "kontor":
                    return self._illegal_action_result(s, action)
                if s.kontor_tile is not None:
                    return self._illegal_action_result(s, action)
                s.kontor_tile = tile_id
                stored_in = "kontor"

            # Andere TileGroups dürfen nicht geparkt werden
            else:
                return self._illegal_action_result(s, action)

            # aktuelles Tile ist jetzt weggeparkt
            s.current_tile = None

            # nächsten Schritt vorbereiten
            self._advance_after_turn(s)

            next_actions = self.legal_actions(s)
            done = len(next_actions) == 0

            info = StepInfo(
                last_action=action,
                stored_tile=tile_id,
                stored_in=stored_in,
                next_tile=s.current_tile,
                next_phase=s.phase,
                n_legal_next=len(next_actions),
            )
            return s, 0, done, info

        # -------------------------------------------------
        # Fall B: normales Platzieren eines Tiles
        # -------------------------------------------------
        if action.kind == "place_tile":
            if action.pos is None or action.rot is None:
                return self._illegal_action_result(s, action)

            pos = action.pos
            rot = action.rot

            if not is_legal_placement(s, pos, tile_id, rot):
                return self._illegal_action_result(s, action)

            # Tile auf das Board legen
            s.place_tile(pos, tile_id, rot)

            # DSU / Features aktualisieren
            update_all_dsus_after_place(s, pos)
            update_neighbor_dsus_after_place(s, pos)

            # Falls Auftragsplättchen: passenden Marker ziehen und aktivieren
            if tile.tile_group == tt.TileGroup.Auftrag and tile.task_type is not None:
                marker = self._draw_task_marker(s, tile.task_type)
                if marker is not None:
                    s.active_tasks.append(
                        tasks.ActiveTask(
                            pos=pos,
                            task_type=tile.task_type,
                            marker=marker,
                        )
                    )

            # Aktive, geschaffte, verlorene Aufträge nach jedem Zug aktualisieren
            newly_completed, newly_failed = self.update_active_tasks(s)

            # aktuelles Tile ist verbraucht
            s.current_tile = None

            # nächsten Schritt vorbereiten
            self._advance_after_turn(s)

            next_actions = self.legal_actions(s)
            done = len(next_actions) == 0

            info = StepInfo(
                last_action=action,
                placed_tile=tile_id,
                placed_pos=pos,
                placed_rot=rot,
                chosen_source="main",
                newly_completed_tasks=newly_completed,
                newly_failed_tasks=newly_failed,
                next_tile=s.current_tile,
                next_phase=s.phase,
                n_legal_next=len(next_actions),
            )
            return s, 0, done, info

        # -------------------------------------------------
        # Fall C: alles andere ist in dieser Phase illegal
        # -------------------------------------------------
        return self._illegal_action_result(s, action)

    def _step_choose_next_tile_source(self, s: State, action: Action):
        if action.kind != "choose_source":
            return self._illegal_action_result(s, action)

        chosen_source = None
        drawn_tile = None

        if action.choice == "storehouse":
            if s.storehouse_tile is None:
                return self._illegal_action_result(s, action)
            drawn_tile = s.storehouse_tile
            s.current_tile = s.storehouse_tile
            s.storehouse_tile = None
            chosen_source = "storehouse"
            s.phase = "place_tile"

        elif action.choice == "kontor":
            if s.kontor_tile is None:
                return self._illegal_action_result(s, action)
            drawn_tile = s.kontor_tile
            s.current_tile = s.kontor_tile
            s.kontor_tile = None
            chosen_source = "kontor"
            s.phase = "place_tile"

        elif action.choice == "main":
            chosen_source = "main"
            self._draw_main_tile(s)
            drawn_tile = s.current_tile

        elif action.choice == "task":
            if not self._should_offer_task_tile(s):
                return self._illegal_action_result(s, action)
            chosen_source = "task"
            self._draw_task_tile(s)
            drawn_tile = s.current_tile

        else:
            return self._illegal_action_result(s, action)

        next_actions = self.legal_actions(s)
        done = len(next_actions) == 0

        info = StepInfo(
            last_action=action,
            chosen_source=chosen_source,
            drawn_tile=drawn_tile,
            next_tile=s.current_tile,
            next_phase=s.phase,
            n_legal_next=len(next_actions)
        )
        return s, 0, done, info

# Legale Aktionen

    def legal_actions(self, s: State) -> list[Action]:
        if s.phase == "choose_next_tile_source":
            actions = []

            if s.storehouse_tile is not None:
                actions.append(Action(kind="choose_source", choice="storehouse"))
            if s.kontor_tile is not None:
                actions.append(Action(kind="choose_source", choice="kontor"))

            if self._should_offer_task_tile(s):
                actions.append(Action(kind="choose_source", choice="task"))
            elif s.main_stack:
                actions.append(Action(kind="choose_source", choice="main"))

            return actions

        if s.phase == "place_tile":
            if s.current_tile is None:
                return []

            actions = []
            tile_id = s.current_tile
            tile = TILES[tile_id]
            is_landscape = tile.tile_group == tt.TileGroup.Landschaft
            is_sonder = tile.tile_group == tt.TileGroup.Sonder

            for pos, rot in legal_actions(s, tile_id):
                # jede mögliche Kombination aus (pos, rot) um Tile zu legen
                actions.append(Action(kind="place_tile", pos=pos, rot=rot))

                if not is_landscape:
                    continue

                if s.sackgasse_available:
                    road_eges = ROAD_EDGE_INDICES_BY_TILE_ROT[(tile_id,rot)]
                    for edge_idx in road_eges:
                        actions.append(
                            Action(
                                kind="place_tile",
                                pos=pos,
                                rot=rot,
                                edge_override_edge=edge_idx,
                                edge_override_from=tt.EdgeType.Strasse,
                                edge_override_to=tt.EdgeType.Wiese
                            )
                        )

                if s.staudamm_available:
                    road_eges = RIVER_EDGE_INDICES_BY_TILE_ROT[(tile_id,rot)]
                    for edge_idx in road_eges:
                        actions.append(
                            Action(
                                kind="place_tile",
                                pos=pos,
                                rot=rot,
                                edge_override_edge=edge_idx,
                                edge_override_from=tt.EdgeType.Fluss,
                                edge_override_to=tt.EdgeType.Wiese
                            )
                        )

            # Möglichkeiten das Landschaftsplättchen ins Warenhaus oder Kontor zu legen
            if is_landscape:
                if s.storehouse_tile is None:
                    actions.append(Action(kind="store_tile", choice="storehouse"))
                if s.kontor_tile is None:
                    actions.append(Action(kind="store_tile", choice="kontor"))

            # zusätzliche Möglichkeit das Sonderplättchen ins Kontor zu legen
            if is_sonder:
                if s.kontor_tile is None:
                    actions.append(Action(kind="store_tile", choice="kontor"))

            return actions

    def _advance_after_turn(self, s: State) -> None:
        """
        Bereitet den nächsten Schritt nach einem abgeschlossenen Zug vor.

        Wenn ein Tile in Lagerhaus/Kontor liegt, gibt es immer eine Quellenwahl:
        gespeichertes Tile aus Lagerhaus/Kontor ODER normales nächstes Tile (Task/Main je nach Spielsituation)
        """
        has_stored_tile = (s.storehouse_tile is not None) or (s.kontor_tile is not None)

        # Falls Tile stored, dann immer die Wahl zwischen Landschafts-/Auftrags-Plättchen ziehen oder
        # stored_tile nehmen
        if has_stored_tile:
            s.current_tile = None
            s.phase = "choose_next_tile_source"

        # Falls kein Tile stored in Lagerhaus oder Kontor
        if self._should_offer_task_tile(s):
            self._draw_task_tile(s)
            return

        self._draw_main_tile(s)

# Auftragsplättchen Logik

    def _number_of_tasks_active(self, s:State) -> int:
        return 3 + self._fujiyama_task_solved(s)

    def _should_offer_task_tile(self, s: State) -> bool:
        return len(s.active_tasks) < self._number_of_tasks_active(s) and s.task_stack

    def _draw_task_tile(self, s: State) -> None:
        if s.task_stack:
            s.current_tile = s.task_stack.pop()
        else:
            s.current_tile = None
        s.phase = "place_tile"

    def _draw_task_marker(self, s: State, task_type: tt.TaskType) -> tasks.TaskMarker | None:
        for i, marker in enumerate(s.task_marker_stack):
            if marker.task_type == task_type:
                return s.task_marker_stack.pop(i)
        return None

    def update_active_tasks(self, s: State):
        still_active = []
        newly_completed = []
        newly_failed = []

        for active in s.active_tasks:
            status = self._task_status(s, active)
            if status == "fulfilled":
                s.completed_task_markers.append(active.marker)
                newly_completed.append(active.marker)
            elif status == "failed":
                s.failed_task_markers.append(active.marker)
                newly_failed.append(active.marker)
            else:
                still_active.append(active)

        s.active_tasks = still_active
        return newly_completed, newly_failed

    def _task_status(self, s: State, active: tasks.ActiveTask) -> str:
        t = active.task_type
        target = active.marker.target

        if t == tt.TaskType.Rundum:
            count = 0
            for side in range(6):
                if tt.neighbor(active.pos, side) in s.board:
                    count += 1

            if count == target:
                return "fulfilled"
            if count > target:
                return "failed"
            return "active"

        edge_type = tasks.TASK_TO_EDGE[t]
        dsu = s.feature_dsu[edge_type]

        if active.pos not in dsu.parent:
            return "active"

        root = dsu.find(active.pos)
        size = dsu.size[root]

        if size == target:
            return "fulfilled"
        if size > target:
            return "failed"
        return "active"

# Landschaftsplättchen Logik

    def _draw_main_tile(self, s: State) -> None:
        if s.main_stack:
            s.current_tile = s.main_stack.pop()
        else:
            s.current_tile = None
        s.phase = "place_tile"

    def _result_after_state_change(self, s: State):
        actions = self.legal_actions(s)
        done = len(actions) == 0
        info = StepInfo(
            placed_tile=-1,
            placed_pos=(0, 0),
            placed_rot=0,
            next_tile=s.current_tile,
            n_legal_next=len(actions),
        )
        return s, 0, done, info

    def _illegal_action_result(self, s: State, action: Action):
        return s, -1, True, StepInfo(
            last_action=action,
            next_tile=s.current_tile,
            next_phase=s.phase,
            n_legal_next=0,
        )

    def reset(self, seed: Optional[int] = None) -> State:
        if seed is not None:
            self.rng.seed(seed)

        s = State()

        if self.initial_main_stack is not None:
            s.main_stack = list(self.initial_main_stack)
            s.task_stack = list(self.initial_task_stack or [])
            s.temple_tiles = []
            s.temple_hidden_stack = []

        else:
            main_stack, task_stack, temple_tiles, temple_hidden_stack = self._build_stacks()
            s.main_stack = main_stack
            s.task_stack = task_stack
            s.temple_tiles = temple_tiles
            s.temple_hidden_stack = temple_hidden_stack

        s.task_marker_stack = self._build_task_marker_stack()

        self._advance_after_turn(s)
        return s

    ############################################
    ############ Sonderkarten Logik ############
    ############################################

    ##### Fujiyama abgeschlossen #####
    def _fujiyama_task_solved(self, s: State) -> bool:
        dsu = s.feature_dsu[tt.EdgeType.Vulkan]

        for root in dsu.parent:
            if dsu.find(root) == root and dsu.closed.get(root, False):
                return True

        return False

    ##### Staudamm und Sackgasse #####

    def _append_edge_override_actions(
            self,
            actions: list[Action],
            pos: tt.Pos,
            rot: int,
            edges: tuple[tt.EdgeType, ...],
            has_strasse: bool,
            has_fluss: bool,
    ) -> None:
        if has_strasse:
            for edge_idx, edge_type in enumerate(edges):
                if edge_type == tt.EdgeType.Strasse:
                    actions.append(
                        Action(
                            kind="place_tile",
                            pos=pos,
                            rot=rot,
                            edge_override_edge=edge_idx,
                            edge_override_from=tt.EdgeType.Strasse,
                            edge_override_to=tt.EdgeType.Wiese,
                        )
                    )

        if has_fluss:
            for edge_idx, edge_type in enumerate(edges):
                if edge_type == tt.EdgeType.Fluss:
                    actions.append(
                        Action(
                            kind="place_tile",
                            pos=pos,
                            rot=rot,
                            edge_override_edge=edge_idx,
                            edge_override_from=tt.EdgeType.Fluss,
                            edge_override_to=tt.EdgeType.Wiese,
                        )
                    )