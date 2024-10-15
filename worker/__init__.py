from celery import Celery
import requests
from core.config import config
from core.utils.formula import calculate_cost_benefit, calculate_gap, calculate_persen_losses
from core.cache.redis_backend import redis
from core.factory.data import data_factory

celery_app = Celery(
    "worker",
    backend=config.CELERY_BACKEND_URL,
    broker=config.CELERY_BROKER_URL,
)

data_repository = data_factory.data_repository

celery_app.conf.task_routes = {
    "worker.fetch_variable_data": "variable-queue",
    "worker.send_thermolink_request": "excel-queue"
}
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


class ExcelTask(celery_app.Task):
    abstract = True

    def delay(self, *args, **kwargs):
        # Always queue the task
        return super().delay(*args, **kwargs)

    def apply_async(self, args=None, kwargs=None, **options):
        # Always queue the task
        return super().apply_async(args=args, kwargs=kwargs, **options)

    def __call__(self, *args, **kwargs):
        # Check if we can process the task
        if bool(redis.get('excel_processing')):
            # If a task is being processed, re-queue this task
            self.retry(countdown=60, max_retries=5)
        else:
            # Set the processing flag and proceed with the task
            redis.set('excel_processing', '1')
            return super().__call__(*args, **kwargs)


@celery_app.task(bind=True, base=ExcelTask)
def send_thermolink_request(self, data_id, unique_id, input_data):

    try:
        res = requests.post(
            f"{config.WINDOWS_EFFICIENCY_APP_API}/excels/{unique_id}",
            json={"inputs": input_data},
        )
        res.raise_for_status()  # Raise an error if the API request fail

    except requests.exceptions.RequestException as e:
        # Handle error, e.g., logging or retry mechanism
        print(f"API request failed: {e}")
        self.retry(exc=e, countdown=5)  # Retry on failure
