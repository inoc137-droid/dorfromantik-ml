from dataclasses import dataclass
import dorfromantik.tile_types as tt

@dataclass(frozen=True)
class TaskMarker:
    task_type: tt.TaskType
    target: int          # 4 / 5 / 6
    points: int          # erstmal identisch zu target

@dataclass
class ActiveTask:
    pos: tt.Pos
    task_type: tt.TaskType
    marker: TaskMarker

TASK_TO_EDGE = {
    tt.TaskType.Sakura: tt.EdgeType.Sakura,
    tt.TaskType.Reis: tt.EdgeType.Reis,
    tt.TaskType.Dorf: tt.EdgeType.Dorf,
    tt.TaskType.Strasse: tt.EdgeType.Strasse,
    tt.TaskType.Fluss: tt.EdgeType.Fluss,
}