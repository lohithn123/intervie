# 🚀 AI Interviewer Platform - Deployment Guide

This guide covers deploying the AI Interviewer Platform to various cloud providers and environments.

## 📋 Prerequisites

- Docker and Docker Compose installed
- API keys for OpenAI and ElevenLabs
- Cloud provider CLI tools (AWS CLI, gcloud, az) if deploying to cloud
- Domain name (optional, for production)
- SSL certificates (for HTTPS in production)

## 🐳 Local Deployment with Docker

### Quick Start

1. **Clone the repository**

   ```bash
   git clone https://github.com/702ron/ai-interviewer-platform.git
   cd ai-interviewer-platform
   ```

2. **Set up environment variables**

   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Run with Docker Compose**

   ```bash
   docker-compose up -d
   ```

4. **Access the application**
   - Open http://localhost:8000 in your browser
   - API docs: http://localhost:8000/docs

### Development Mode

For hot-reloading during development:

```bash
docker-compose up
```

This mounts your source code as volumes, allowing live updates.

## ☁️ Cloud Deployments

### AWS (ECS/Fargate)

1. **Prerequisites**

   - AWS CLI configured
   - ECR access
   - ECS cluster created

2. **Deploy**

   ```bash
   chmod +x deploy/deploy-aws.sh
   ./deploy/deploy-aws.sh
   ```

3. **Configure ALB**
   - Create an Application Load Balancer
   - Configure target group for port 8000
   - Add WebSocket support in target group attributes

### Google Cloud Platform (Cloud Run)

1. **Prerequisites**

   - gcloud CLI configured
   - Project selected

2. **Deploy**

   ```bash
   chmod +x deploy/deploy-gcp.sh
   ./deploy/deploy-gcp.sh
   ```

3. **Enable WebSocket support**
   ```bash
   gcloud run services update ai-interviewer \
     --session-affinity \
     --region us-central1
   ```

### Azure (Container Instances)

1. **Prerequisites**

   - Azure CLI configured
   - Subscription selected

2. **Deploy**
   ```bash
   chmod +x deploy/deploy-azure.sh
   ./deploy/deploy-azure.sh
   ```

## 🔒 Production Configuration

### SSL/TLS Setup

1. **Obtain SSL certificates**

   - Use Let's Encrypt for free certificates
   - Or purchase from a certificate authority

2. **Configure Nginx**

   ```bash
   # Place certificates in ssl/ directory
   mkdir ssl
   cp your-cert.pem ssl/cert.pem
   cp your-key.pem ssl/key.pem
   ```

3. **Deploy with Nginx**
   ```bash
   docker-compose --profile production up -d
   ```

### Environment Variables

Create `.env.production` from the template:

```bash
cp .env.production.example .env.production
# Edit with production values
```

Key variables:

- `OPENAI_API_KEY`: Your OpenAI API key
- `ELEVENLABS_API_KEY`: Your ElevenLabs API key
- `SECRET_KEY`: Generate with `openssl rand -hex 32`
- `ALLOWED_HOSTS`: Your domain names

### Database Considerations

For production, consider migrating from SQLite to PostgreSQL:

1. **Update DATABASE_URL**

   ```
   DATABASE_URL=postgresql+asyncpg://user:password@host:5432/dbname
   ```

2. **Add to requirements.txt**

   ```
   asyncpg==0.28.0
   ```

3. **Update docker-compose.yml** to include PostgreSQL service

## 🔍 Monitoring & Logging

### Application Logs

- **Docker**: `docker-compose logs -f interviewer`
- **AWS**: CloudWatch Logs
- **GCP**: Cloud Logging
- **Azure**: Container Instance logs

### Health Checks

The application includes health check endpoints:

- `/` - Basic health check
- `/health` - Detailed health status

### Performance Monitoring

Consider integrating:

- **Sentry** for error tracking
- **Datadog** or **New Relic** for APM
- **Prometheus + Grafana** for metrics

## 🔧 Troubleshooting

### Common Issues

1. **WebSocket Connection Fails**

   - Ensure your reverse proxy supports WebSocket upgrade
   - Check CORS settings if accessing from different domain
   - Verify firewall rules allow WebSocket traffic

2. **Audio Not Working**

   - Verify ElevenLabs API key is valid
   - Check browser console for MediaRecorder errors
   - Ensure HTTPS is enabled (required for microphone access)

3. **High Memory Usage**
   - Increase container memory limits
   - Consider implementing audio chunk size limits
   - Monitor for memory leaks in long-running interviews

### Debug Mode

Enable debug logging:

```bash
LOG_LEVEL=debug docker-compose up
```

## 🚦 Scaling Considerations

### Horizontal Scaling

1. **Stateless Design**

   - Application is stateless except for SQLite
   - Use external database for multi-instance deployment

2. **Load Balancing**

   - Use sticky sessions for WebSocket connections
   - Configure session affinity in your load balancer

3. **Caching**
   - Consider Redis for session management
   - Cache AI responses where appropriate

### Vertical Scaling

Adjust resources based on usage:

```yaml
# docker-compose.yml
services:
  interviewer:
    deploy:
      resources:
        limits:
          cpus: "2"
          memory: 4G
```

## 📊 Cost Optimization

1. **API Usage**

   - Monitor OpenAI and ElevenLabs usage
   - Implement rate limiting
   - Consider caching common responses

2. **Infrastructure**

   - Use spot instances for non-critical workloads
   - Implement auto-scaling policies
   - Schedule scaling for known traffic patterns

3. **Storage**
   - Implement log rotation
   - Clean up old interview data
   - Use object storage for audio files

## 🔄 Backup & Recovery

### Database Backup

```bash
# Backup SQLite database
docker-compose exec interviewer sqlite3 /app/data/interviewer.db ".backup /app/data/backup.db"

# For PostgreSQL
pg_dump -h localhost -U user -d interviewer > backup.sql
```

### Application State

- Interview transcripts are stored in the database
- Consider backing up to S3/GCS/Azure Storage
- Implement automated backup schedules

## 📝 Maintenance

### Updates

1. **Pull latest changes**

   ```bash
   git pull origin main
   ```

2. **Rebuild and deploy**
   ```bash
   docker-compose build
   docker-compose up -d
   ```

### Security Updates

- Regularly update base Docker images
- Keep Python dependencies updated
- Monitor for security advisories

## 🤝 Support

For issues and questions:

- Check the [GitHub Issues](https://github.com/702ron/ai-interviewer-platform/issues)
- Review application logs
- Ensure all prerequisites are met

---

Happy deploying! 🎉
