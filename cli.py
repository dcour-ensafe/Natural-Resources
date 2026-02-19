from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from soil_analysis import analyze_soil_image, load_image_rgb


def _rgb_to_hex(rgb: np.ndarray) -> str:
    rgb_int = np.clip(rgb, 0, 255).astype(int)
    return "#%02x%02x%02x" % tuple(rgb_int.tolist())


def analyze_image_path(image_path: str | Path) -> dict:
    path = Path(image_path)
    if not path.exists():
        raise FileNotFoundError(f"Image file not found: {path}")

    rgb = load_image_rgb(path.read_bytes())
    result = analyze_soil_image(rgb)

    matrix = result["matrix"]
    secondary = result["secondary_features"]

    return {
        "image": str(path),
        "soil_coverage_percent": result["soil_coverage_percent"],
        "matrix": {
            "munsell": matrix.munsell,
            "percentage": matrix.percentage,
            "representative_hex": _rgb_to_hex(matrix.rgb),
        },
        "secondary_features": [
            {
                "munsell": feature.munsell,
                "percentage": feature.percentage,
                "representative_hex": _rgb_to_hex(feature.rgb),
            }
            for feature in secondary
        ],
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Analyze a soil photo and estimate matrix + secondary feature color percentages "
            "using a prototype Munsell matching workflow."
        )
    )
    parser.add_argument("image", help="Path to the soil image file (jpg, png, etc.).")
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Print pretty-formatted JSON output.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        output = analyze_image_path(args.image)
    except Exception as exc:  # pragma: no cover - top-level CLI error handling
        parser.error(str(exc))
        return 2

    if args.pretty:
        print(json.dumps(output, indent=2))
    else:
        print(json.dumps(output))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
