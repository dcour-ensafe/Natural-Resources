import numpy as np

from cli import _rgb_to_hex


def test_rgb_to_hex_roundtrip_style_values():
    rgb = np.array([138.7, 116.2, 89.9], dtype=np.float32)
    assert _rgb_to_hex(rgb) == "#8a7459"
