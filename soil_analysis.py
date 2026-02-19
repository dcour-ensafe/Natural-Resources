from __future__ import annotations

import csv
import io
from dataclasses import dataclass
from pathlib import Path
from typing import List

import numpy as np
from PIL import Image


@dataclass
class ColorCluster:
    rgb: np.ndarray
    percentage: float
    munsell: str


def load_image_rgb(file_bytes: bytes) -> np.ndarray:
    image = Image.open(io.BytesIO(file_bytes))
    rgb = image.convert("RGB")
    return np.asarray(rgb, dtype=np.uint8)


def rgb_to_hsv_array(rgb: np.ndarray) -> np.ndarray:
    arr = rgb.astype(np.float32) / 255.0
    r, g, b = arr[..., 0], arr[..., 1], arr[..., 2]

    cmax = np.max(arr, axis=-1)
    cmin = np.min(arr, axis=-1)
    delta = cmax - cmin

    h = np.zeros_like(cmax)
    mask = delta != 0

    r_mask = (cmax == r) & mask
    g_mask = (cmax == g) & mask
    b_mask = (cmax == b) & mask

    h[r_mask] = ((g[r_mask] - b[r_mask]) / delta[r_mask]) % 6
    h[g_mask] = ((b[g_mask] - r[g_mask]) / delta[g_mask]) + 2
    h[b_mask] = ((r[b_mask] - g[b_mask]) / delta[b_mask]) + 4
    h = h / 6.0

    s = np.where(cmax == 0, 0, delta / cmax)
    v = cmax

    return np.stack([h, s, v], axis=-1)


def detect_soil_mask(rgb: np.ndarray) -> np.ndarray:
    hsv = rgb_to_hsv_array(rgb)
    h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]

    # Broad earthy hue + neutral tone fallback for low saturation soil grays.
    earthy_hue = ((h >= 0.03) & (h <= 0.16) & (s >= 0.15) & (v >= 0.12) & (v <= 0.95))
    neutral_soil = (s <= 0.2) & (v >= 0.1) & (v <= 0.85)

    soil_mask = earthy_hue | neutral_soil
    return soil_mask


def _kmeans(points: np.ndarray, k: int, iterations: int = 15) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(42)
    if len(points) < k:
        k = max(1, len(points))

    indices = rng.choice(len(points), size=k, replace=False)
    centroids = points[indices].astype(np.float32)

    for _ in range(iterations):
        distances = np.sum((points[:, None, :] - centroids[None, :, :]) ** 2, axis=2)
        labels = np.argmin(distances, axis=1)

        new_centroids = centroids.copy()
        for i in range(k):
            members = points[labels == i]
            if len(members) > 0:
                new_centroids[i] = members.mean(axis=0)

        if np.allclose(new_centroids, centroids, atol=1.0):
            centroids = new_centroids
            break
        centroids = new_centroids

    distances = np.sum((points[:, None, :] - centroids[None, :, :]) ** 2, axis=2)
    labels = np.argmin(distances, axis=1)
    return centroids, labels


def _load_munsell_palette(path: str | Path = "data/munsell_palette.csv") -> tuple[np.ndarray, List[str]]:
    chips = []
    labels = []
    with open(path, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            notation = row["notation"]
            hex_value = row["hex"].strip("#")
            rgb = np.array(
                [int(hex_value[i : i + 2], 16) for i in (0, 2, 4)],
                dtype=np.float32,
            )
            chips.append(rgb)
            labels.append(notation)
    return np.vstack(chips), labels


def nearest_munsell(rgb: np.ndarray, chips: np.ndarray, labels: List[str]) -> str:
    distances = np.sum((chips - rgb[None, :]) ** 2, axis=1)
    idx = int(np.argmin(distances))
    return labels[idx]


def analyze_soil_image(rgb: np.ndarray, clusters: int = 3) -> dict:
    soil_mask = detect_soil_mask(rgb)
    soil_pixels = rgb[soil_mask]

    if len(soil_pixels) < 50:
        raise ValueError("Not enough probable soil pixels found. Please upload a clearer soil photo.")

    centroids, labels = _kmeans(soil_pixels.astype(np.float32), k=clusters)
    chips, chip_labels = _load_munsell_palette()

    results = []
    total = len(soil_pixels)
    for idx, centroid in enumerate(centroids):
        pct = float(np.sum(labels == idx) / total * 100)
        if pct < 2:
            continue
        munsell = nearest_munsell(centroid, chips, chip_labels)
        results.append(
            ColorCluster(
                rgb=centroid,
                percentage=round(pct, 1),
                munsell=munsell,
            )
        )

    results.sort(key=lambda c: c.percentage, reverse=True)
    matrix = results[0]
    secondary = results[1:]

    return {
        "matrix": matrix,
        "secondary_features": secondary,
        "soil_coverage_percent": round(float(np.mean(soil_mask) * 100), 1),
        "soil_mask": soil_mask,
    }
