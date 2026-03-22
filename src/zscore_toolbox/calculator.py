"""Z-score calculation logic."""


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
