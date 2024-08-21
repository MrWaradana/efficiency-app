import requests

def fetch_data_from_api(url):
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json()
    else:
        return None
    
def get_key_by_value(d, value):
    for key, val in d.items():
        if val == value:
            return key
    return None 