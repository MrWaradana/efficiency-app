def calculate_gap(target, current):
    if target is not None and current is not None:
        return target - current
    return 0


def calculate_nilai_losses(gap, deviasi, persen_hr):
    if deviasi == 0 or None:
        raise Exception("deviasi cannot be 0")

    if gap is None and persen_hr is None:
        return 0

    result = (gap / deviasi) * persen_hr

    return abs(result)
