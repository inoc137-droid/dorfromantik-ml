from dataclasses import dataclass
from typing import Optional
from dorfromantik.action import Action
import dorfromantik.tile_types as tt


@dataclass(slots=True)
class StepInfo:
    last_action: Action

    # Was in diesem Schritt konkret passiert ist
    # wurde ein Tile gelegt?
    placed_tile: Optional[int] = None
    placed_pos: Optional[tt.Pos] = None
    placed_rot: Optional[int] = None

    # wurde ein Tile geparkt
    stored_tile: Optional[int] = None
    stored_in: Optional[str] = None          # "storehouse" / "kontor"

    chosen_source: Optional[str] = None      # "main" / "task" / "storehouse" / "kontor"
    drawn_tile: Optional[int] = None         # Tile, das durch die Quellenwahl/Draw aktiv wurde

    # wurde ein Tile verändert
    sackgasse_used: bool = False
    staudamm_used: bool = False
    altered_edge: Optional[int] = None

    # Task-Ereignisse dieses Schritts
    newly_completed_tasks: Optional[list] = None
    newly_failed_tasks: Optional[list] = None

    # Zustand nach dem Schritt
    next_tile: Optional[int] = None
    next_phase: Optional[str] = None
    n_legal_next: int = 0
