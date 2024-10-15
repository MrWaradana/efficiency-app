import time
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


LOCK_NAME = 'exceling_thermoflow_process'
LOCK_TIMEOUT = 300  # 1 hour, adjust based on your longest expected process time


@celery_app.task(bind=True)
def send_thermolink_request(self, data_id, unique_id, input_data, url):

    lock = redis.lock(LOCK_NAME, timeout=LOCK_TIMEOUT)

    have_lock = False

    try:

        have_lock = lock.acquire(blocking=False)

        if have_lock:
            res = requests.post(url,
                                json={"inputs": input_data},
                                )
            res.raise_for_status()  # Raise an error if the API request fail

            if res.ok:
                redis.hmset(f"process:{unique_id}", {
                    'data_id': data_id,
                    'lock_name': LOCK_NAME,
                    'status': 'Processing'
                })

            # Wait for the process to complete
            while True:
                status = redis.hget(f'process:{unique_id}', 'status')
                if status == b'Done':
                    return "Process completed successfully"
                elif status == b'Failed':
                    raise Exception("Process failed")
                time.sleep(10)  # Wait for 10 seconds before checking again
        else:
            self.retry(countdown=60)

    except requests.exceptions.RequestException as e:
        # Handle error, e.g., logging or retry mechanism
        print(f"API request failed: {e}")
        self.retry(exc=e, countdown=5)  # Retry on failure

    finally:
        if have_lock:
            # Only release the lock if the process hasn't completed
            # (if it has completed, the lock was released by the callback)
            lock.release()
