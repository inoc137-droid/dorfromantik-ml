from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Tuple, Any

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

plt.ion()


# ============================================================
# Konfiguration
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
TILE_DIR = BASE_DIR / "original_render"

# Hintergrund transparent oder weiß
TRANSPARENT_BACKGROUND = False

# Rand um das gesamte Bild
PADDING = 30

# Zusätzliche Beschriftung der Koordinaten im Plot
SHOW_COORD_LABELS = False

# Speichern der Vorschau
SAVE_OUTPUT = False
OUTPUT_FILE = BASE_DIR / "board_render.png"


# ============================================================
# Optional: einfache Testklasse
# Wenn du schon eine eigene PlacedTile-Klasse hast, kannst du
# diesen Block ignorieren / löschen.
# ============================================================

@dataclass
class PlacedTile:
    tile_id: int
    rot: int


# ============================================================
# Hilfsfunktionen
# ============================================================

def tile_id_to_filename(tile_id: int) -> str:
    """tile_id=0 -> tile_000.png"""
    return f"tile_{tile_id:03d}.png"


def load_rgba(path: Path) -> Image.Image:
    return Image.open(path).convert("RGBA")


def get_opaque_bbox(img: Image.Image) -> Tuple[int, int, int, int]:
    """
    Bounding Box der sichtbaren Pixel anhand des Alpha-Kanals.
    Rückgabe: (left, top, right, bottom), right/bottom exklusiv
    """
    alpha = img.getchannel("A")
    bbox = alpha.getbbox()
    if bbox is None:
        raise ValueError("Bild enthält keine sichtbaren Pixel.")
    return bbox


def get_tile_radius_from_image(img: Image.Image) -> float:
    """
    Bestimmt den Hex-Radius R aus der sichtbaren Breite.
    Für flat-top / Spitzen links-rechts gilt:
    sichtbare Hex-Breite = 2R
    """
    left, top, right, bottom = get_opaque_bbox(img)
    opaque_width = right - left
    return opaque_width / 2.0


def rotate_tile(img: Image.Image, rot: int) -> Image.Image:
    """
    Rotation in 60°-Schritten.
    rot=0..5, im Uhrzeigersinn.
    Pillow rotiert positiv gegen den Uhrzeigersinn,
    daher negatives Vorzeichen.
    """
    rot = rot % 6
    angle = -60 * rot
    return img.rotate(angle, resample=Image.Resampling.BICUBIC, expand=False)


def board_to_pixel(q: int, r: int, radius: float) -> Tuple[float, float]:
    """
    Mapping für dein Koordinatensystem:
      (0, 1) = nach oben
      (1, 0) = nach oben rechts

    Hexe sind flat-top / Spitzen links-rechts.

    Basisvektoren:
      e_r = (0, -sqrt(3) * R)              # nach oben
      e_q = (1.5 * R, -sqrt(3)/2 * R)      # nach oben rechts

    Daraus:
      x = 1.5 * R * q
      y = -sqrt(3) * R * (r + q/2)
    """
    x = 1.5 * radius * q
    y = -math.sqrt(3) * radius * (r + q / 2.0)
    return x, y


def alpha_composite_at(canvas: Image.Image, tile: Image.Image, x: int, y: int) -> None:
    """
    Tile an Position (x, y) auf Canvas legen.
    x, y sind Pixelkoordinaten der linken oberen Ecke.
    """
    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    layer.paste(tile, (x, y), tile)
    canvas.alpha_composite(layer)


def extract_tile_fields(placed_tile: Any) -> Tuple[int, int]:
    """
    Unterstützt Objekte mit .tile_id / .rot
    oder Dict-ähnliche Einträge mit ['tile_id'] / ['rot'].
    """
    if hasattr(placed_tile, "tile_id") and hasattr(placed_tile, "rot"):
        return int(placed_tile.tile_id), int(placed_tile.rot)

    if isinstance(placed_tile, dict):
        return int(placed_tile["tile_id"]), int(placed_tile["rot"])

    raise TypeError(
        "PlacedTile-Eintrag muss Attribute .tile_id und .rot haben "
        "oder ein Dict mit 'tile_id' und 'rot' sein."
    )


# ============================================================
# Rendering
# ============================================================

def render_board(board: Dict[Tuple[int, int], Any], tile_dir: Path = TILE_DIR) -> Image.Image:
    """
    Rendert das Board-Dictionary zu einem Pillow-Bild.

    board-Format:
      {
          (q, r): PlacedTile(tile_id=8, rot=0),
          ...
      }
    """
    if not board:
        raise ValueError("board ist leer.")

    # Ein erstes Tile laden, um Größe und Radius zu bestimmen
    first_pos, first_placed = next(iter(board.items()))
    first_tile_id, _ = extract_tile_fields(first_placed)

    first_path = tile_dir / tile_id_to_filename(first_tile_id)
    if not first_path.exists():
        raise FileNotFoundError(f"Tile-Datei nicht gefunden: {first_path}")

    first_img = load_rgba(first_path)
    img_w, img_h = first_img.size
    radius = get_tile_radius_from_image(first_img)

    # Mittelpunkte aller Tiles berechnen
    centers = []
    for (q, r), placed_tile in board.items():
        tile_id, rot = extract_tile_fields(placed_tile)
        cx, cy = board_to_pixel(q, r, radius)
        centers.append((q, r, tile_id, rot, cx, cy))

    # Canvas-Größe bestimmen
    half_w = img_w / 2.0
    half_h = img_h / 2.0

    min_x = min(cx - half_w for _, _, _, _, cx, cy in centers)
    max_x = max(cx + half_w for _, _, _, _, cx, cy in centers)
    min_y = min(cy - half_h for _, _, _, _, cx, cy in centers)
    max_y = max(cy + half_h for _, _, _, _, cx, cy in centers)

    canvas_w = int(math.ceil(max_x - min_x)) + 2 * PADDING
    canvas_h = int(math.ceil(max_y - min_y)) + 2 * PADDING

    bg = (255, 255, 255, 0) if TRANSPARENT_BACKGROUND else (90, 120, 120, 255)
    canvas = Image.new("RGBA", (canvas_w, canvas_h), bg)

    offset_x = -min_x + PADDING
    offset_y = -min_y + PADDING

    # Tiles zeichnen
    for q, r, tile_id, rot, cx, cy in centers:
        tile_path = tile_dir / tile_id_to_filename(tile_id)
        if not tile_path.exists():
            raise FileNotFoundError(f"Tile-Datei nicht gefunden: {tile_path}")

        tile = load_rgba(tile_path)
        tile = rotate_tile(tile, rot)

        paste_x = int(round(cx + offset_x - half_w))
        paste_y = int(round(cy + offset_y - half_h))
        alpha_composite_at(canvas, tile, paste_x, paste_y)

    return canvas


def show_board_image(
    img: Image.Image,
    board: Dict[Tuple[int, int], Any] | None = None,
    *,
    block: bool = True,
) -> None:
    arr = np.array(img)

    fig = plt.figure(1)
    fig.clf()

    manager = plt.get_current_fig_manager()
    if not hasattr(fig, "_window_prepared"):
        try:
            pass
            # manager.window.state("zoomed")
        except Exception:
            try:
                manager.full_screen_toggle()
            except Exception:
                try:
                    manager.resize(*manager.window.maxsize())
                except Exception:
                    pass
        fig._window_prepared = True

    ax = fig.add_subplot(111)
    ax.set_position([0, 0, 1, 1])
    ax.imshow(arr)

    h, w = arr.shape[:2]
    ax.set_xlim(0, w)
    ax.set_ylim(h, 0)
    ax.set_aspect("equal")
    ax.axis("off")

    if SHOW_COORD_LABELS and board:
        first_pos, first_placed = next(iter(board.items()))
        first_tile_id, _ = extract_tile_fields(first_placed)
        first_img = load_rgba(TILE_DIR / tile_id_to_filename(first_tile_id))
        img_w, img_h = first_img.size
        radius = get_tile_radius_from_image(first_img)
        half_w = img_w / 2.0
        half_h = img_h / 2.0

        centers = []
        for (q, r), placed_tile in board.items():
            cx, cy = board_to_pixel(q, r, radius)
            centers.append((q, r, cx, cy))

        min_x = min(cx - half_w for _, _, cx, cy in centers)
        min_y = min(cy - half_h for _, _, cx, cy in centers)
        offset_x = -min_x + PADDING
        offset_y = -min_y + PADDING

        for q, r, cx, cy in centers:
            px = cx + offset_x
            py = cy + offset_y
            ax.text(px, py, f"({q},{r})", ha="center", va="center")

    if block:
        plt.show(block=True)
    else:
        fig.canvas.draw_idle()
        plt.pause(0.001)


# ============================================================
# Beispielverwendung
# ============================================================

if __name__ == "__main__":
    # Beispielboard
    demo_board = {
        (0, 0): PlacedTile(tile_id=8, rot=0),
        (-1, 0): PlacedTile(tile_id=4, rot=2),
        (1, -1): PlacedTile(tile_id=2, rot=5),
        (0, 1): PlacedTile(tile_id=0, rot=4),
        (2, -1): PlacedTile(tile_id=3, rot=0),
    }

    render_and_show(demo_board)
