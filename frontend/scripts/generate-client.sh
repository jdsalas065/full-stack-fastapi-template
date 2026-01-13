#! /usr/bin/env bash

set -e
set -x

# Script to generate OpenAPI client for frontend
# This script can work in two modes:
# 1. From a running backend API (default)
# 2. From an existing openapi.json file

API_URL="${VITE_API_URL:-http://localhost:8000}"
OPENAPI_JSON_URL="${API_URL}/api/v1/openapi.json"
OPENAPI_JSON_FILE="./openapi.json"

echo "Generating OpenAPI client..."

# Check if openapi.json already exists
if [ -f "$OPENAPI_JSON_FILE" ]; then
    echo "Using existing openapi.json file..."
    npm run generate-client
    exit 0
fi

# Try to fetch from running backend
echo "Fetching OpenAPI schema from ${OPENAPI_JSON_URL}..."
if curl -f -s "$OPENAPI_JSON_URL" > "$OPENAPI_JSON_FILE" 2>/dev/null; then
    echo "Successfully fetched OpenAPI schema"
    npm run generate-client
    rm -f "$OPENAPI_JSON_FILE"
else
    echo "Error: Could not fetch OpenAPI schema from ${OPENAPI_JSON_URL}"
    echo "Please ensure:"
    echo "  1. Backend is running at ${API_URL}"
    echo "  2. Or place an openapi.json file in the frontend directory"
    exit 1
fi
