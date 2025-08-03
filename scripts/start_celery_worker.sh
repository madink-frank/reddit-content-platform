#!/bin/bash
"""
Script to start Celery worker for development.
"""

echo "Starting Celery worker for Reddit Content Platform..."

# Set environment variables if not already set
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Start Celery worker with appropriate settings
celery -A app.core.celery_app worker \
    --loglevel=info \
    --concurrency=4 \
    --queues=crawling,analysis,content,deployment,maintenance,celery \
    --hostname=worker@%h \
    --without-gossip \
    --without-mingle \
    --without-heartbeat