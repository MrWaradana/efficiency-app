from celery import Celery
import requests
from core.config import config
from core.utils.formula import calculate_cost_benefit, calculate_gap, calculate_persen_losses

celery_app = Celery(
    "worker",
    backend=config.CELERY_BACKEND_URL,
    broker=config.CELERY_BROKER_URL,
)

celery_app.conf.task_routes = {"worker.fetch_variable_data": "test-queue"}
celery_app.conf.update(task_track_started=True)

@celery_app.task(bind=True)
def fetch_variable_data(self, url, username, password):
    try:

        if url == "https://10.47.0.54/piwebapi/streams/F1DPw1kUu10ziUaXEx2rIyo4pA2xgAAAS1RKQi1LSTAwLVBJMVxUSkIzLjFSWSBBSVIgRkxPVyAoTUlMTCBJTkxFVCk/value":
            return 'N/A'
        
        response = requests.get(
            url,
            auth=(username, password),
            verify=False,  # Consider removing this in production
            timeout=5
        )
        
        if response.json().get("Errors", None):
            return 'N/A'
        
        if response.status_code == 404:
            return 'N/A'

        if not response.ok:
            return 'N/A'
        
        response.raise_for_status()  # Raise an exception for HTTP errors (e.g., 404)
        return response.json().get('Value', 'N/A')

    except requests.exceptions.RequestException as e:
        self.retry(exc=e, countdown=5)  # Retry on failure
        return 'N/A'
    
    except Exception as e:
        return 'N/A'

def process_data_pareto(self, data, nphr, variable_schema):
    current_data, target_data, total_cost = data
    
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
    
    return payload, per