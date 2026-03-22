"""Z-score calculation logic."""

import numpy as np


def compute_zscore(
    y_mean: float,
    y_plus1sd: float,
    y_minus1sd: float,
    y_point: float,
    y_plus2sd: float | None = None,
    y_minus2sd: float | None = None,
) -> float:
    """Calculate a Z-score from pixel y-coordinates.

    The scale is derived from the vertical distance between Mean and SD marks.
    If +/-2 SD values are provided, all available SD distances are averaged
    for a more accurate SD pixel calculation.
    Raises ValueError if the SD marks are too close together to be meaningful.
    """
    sd_estimates: list[float] = [
        y_mean - y_plus1sd,   # 1 SD above mean
        y_minus1sd - y_mean,  # 1 SD below mean
    ]
    if y_plus2sd is not None:
        sd_estimates.append((y_mean - y_plus2sd) / 2)  # 2 SD above → per-SD
    if y_minus2sd is not None:
        sd_estimates.append((y_minus2sd - y_mean) / 2)  # 2 SD below → per-SD

    sd_pixels = sum(sd_estimates) / len(sd_estimates)
    if abs(sd_pixels) < 0.5:
        raise ValueError(
            "Mean and SD marks are too close together.\n"
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
