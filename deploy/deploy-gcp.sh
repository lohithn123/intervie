#!/bin/bash
# Google Cloud Run Deployment Script for AI Interviewer Platform

set -e

# Configuration
PROJECT_ID=${GCP_PROJECT_ID:-$(gcloud config get-value project)}
REGION=${GCP_REGION:-"us-central1"}
SERVICE_NAME="ai-interviewer"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

echo "🚀 Starting GCP deployment..."
echo "📍 Project: ${PROJECT_ID}"
echo "📍 Region: ${REGION}"

# Enable required APIs
echo "🔧 Enabling required APIs..."
gcloud services enable containerregistry.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com

# Build and push Docker image to Container Registry
echo "📦 Building and pushing Docker image..."
gcloud builds submit --tag ${IMAGE_NAME}:latest .

# Deploy to Cloud Run
echo "🚀 Deploying to Cloud Run..."
gcloud run deploy ${SERVICE_NAME} \
  --image ${IMAGE_NAME}:latest \
  --platform managed \
  --region ${REGION} \
  --allow-unauthenticated \
  --port 8000 \
  --memory 1Gi \
  --cpu 1 \
  --timeout 300 \
  --concurrency 100 \
  --max-instances 10 \
  --set-env-vars "OPENAI_API_KEY=${OPENAI_API_KEY},ELEVENLABS_API_KEY=${ELEVENLABS_API_KEY}"

# Get the service URL
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} --platform managed --region ${REGION} --format 'value(status.url)')

echo "✅ Deployment complete!"
echo "🌐 Your application is available at: ${SERVICE_URL}"
echo ""
echo "📝 Additional configurations:"
echo "  - To add a custom domain: gcloud run domain-mappings create --service ${SERVICE_NAME} --domain YOUR_DOMAIN --region ${REGION}"
echo "  - To view logs: gcloud logging read 'resource.type=cloud_run_revision AND resource.labels.service_name=${SERVICE_NAME}' --project ${PROJECT_ID}"
echo "  - To update environment variables: gcloud run services update ${SERVICE_NAME} --update-env-vars KEY=VALUE --region ${REGION}" 