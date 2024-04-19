# Executes load testing on the celery server
# Usage: python3 load_testing.py number_of_tasks
import threading
from typing import List
import datetime
import os
import logging
from uuid import uuid4
import shutil
import subprocess
import csv
import time
import signal
import psutil


from celery import group
from celery.result import GroupResult

from models import db, Task, User, TaskStatus
from celery_tasks import process_task

WAIT_PER_TAKS = 60
MAX_CPU = 0.95 * 100
MAX_DURATION = 10
VIDEO_PATH = os.path.abspath("load_testing_video.mp4")


def create_task(folder_path: str, total_tasks: int) -> List[Task]:
    """Create queued tasks."""
    user = User.query.first()
    if not user:
        user = User(username="test", email="test", hashed_password="test")
        db.session.add(user)
        db.session.commit()
    tasks = []
    for _i in range(total_tasks):
        uuid = uuid4()
        video_folder = os.path.join(folder_path, str(uuid))
        os.makedirs(video_folder, exist_ok=True)
        video_path = os.path.abspath(os.path.join(video_folder, "video.mp4"))
        shutil.copyfile(VIDEO_PATH, video_path)
        task = Task(
            status=TaskStatus.UPLOADED,
            created_by_id=user.id,
            video_path=video_path,
            file_name="test_video.mp4",
        )
        db.session.add(task)
        tasks.append(task)
    db.session.commit()
    return [t.id for t in tasks]


def delete_tasks(tasks: List[Task]):
    """Delete tasks with results."""
    for task in tasks:
        task: Task = Task.query.get(task)
        shutil.rmtree(os.path.dirname(task.video_path))
        db.session.delete(task)


def write_results(
    folder_path: str, concurrency: str, results: List[int], celery_tasks: List[str]
) -> bool:
    """Write results to a csv file.
    Additionally says if all were processed correctly
    """
    # Ensure session is
    failed_tasks = False
    with open(f"{folder_path}/{concurrency}_results.csv", mode="w") as file:
        writer = csv.writer(file)
        writer.writerow(
            [
                "task_id",
                "status",
                "processing_time_seconds",
                "processing_started_at",
                "processing_ended_at",
                "celery_task_id",
                "celery_status",
            ]
        )
        for i, task_id in enumerate(results):
            task: Task = Task.query.get(task_id)
            if task.status != TaskStatus.PROCESSED:
                failed_tasks = True
            writer.writerow(
                [
                    task.id,
                    task.status,
                    (
                        (
                            task.processing_ended_at - task.processing_started_at
                        ).total_seconds()
                        if task.processing_ended_at and task.processing_started_at
                        else None
                    ),
                    (
                        task.processing_started_at.timestamp()
                        if task.processing_started_at
                        else None
                    ),
                    (
                        task.processing_ended_at.timestamp()
                        if task.processing_ended_at
                        else None
                    ),
                    celery_tasks[i].id,
                    celery_tasks[i].status,
                ]
            )
        return failed_tasks


def run_scenary(
    flask_app, total_tasks: int, concurrency: int, folder_path: str
) -> bool:
    print(
        "starting scenary with concurrency",
        concurrency,
        "at",
        datetime.datetime.now(),
        "for",
        total_tasks,
        "tasks",
    )

    MAX_WAIT = WAIT_PER_TAKS * total_tasks

    save_stats = True
    too_much_cpu = False

    def save_cpu_and_memory_usage() -> bool:
        """Save CPU and memory usage
        Also says if too much CPU was used
        ."""
        nonlocal too_much_cpu
        with open(
            f"{folder_path}/{concurrency}_cpu_memory_usage.csv", mode="w"
        ) as file:
            writer = csv.writer(file)
            writer.writerow(["time", "cpu", "memory"])
            while save_stats:
                timestamp = datetime.datetime.now().timestamp()
                cpu_percent = psutil.cpu_percent()
                if cpu_percent > MAX_CPU:
                    too_much_cpu = True
                writer.writerow(
                    [
                        timestamp,
                        cpu_percent,
                        psutil.virtual_memory().percent,
                    ]
                )
                time.sleep(0.5)

    # Purge taks
    flask_app.extensions["celery"].control.purge()

    #  Create tasks
    tasks_ids = create_task(folder_path, total_tasks)
    # queue tasks to celery
    celery_tasks = []
    for task_id in tasks_ids:
        celery_task = process_task.s(task_id)
        celery_tasks.append(celery_task)

    # Lunch a thread to save CPU and memory usage
    cpu_memory_thread = threading.Thread(target=save_cpu_and_memory_usage)
    cpu_memory_thread.start()

    # Start celery worker
    process = subprocess.Popen(
        [os.path.abspath("start_celery_worker.sh"), str(concurrency)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
        preexec_fn=os.setsid,
    )
    try:
        # Wait for tasks to finish
        job = group(celery_tasks)
        result = job.apply_async()
        result.save()
        start_at = datetime.datetime.now()
        too_much_time = False
        while True:
            if result.ready():
                break
            if (datetime.datetime.now() - start_at).seconds > MAX_WAIT:
                print("Kiling worker, too much time")
                # Kill the worker
                too_much_time = True
                break
            time.sleep(1)
        save_stats = False
        cpu_memory_thread.join()
        saved_result = GroupResult.restore(result.id)
        failed_tasks = write_results(
            folder_path, concurrency, tasks_ids, saved_result.results
        )
        #  Delete tasks with results
        delete_tasks(tasks_ids)
    finally:
        os.killpg(
            os.getpgid(process.pid), signal.SIGTERM
        )  # Send the signal to all the process groups
        # pass
    print(
        "Ended scenary with concurrency",
        concurrency,
        "at",
        datetime.datetime.now(),
        "for",
        total_tasks,
        "tasks",
    )
    if too_much_cpu:
        print("Too much CPU for scenary with concurrency", concurrency)
    if failed_tasks:
        print("Failed tasks for scenary with concurrency", concurrency)
    if too_much_time:
        print("Task are taken more than 60 seconds", concurrency)
    return not too_much_cpu and not failed_tasks and not too_much_time


def load_test(flask_app, total_tasks: int, total_minutes: int):
    start_at = datetime.datetime.now()
    print(f"Starting load testing at {start_at} and max {total_minutes} minutes")
    # Create results folder
    folder_path = f"load_testing/{start_at.isoformat()}"
    os.makedirs(folder_path, exist_ok=True)
    initial_concurrency = 1
    keep_going = run_scenary(flask_app, total_tasks, initial_concurrency, folder_path)
    #  Check if need to increment concurrency
    while keep_going:
        initial_concurrency += 1
        keep_going = run_scenary(
            flask_app, total_tasks, initial_concurrency, folder_path
        )
        if datetime.datetime.now() - start_at > datetime.timedelta(
            minutes=total_minutes
        ):
            break
    end_at = datetime.datetime.now()
    print(
        "Load testing finished",
        end_at,
        "total time",
        (end_at - start_at).total_seconds(),
    )
