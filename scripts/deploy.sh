#!/bin/bash
set -euo pipefail

# deploy a new docker image to a service in ECS and wait for the deployment to finish
# usage: `ENVIRONMENT=integration IMAGE_TAG=latest ./deploy.sh sandwich`

APP=${1?"app name required"}
ENVIRONMENT=${ENVIRONMENT?"must be defined"}
IMAGE_TAG=${IMAGE_TAG:-latest}
DEPLOY_TIMEOUT=${DEPLOY_TIMEOUT:-900}

CLUSTER="$ENVIRONMENT-newhippo"
SERVICE="$ENVIRONMENT-sandwich-$APP"

SERVICES=("$SERVICE")

# Add worker service for sandwich
if [[ "$APP" == "sandwich" ]]; then
  SERVICES+=("$SERVICE-worker")
fi

# 1: re-tag the docker image app:latest to app:integration
MANIFEST=$(aws ecr batch-get-image --repository-name "$APP" --image-ids imageTag="$IMAGE_TAG" --output text --query 'images[].imageManifest')
if [[ -z "$MANIFEST" ]]; then
  echo "failed to get image manifest for $APP:$IMAGE_TAG"
  exit 1
fi
aws ecr put-image --repository-name "$APP" --image-tag "$ENVIRONMENT" --image-manifest "$MANIFEST"

# 2: trigger an ECS deployment that will pick up the updated image
for SERVICE in "${SERVICES[@]}"; do
  aws ecs update-service --cluster "$CLUSTER" --service "$SERVICE" --force-new-deployment
done

# 3: wait for the previous deployment to drain
for SERVICE in "${SERVICES[@]}"; do
  echo "waiting for deployment of $SERVICE in $CLUSTER to finish..."
  while true; do
    DEPLOYMENTS=$(aws ecs describe-services --cluster "$CLUSTER" --services "$SERVICE" --query 'services[].deployments[].[rolloutState,createdAt]' --output text)
    echo "$DEPLOYMENTS"

    set +e
    FAILED=$(echo "$DEPLOYMENTS" | grep -c "FAILED")
    IN_PROGRESS=$(echo "$DEPLOYMENTS" | grep -c "IN_PROGRESS")
    set -e

    # if any deployments are in progress, wait
    if [[ $IN_PROGRESS -gt 0 ]]; then
      if [[ "$SECONDS" -gt "$DEPLOY_TIMEOUT" ]]; then
        echo "timed out after $SECONDS seconds"
        exit 1
      fi
      echo "will check again in 10s..."
      sleep 10
    elif [[ $FAILED -gt 0 ]]; then
      echo "deployment failed"
      exit 1
    else
      break
    fi
  done
done
