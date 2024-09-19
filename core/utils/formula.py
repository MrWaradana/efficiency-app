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

    return abs(result)


def calculate_pareto(target_data, current_data):
    gap = calculate_gap(target_data.nilai, current_data.nilai)
    persen_losses = calculate_persen_losses(
        gap, target_data.deviasi, current_data.persen_hr
    )
    nilai_losses = (persen_losses / 100) * 1000

    return gap, persen_losses, nilai_losses


def calculate_cost_benefit(netto, heatRate, nilai_losses):
    cost_benefit = nilai_losses * (netto * heatRate)
    return cost_benefit
