#!/bin/bash
# Start celery worker
#  Usage: sh start_celery_worker.sh concurrency
export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES
# source "venv/bin/activate"
celery -A make_celery  worker --loglevel INFO --concurrency=$1  -n worker

