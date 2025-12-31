#! /usr/bin/env bash

set -e
set -x

# Run Alembic migrations
alembic upgrade head

# Initialize MinIO bucket
python scripts/init_minio.py

echo "Backend prestart completed successfully"
