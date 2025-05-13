#!/usr/bin/env bash

# 1. Ensure the Artifact Registry repo exists
gcloud artifacts repositories describe pm-sage-repo --location=us-east1 \
  || gcloud artifacts repositories create pm-sage-repo \
       --repository-format=docker \
       --location=us-east1 \
       --description="Docker repo for PM-Sage UI"

# 2. Build & push via Cloud Build
gcloud builds submit ui/ \
  --tag=us-east1-docker.pkg.dev/qwiklabs-gcp-03-f29fe995937e/pm-sage-repo/pm-sage-ui:latest

# 3. Deploy to Cloud Run
gcloud run deploy pm-sage-ui \
  --image=us-east1-docker.pkg.dev/qwiklabs-gcp-03-f29fe995937e/pm-sage-repo/pm-sage-ui:latest \
  --region=us-east1 \
  --platform=managed \
  --allow-unauthenticated
