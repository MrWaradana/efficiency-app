def calculate_gap(target, current) -> float:
    if target is not None and current is not None:
        return current - target
    return 0


def calculate_persen_losses(gap, deviasi, persen_hr):
    if deviasi == 0 or None:
        raise Exception("deviasi cannot be 0")

    if gap is None and persen_hr is None:
        return 0

    result = (gap / deviasi) * persen_hr
    normalize_result = (100 * result) / 100

    return abs(result)
