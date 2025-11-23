# Deployment Guide

## Stock Intelligence System - AWS Deployment

### Prerequisites

- AWS Account with appropriate permissions
- Terraform >= 1.0
- Docker
- AWS CLI configured
- GitHub account (for CI/CD)

### Infrastructure Setup

#### 1. Terraform Deployment

```bash
cd deploy/terraform

# Initialize Terraform
terraform init

# Plan the deployment
terraform plan -var="db_password=YOUR_SECURE_PASSWORD"

# Apply the configuration
terraform apply -var="db_password=YOUR_SECURE_PASSWORD"
```

#### 2. Environment Variables

Set the following secrets in your GitHub repository:

- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `DB_PASSWORD`
- `KIS_APPKEY`
- `KIS_APPSECRET`
- `DART_API_KEY`
- `BIGKINDS_API_KEY`
- `UPSTAGE_API_KEY`
- `KAKAO_ACCESS_TOKEN`

### Container Deployment

#### 1. Build and Push Docker Images

```bash
# Login to ECR
aws ecr get-login-password --region ap-northeast-2 | docker login --username AWS --password-stdin YOUR_ACCOUNT_ID.dkr.ecr.ap-northeast-2.amazonaws.com

# Build API image
docker build -t stock-intelligence-api -f docker/Dockerfile.api .

# Tag and push API image
docker tag stock-intelligence-api:latest YOUR_ACCOUNT_ID.dkr.ecr.ap-northeast-2.amazonaws.com/stock-intelligence/api:latest
docker push YOUR_ACCOUNT_ID.dkr.ecr.ap-northeast-2.amazonaws.com/stock-intelligence/api:latest

# Build Dashboard image
docker build -t stock-intelligence-dashboard -f docker/Dockerfile.dashboard .

# Tag and push Dashboard image
docker tag stock-intelligence-dashboard:latest YOUR_ACCOUNT_ID.dkr.ecr.ap-northeast-2.amazonaws.com/stock-intelligence/dashboard:latest
docker push YOUR_ACCOUNT_ID.dkr.ecr.ap-northeast-2.amazonaws.com/stock-intelligence/dashboard:latest
```

#### 2. Create ECS Task Definitions

API Task Definition (api-task-definition.json):

```json
{
  "family": "stock-intelligence-api",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "containerDefinitions": [
    {
      "name": "api",
      "image": "YOUR_ACCOUNT_ID.dkr.ecr.ap-northeast-2.amazonaws.com/stock-intelligence/api:latest",
      "essential": true,
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {"name": "APP_ENV", "value": "production"},
        {"name": "LOG_LEVEL", "value": "INFO"}
      ],
      "secrets": [
        {"name": "DATABASE_URL", "valueFrom": "arn:aws:secretsmanager:REGION:ACCOUNT:secret:stock-intelligence/db"},
        {"name": "REDIS_URL", "valueFrom": "arn:aws:secretsmanager:REGION:ACCOUNT:secret:stock-intelligence/redis"},
        {"name": "KIS_APPKEY", "valueFrom": "arn:aws:secretsmanager:REGION:ACCOUNT:secret:stock-intelligence/kis-appkey"},
        {"name": "KIS_APPSECRET", "valueFrom": "arn:aws:secretsmanager:REGION:ACCOUNT:secret:stock-intelligence/kis-appsecret"}
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/stock-intelligence/api",
          "awslogs-region": "ap-northeast-2",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

#### 3. Create ECS Services

```bash
# Create API service
aws ecs create-service \
  --cluster stock-intelligence-cluster \
  --service-name stock-intelligence-api \
  --task-definition stock-intelligence-api \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx,subnet-yyy],securityGroups=[sg-xxx],assignPublicIp=ENABLED}" \
  --load-balancers "targetGroupArn=arn:aws:elasticloadbalancing:...,containerName=api,containerPort=8000"

# Create Dashboard service
aws ecs create-service \
  --cluster stock-intelligence-cluster \
  --service-name stock-intelligence-dashboard \
  --task-definition stock-intelligence-dashboard \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx,subnet-yyy],securityGroups=[sg-xxx],assignPublicIp=ENABLED}" \
  --load-balancers "targetGroupArn=arn:aws:elasticloadbalancing:...,containerName=dashboard,containerPort=8501"
```

### Database Initialization

```bash
# Connect to RDS PostgreSQL
psql -h YOUR_RDS_ENDPOINT -U stockadmin -d stockdb

# Run initialization script
\i scripts/init_db.sql
```

### Monitoring and Logging

#### CloudWatch Dashboards

Create custom dashboards to monitor:

- API response times
- Error rates
- Database connections
- Cache hit ratios
- ECS task health

#### Alarms

Set up CloudWatch Alarms for:

- High CPU usage (> 80%)
- High memory usage (> 85%)
- API error rate (> 5%)
- Database connection errors
- ECS task failures

### Scaling Configuration

#### Auto Scaling Policies

```bash
# Register scalable target
aws application-autoscaling register-scalable-target \
  --service-namespace ecs \
  --scalable-dimension ecs:service:DesiredCount \
  --resource-id service/stock-intelligence-cluster/stock-intelligence-api \
  --min-capacity 2 \
  --max-capacity 10

# Create scaling policy
aws application-autoscaling put-scaling-policy \
  --service-namespace ecs \
  --scalable-dimension ecs:service:DesiredCount \
  --resource-id service/stock-intelligence-cluster/stock-intelligence-api \
  --policy-name cpu-scaling-policy \
  --policy-type TargetTrackingScaling \
  --target-tracking-scaling-policy-configuration file://scaling-policy.json
```

### Backup and Recovery

#### Database Backups

- Automated daily backups (retention: 7 days)
- Manual snapshots before major updates
- Point-in-time recovery enabled

#### S3 Data Backups

```bash
# Backup configuration files
aws s3 cp config/ s3://stock-intelligence-data-prod/backups/config/ --recursive

# Backup logs
aws s3 cp /var/log/app/ s3://stock-intelligence-data-prod/backups/logs/ --recursive
```

### Security Best Practices

1. **Secrets Management**
   - Use AWS Secrets Manager for all sensitive data
   - Rotate credentials regularly
   - Never commit secrets to version control

2. **Network Security**
   - Use VPC with private subnets for database
   - Implement security groups with least privilege
   - Enable VPC Flow Logs

3. **Application Security**
   - Enable HTTPS with SSL/TLS certificates
   - Implement rate limiting
   - Use WAF for DDoS protection

4. **Access Control**
   - Use IAM roles for ECS tasks
   - Enable MFA for AWS console access
   - Implement least privilege principle

### Troubleshooting

#### Common Issues

1. **Container fails to start**
   ```bash
   # Check ECS task logs
   aws logs tail /ecs/stock-intelligence/api --follow
   ```

2. **Database connection errors**
   - Verify security group rules
   - Check RDS instance status
   - Validate connection string

3. **High latency**
   - Check Redis cache hit rate
   - Review database query performance
   - Scale ECS tasks if needed

### Cost Optimization

1. **Use Reserved Instances** for predictable workloads
2. **Enable S3 Lifecycle Policies** to archive old logs
3. **Review and optimize** RDS instance size
4. **Use Spot Instances** for non-critical batch jobs
5. **Set up Cost Alerts** in AWS Billing

### Maintenance

#### Regular Tasks

- Weekly: Review CloudWatch metrics and logs
- Monthly: Update Docker images with security patches
- Quarterly: Review and optimize infrastructure costs
- Annually: Disaster recovery drill

### Support and Documentation

- API Documentation: https://YOUR_DOMAIN/docs
- Monitoring Dashboard: CloudWatch Console
- Incident Response: [Your runbook here]

### Contact

For deployment issues or questions, contact:
- DevOps Team: devops@example.com
- On-call: [PagerDuty/Slack channel]
