#!/usr/bin/env bash

# 1) Extend Cloud Build & HTTP timeouts
gcloud config set builds/timeout 30m               # allow longer build time
export CLOUDSDK_CORE_HTTP_TIMEOUT=300              # allow longer HTTP upload

# 2) Deploy Gen 2 Function
gcloud functions deploy pm-sage-rag \
  --gen2 \
  --region=us-east1 \
  --runtime=python311 \
  --entry-point=app \
  --trigger-http \
  --memory=1Gi \
  --allow-unauthenticated \
  --verbosity=debug

