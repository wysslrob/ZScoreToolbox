"""Z-score calculation logic."""

import numpy as np


def compute_zscore(y_mean: float, y_plus1sd: float, y_minus1sd: float, y_point: float) -> float:
    """Calculate a Z-score from four pixel y-coordinates.

    The scale is derived from the vertical distance between Mean and +/-1 SD marks.
    Raises ValueError if the SD marks are too close together to be meaningful.
    """
    sd_pixels = ((y_mean - y_plus1sd) + (y_minus1sd - y_mean)) / 2
    if abs(sd_pixels) < 0.5:
        raise ValueError(
            "Mean and +/-1 SD are too close together.\n"
            "Please place the points further apart."
        )
    return round((y_mean - y_point) / sd_pixels, 3)


def compute_zscore_from_points(
    y_values: list[float],
) -> tuple[float, float, float]:
    """Calculate Z-score from a list of Y pixel coordinates.

    Returns (z_score, mean_y, sd_y).
    Raises ValueError if fewer than 10 points or SD is near zero.
    """
    if len(y_values) < 10:
        raise ValueError("Draw a longer line — not enough data points.")
    arr = np.array(y_values, dtype=float)
    mean_y = float(np.mean(arr))
    sd_y = float(np.std(arr))
    if sd_y < 0.5:
        raise ValueError("The drawn line is too flat to calculate SD.")
    last_y = y_values[-1]
    z = (mean_y - last_y) / sd_y
    return round(z, 3), round(mean_y, 1), round(sd_y, 1)
