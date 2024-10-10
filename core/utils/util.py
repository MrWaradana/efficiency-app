from collections import defaultdict
import random
import aiohttp
import requests

from core.utils.formula import calculate_cost_benefit, calculate_gap, calculate_persen_losses


def fetch_data_from_api(url):
    """
    Fetch data from given API endpoint.

    Args:
    url (str): The API endpoint to fetch from.

    Returns:
    dict: The JSON response of the API endpoint.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
    except requests.exceptions.RequestException as e:
        # Handle any exceptions that occur
        print(f"An error occurred: {e}")
        return None

    if response.ok:
        return response.json()
    else:
        return None


async def fetch_variable_data(session, url, username, password):
    async with session.get(url, auth=aiohttp.BasicAuth(username, password), ssl=False) as response:
        if response.ok:
            json_response = await response.json()
            return json_response.get('Value')
        return "N/A"


def get_key_by_value(variable_mapping, value):

    for key, val in variable_mapping.items():

        variable_string = val["name"]

        if variable_string == value:
            return key
    return None


def modify_number(original_number: float, max_delta) -> float:
    """
    Modify a number by adding or subtracting a random delta value.

    :param original_number: The number to modify.
    :param max_delta: The maximum absolute value for the random delta.
    :return: The modified number.
    """
    sign = random.choice([-1, 1])

    # Generate a random delta value between 0 and max_delta
    delta = random.uniform(0, max_delta)

    # Apply the delta with the random sign
    new_number = original_number + (sign * delta)

    return float(new_number)


def process_single_data_pareto(nphr, variable_schema, data_tuple):
    """
    Process a single data point with all calculations
    """
    current_data, target_data, total_cost = data_tuple

    gap = calculate_gap(target_data.nilai, current_data.nilai)
    persen_losses = calculate_persen_losses(
        gap, target_data.deviasi, current_data.persen_hr
    )
    nilai_losses = (persen_losses / 100) * 1000
    netto = 1000
    cost_benefit = calculate_cost_benefit(netto, nphr, nilai_losses)

    return {
        "category": current_data.variable.category,
        "id": str(current_data.id),
        "variable": variable_schema.dump(current_data.variable),
        "existing_data": current_data.nilai,
        "reference_data": target_data.nilai,
        "deviasi": current_data.deviasi,
        "persen_hr": current_data.persen_hr,
        "persen_losses": persen_losses,
        "nilai_losses": nilai_losses,
        "cost_benefit": cost_benefit,
        "gap": gap,
        "total_biaya": total_cost,
        "symptoms": "Higher" if gap > 0 else "Lower",
        "has_cause": bool(current_data.variable.causes),
        "is_pareto": current_data.variable.is_pareto
    }


def batch_process_data_pareto(categorized_data, nphr, variable_schema):
    calculated_data_by_category = defaultdict(list)
    calculated_data_uncategorized = []
    aggregated_value = defaultdict(lambda: {
        'persen_losses': 0,
        'total_biaya': 0,
        'cost_benefit': 0
    })

    for current_data, target_data, total_cost in categorized_data:
        gap = calculate_gap(target_data.nilai, current_data.nilai)
        persen_losses = calculate_persen_losses(
            gap, target_data.deviasi, current_data.persen_hr
        )
        nilai_losses = (persen_losses / 100) * 1000

        category = current_data.variable.category

        hasCause = True if current_data.variable.causes else False

        # Static Data
        netto = 1000

        cost_benefit = calculate_cost_benefit(netto, nphr, nilai_losses)

        if category is not None:

            aggregated_value[category]['persen_losses'] += persen_losses or 0
            aggregated_value[category]['total_biaya'] += total_cost or 0
            aggregated_value[category]['cost_benefit'] += cost_benefit or 0

        payload = {
            "id": str(current_data.id),
            "variable": variable_schema.dump(current_data.variable),
            "existing_data": current_data.nilai,
            "reference_data": target_data.nilai,
            "deviasi": current_data.deviasi,
            "persen_hr": current_data.persen_hr,
            "persen_losses": persen_losses,
            "nilai_losses": nilai_losses,
            "cost_benefit": cost_benefit,
            "gap": gap,
            "total_biaya": total_cost,
            "symptoms": "Higher" if gap > 0 else "Lower",
            "has_cause" : hasCause,
            "is_pareto" : current_data.variable.is_pareto
        }

        calculated_data_by_category[category].append(payload) if category is not None else calculated_data_uncategorized.append(payload)

    return calculated_data_by_category, calculated_data_uncategorized, aggregated_value
