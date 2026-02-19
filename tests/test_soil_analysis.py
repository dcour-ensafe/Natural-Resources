import numpy as np

from soil_analysis import analyze_soil_image, nearest_munsell


def test_nearest_munsell_exact_match():
    chips = np.array([[100, 90, 80], [50, 50, 50]], dtype=np.float32)
    labels = ["10YR 5/3", "N 4/"]
    assert nearest_munsell(np.array([100, 90, 80], dtype=np.float32), chips, labels) == "10YR 5/3"


def test_analyze_image_matrix_and_secondary():
    # 80% matrix-like brown, 20% gray mottles
    matrix = np.full((80, 10, 3), [155, 130, 100], dtype=np.uint8)
    mottles = np.full((20, 10, 3), [120, 120, 120], dtype=np.uint8)
    img = np.vstack([matrix, mottles])

    result = analyze_soil_image(img, clusters=2)

    assert result["matrix"].percentage > 70
    assert result["soil_coverage_percent"] > 90
    if result["secondary_features"]:
        assert result["secondary_features"][0].percentage < result["matrix"].percentage
