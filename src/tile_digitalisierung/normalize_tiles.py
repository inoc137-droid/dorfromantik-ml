from __future__ import annotations

import argparse
from pathlib import Path
from typing import Tuple

import numpy as np
from PIL import Image


def load_rgba(path: Path) -> np.ndarray:
    """Load image as RGBA uint8 numpy array."""
    img = Image.open(path).convert("RGBA")
    return np.array(img, dtype=np.uint8)


def save_rgba(arr: np.ndarray, path: Path) -> None:
    """Save RGBA uint8 numpy array as PNG."""
    img = Image.fromarray(arr, mode="RGBA")
    img.save(path)


def get_opaque_mask(rgba: np.ndarray, alpha_threshold: int = 1) -> np.ndarray:
    """Return boolean mask for visible pixels."""
    alpha = rgba[:, :, 3]
    return alpha >= alpha_threshold


def percentile_stretch_rgb(
    rgba: np.ndarray,
    mask: np.ndarray,
    low_pct: float = 1.0,
    high_pct: float = 99.0,
) -> np.ndarray:
    """
    Robustly stretch RGB intensities using percentiles computed only on opaque pixels.
    Alpha channel is preserved.
    """
    result = rgba.copy().astype(np.float32)

    if not np.any(mask):
        return rgba.copy()

    for c in range(3):
        channel = result[:, :, c]
        values = channel[mask]

        lo = np.percentile(values, low_pct)
        hi = np.percentile(values, high_pct)

        if hi <= lo:
            continue

        stretched = (channel - lo) * (255.0 / (hi - lo))
        stretched = np.clip(stretched, 0, 255)
        result[:, :, c] = stretched

    return result.astype(np.uint8)


def build_histogram_mapping(src_values: np.ndarray, ref_values: np.ndarray) -> np.ndarray:
    """
    Build a 256-entry lookup table mapping src intensities to ref intensities
    using cumulative histograms.
    """
    src_hist = np.bincount(src_values, minlength=256).astype(np.float64)
    ref_hist = np.bincount(ref_values, minlength=256).astype(np.float64)

    src_cdf = np.cumsum(src_hist)
    ref_cdf = np.cumsum(ref_hist)

    if src_cdf[-1] == 0 or ref_cdf[-1] == 0:
        return np.arange(256, dtype=np.uint8)

    src_cdf /= src_cdf[-1]
    ref_cdf /= ref_cdf[-1]

    mapping = np.zeros(256, dtype=np.uint8)

    ref_idx = 0
    for src_idx in range(256):
        while ref_idx < 255 and ref_cdf[ref_idx] < src_cdf[src_idx]:
            ref_idx += 1
        mapping[src_idx] = ref_idx

    return mapping


def masked_histogram_match_rgb(
    src_rgba: np.ndarray,
    ref_rgba: np.ndarray,
    src_mask: np.ndarray,
    ref_mask: np.ndarray,
) -> np.ndarray:
    """
    Histogram-match RGB channels of src to ref using only opaque pixels.
    Alpha channel is preserved.
    """
    out = src_rgba.copy()

    if not np.any(src_mask) or not np.any(ref_mask):
        return out

    for c in range(3):
        src_values = src_rgba[:, :, c][src_mask]
        ref_values = ref_rgba[:, :, c][ref_mask]

        lut = build_histogram_mapping(src_values, ref_values)

        matched_channel = out[:, :, c]
        matched_channel[src_mask] = lut[matched_channel[src_mask]]
        out[:, :, c] = matched_channel

    return out


def apply_alpha_cleanup(rgba: np.ndarray, alpha_threshold: int = 1) -> np.ndarray:
    """
    Ensure fully transparent pixels have RGB=0 to avoid dirty edges.
    """
    out = rgba.copy()
    transparent = out[:, :, 3] < alpha_threshold
    out[transparent, 0:3] = 0
    return out


def resize_if_needed(rgba: np.ndarray, target_size: Tuple[int, int]) -> np.ndarray:
    """
    Resize image to target size if needed. Uses high-quality down/up sampling.
    """
    h, w = rgba.shape[:2]
    target_w, target_h = target_size
    if (w, h) == (target_w, target_h):
        return rgba

    img = Image.fromarray(rgba, mode="RGBA")
    img = img.resize((target_w, target_h), resample=Image.Resampling.LANCZOS)
    return np.array(img, dtype=np.uint8)


def process_image(
    src_path: Path,
    out_path: Path,
    ref_rgba: np.ndarray,
    ref_mask: np.ndarray,
    target_size: Tuple[int, int],
    normalize_first: bool = True,
) -> None:
    rgba = load_rgba(src_path)
    rgba = resize_if_needed(rgba, target_size)
    mask = get_opaque_mask(rgba)

    # Step 1: robust brightness/contrast normalization
    if normalize_first:
        rgba = percentile_stretch_rgb(rgba, mask, low_pct=1.0, high_pct=99.0)

    # Step 2: match color distribution to reference
    rgba = masked_histogram_match_rgb(rgba, ref_rgba, mask, ref_mask)

    # Cleanup transparent edge pixels
    rgba = apply_alpha_cleanup(rgba)

    save_rgba(rgba, out_path)


def collect_images(input_dir: Path) -> list[Path]:
    exts = {".png", ".PNG"}
    return sorted([p for p in input_dir.iterdir() if p.suffix in exts and p.is_file()])


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Normalize and color-match aligned hex tile PNGs."
    )
    parser.add_argument("--input-dir", required=True, help="Folder with aligned PNG files")
    parser.add_argument("--output-dir", required=True, help="Folder for processed PNG files")
    parser.add_argument(
        "--reference",
        required=True,
        help="Reference PNG used as the color target",
    )
    parser.add_argument(
        "--skip-reference-copy",
        action="store_true",
        help="Do not copy the reference file unchanged into the output folder",
    )
    parser.add_argument(
        "--no-normalize",
        action="store_true",
        help="Disable the initial brightness/contrast normalization step",
    )

    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    reference_path = Path(args.reference)

    output_dir.mkdir(parents=True, exist_ok=True)

    ref_rgba = load_rgba(reference_path)
    ref_mask = get_opaque_mask(ref_rgba)
    ref_h, ref_w = ref_rgba.shape[:2]
    target_size = (ref_w, ref_h)

    images = collect_images(input_dir)

    if not images:
        raise SystemExit(f"Keine PNG-Dateien in {input_dir} gefunden.")

    for src_path in images:
        out_path = output_dir / src_path.name

        if src_path.resolve() == reference_path.resolve():
            if not args.skip_reference_copy:
                save_rgba(ref_rgba, out_path)
            print(f"[REF] {src_path.name}")
            continue

        process_image(
            src_path=src_path,
            out_path=out_path,
            ref_rgba=ref_rgba,
            ref_mask=ref_mask,
            target_size=target_size,
            normalize_first=not args.no_normalize,
        )
        print(f"[OK]  {src_path.name} -> {out_path.name}")

    print("Fertig.")


if __name__ == "__main__":
    main()