from celery import Celery
import requests
from core.config import config

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
        response = requests.get(
            url,
            auth=(username, password),
            verify=False,  # Consider removing this in production
            timeout=5
        )
        response.raise_for_status()  # Raises an error for 4xx/5xx responses
        return response.json().get('Value', 'N/A')

    except requests.RequestException as e:
        self.retry(exc=e, countdown=5)  # Retry on failure
        return 'N/A'
