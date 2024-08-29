import random
import requests


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


def get_key_by_value(variable_mapping, value):

    for key, val in variable_mapping.items():

        variable_string = (
            f"{val['category']}: {val['name']}" if val["category"] else val["name"]
        )

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
