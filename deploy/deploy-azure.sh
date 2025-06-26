#!/bin/bash
# Azure Container Instances Deployment Script for AI Interviewer Platform

set -e

# Configuration
RESOURCE_GROUP=${AZURE_RESOURCE_GROUP:-"ai-interviewer-rg"}
LOCATION=${AZURE_LOCATION:-"eastus"}
CONTAINER_NAME="ai-interviewer"
REGISTRY_NAME="aiintervieweracr"
IMAGE_NAME="${REGISTRY_NAME}.azurecr.io/${CONTAINER_NAME}"
DNS_NAME_LABEL="ai-interviewer-$(openssl rand -hex 4)"

echo "🚀 Starting Azure deployment..."

# Create resource group if it doesn't exist
echo "📦 Creating resource group..."
az group create --name ${RESOURCE_GROUP} --location ${LOCATION} || true

# Create Azure Container Registry if it doesn't exist
echo "📝 Creating container registry..."
az acr create --resource-group ${RESOURCE_GROUP} \
  --name ${REGISTRY_NAME} \
  --sku Basic \
  --admin-enabled true || true

# Get registry credentials
echo "🔐 Getting registry credentials..."
REGISTRY_USERNAME=$(az acr credential show --name ${REGISTRY_NAME} --query username -o tsv)
REGISTRY_PASSWORD=$(az acr credential show --name ${REGISTRY_NAME} --query passwords[0].value -o tsv)

# Build and push image to ACR
echo "📦 Building and pushing Docker image..."
az acr build --registry ${REGISTRY_NAME} \
  --image ${CONTAINER_NAME}:latest \
  --file Dockerfile .

# Deploy to Azure Container Instances
echo "🚀 Deploying to Azure Container Instances..."
az container create \
  --resource-group ${RESOURCE_GROUP} \
  --name ${CONTAINER_NAME} \
  --image ${IMAGE_NAME}:latest \
  --registry-login-server ${REGISTRY_NAME}.azurecr.io \
  --registry-username ${REGISTRY_USERNAME} \
  --registry-password ${REGISTRY_PASSWORD} \
  --dns-name-label ${DNS_NAME_LABEL} \
  --ports 8000 \
  --cpu 1 \
  --memory 1.5 \
  --environment-variables \
    OPENAI_API_KEY=${OPENAI_API_KEY} \
    ELEVENLABS_API_KEY=${ELEVENLABS_API_KEY} \
  --restart-policy OnFailure

# Get the FQDN
echo "⏳ Waiting for deployment to complete..."
sleep 30

FQDN=$(az container show \
  --resource-group ${RESOURCE_GROUP} \
  --name ${CONTAINER_NAME} \
  --query ipAddress.fqdn \
  --output tsv)

echo "✅ Deployment complete!"
echo "🌐 Your application is available at: http://${FQDN}:8000"
echo ""
echo "📝 Additional commands:"
echo "  - View logs: az container logs --resource-group ${RESOURCE_GROUP} --name ${CONTAINER_NAME}"
echo "  - Stream logs: az container attach --resource-group ${RESOURCE_GROUP} --name ${CONTAINER_NAME}"
echo "  - Delete deployment: az group delete --name ${RESOURCE_GROUP} --yes"

# Optional: Deploy with Azure App Service instead
echo ""
echo "💡 For production, consider using Azure App Service:"
echo "  az webapp up --name ${CONTAINER_NAME} --resource-group ${RESOURCE_GROUP} --runtime 'PYTHON:3.11'" 