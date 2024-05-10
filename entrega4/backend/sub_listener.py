# Listen to subscription messages from gcloud

from concurrent.futures import TimeoutError
from google.cloud import pubsub_v1

from models import db
import config


from build_flask_app import create_flask_app
app = create_flask_app()
db.init_app(app)

MAX_CONCURRENCY = 1

tasks = []

def callback(message:pubsub_v1.subscriber.message.Message)->None:
    print(f"Received message {message}.")
    if len(tasks) >= MAX_CONCURRENCY:
        print("Max concurrency reached. Skipping message.")
        return
    task_id = int(message.data.decode())
    tasks.append(task_id)
    message.ack()
    try:
        with app.app_context():
            from process_task import process_task
            process_task(task_id)
    except Exception as e:
        print(f"Error processing task {task_id}: {e}")
    finally:
        tasks.remove(task_id)

subscriber = pubsub_v1.SubscriberClient()
subscription_path = config.SUB_NAME
streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)
print(f"Listening for messages on {subscription_path}..\n")

with subscriber:
    try:
        # When `timeout` is not set, result() will block indefinitely,
        # unless an exception is encountered first.
        streaming_pull_future.result()
    except TimeoutError:
        streaming_pull_future.cancel()  # Trigger the shutdown.
        streaming_pull_future.result()  # Block until the shutdown is complete.