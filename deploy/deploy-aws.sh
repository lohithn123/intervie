#!/bin/bash
# AWS ECS/Fargate Deployment Script for AI Interviewer Platform

set -e

# Configuration
AWS_REGION=${AWS_REGION:-"us-east-1"}
ECR_REPOSITORY="ai-interviewer"
ECS_CLUSTER="ai-interviewer-cluster"
ECS_SERVICE="ai-interviewer-service"
TASK_DEFINITION="ai-interviewer-task"
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

echo "🚀 Starting AWS deployment..."

# Build and push Docker image to ECR
echo "📦 Building Docker image..."
docker build -t ${ECR_REPOSITORY}:latest .

# Login to ECR
echo "🔐 Logging into ECR..."
aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com

# Create ECR repository if it doesn't exist
aws ecr describe-repositories --repository-names ${ECR_REPOSITORY} --region ${AWS_REGION} || \
aws ecr create-repository --repository-name ${ECR_REPOSITORY} --region ${AWS_REGION}

# Tag and push image
echo "📤 Pushing image to ECR..."
docker tag ${ECR_REPOSITORY}:latest ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPOSITORY}:latest
docker push ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPOSITORY}:latest

# Create task definition
echo "📝 Creating task definition..."
cat > task-definition.json <<EOF
{
  "family": "${TASK_DEFINITION}",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "containerDefinitions": [
    {
      "name": "ai-interviewer",
      "image": "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPOSITORY}:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "OPENAI_API_KEY",
          "value": "${OPENAI_API_KEY}"
        },
        {
          "name": "ELEVENLABS_API_KEY",
          "value": "${ELEVENLABS_API_KEY}"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/ai-interviewer",
          "awslogs-region": "${AWS_REGION}",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
EOF

# Register task definition
aws ecs register-task-definition --cli-input-json file://task-definition.json --region ${AWS_REGION}

# Create or update ECS service
echo "🚀 Deploying to ECS..."
aws ecs update-service \
  --cluster ${ECS_CLUSTER} \
  --service ${ECS_SERVICE} \
  --task-definition ${TASK_DEFINITION} \
  --force-new-deployment \
  --region ${AWS_REGION} || \
echo "Service update failed. You may need to create the cluster and service first."

# Clean up
rm task-definition.json

echo "✅ Deployment complete!"
echo "🌐 Access your application through the ALB URL configured in your ECS service." 