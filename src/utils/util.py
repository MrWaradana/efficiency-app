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
