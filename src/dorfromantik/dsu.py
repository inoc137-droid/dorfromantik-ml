from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Set, Tuple, List

Pos = Tuple[int, int]
Side = int
HalfEdge = Tuple[Pos, Side]     # (tile_position, side_index 0..5)

@dataclass
class DSU:
    parent: Dict[Pos, Pos] = field(default_factory=dict)
    size: Dict[Pos, int] = field(default_factory=dict)
    members: Dict[Pos, Set[Pos]] = field(default_factory=dict)  # root -> set(Pos)
    open_edges: Dict[Pos, Set[HalfEdge]] = field(default_factory=dict)  # root -> set(HalfEdge)
    closed: Dict[Pos, bool] = field(default_factory=dict)  # root -> abgeschlossen?
    max_size: int = 0

    def add(self, x: Pos) -> None:
        if x in self.parent:
            return
        self.parent[x] = x
        self.size[x] = 1
        self.members[x] = {x}
        self.open_edges[x] = set()
        self.closed[x] = False
        if self.max_size < 1:
            self.max_size = 1

    def find(self, x: Pos) -> Pos:
        if x not in self.parent:
            raise KeyError(f"DSU.find called for unknown element {x}. Did you forget add()?")
        p = self.parent[x]
        if p != x:
            self.parent[x] = self.find(p)
        return self.parent[x]

    def union(self, a: Pos, b: Pos) -> Pos:
        self.add(a)
        self.add(b)
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return ra

        # union-by-size
        if self.size[ra] < self.size[rb]:
            ra, rb = rb, ra

        self.parent[rb] = ra
        self.size[ra] += self.size[rb]
        del self.size[rb]

        self.members[ra] |= self.members[rb]
        del self.members[rb]

        self.open_edges[ra] |= self.open_edges[rb]
        del self.open_edges[rb]

        # abgeschlossen nur, wenn beide abgeschlossen
        self.closed[ra] = self.closed[ra] and self.closed[rb]
        del self.closed[rb]

        if self.size[ra] > self.max_size:
            self.max_size = self.size[ra]

        return ra

    def refresh_closed(self, x: Pos) -> None:
        rx = self.find(x)
        self.closed[rx] = len(self.open_edges[rx]) == 0

    # --- Offene Kanten / Abgeschlossenheit Helper Funktionen ---

    def add_open_edge(self, x: Pos, side: Side) -> None:
        """(x, side): Fügt dem Root von x die Kante side als open_edge hinzu.
        Macht keine Überprüfung zum Kantentyp. Abfrage in update_dsu. """
        rx = self.find(x)
        self.open_edges[rx].add((x, side))
        self.closed[rx] = False

    def close_between(self, a: Pos, a_side: Side, b: Pos, b_side: Side) -> None:
        """
        (a, a_side, b, b_side): Entfernt die zwei HalfEdges a_side und b_side, die durch union nun innen liegen.
        Aufruf nach Union (oder union innen), robust in beiden Fällen.
        """
        r = self.union(a, b)
        self.open_edges[r].discard((a, a_side))
        self.open_edges[r].discard((b, b_side))
        self.closed[r] = len(self.open_edges[r]) == 0

    def is_closed(self, x: Pos) -> bool:
        """ (x) -> 0/1, ob zu gegebenem Tile an Stelle x, der Root offen oder abgeschlossen ist (also das Ganze Gebiet) """
        rx = self.find(x)
        return self.closed[rx]

    def open_edge_list(self) -> List[Set[HalfEdge]]:
        # Liste offener Kanten
        return list(self.open_edges.values())

    def open_edge_count(self, x: Pos) -> int:
        # Anzahl offener Kanten
        rx = self.find(x)
        return len(self.open_edges[rx])

    def components_list(self) -> List[Set[Pos]]:
        # returns list of member sets (each is a river/road)
        return list(self.members.values())
