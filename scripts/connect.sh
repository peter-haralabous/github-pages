#!/bin/bash
#
# start an interactive session inside a running bread ECS task
# usage: ./scripts/connect.sh integration
#
set -euo pipefail
ENVIRONMENT=${1?"environment required"}

CLUSTER="$ENVIRONMENT-newhippo"
SERVICE="$ENVIRONMENT-sandwich-sandwich"
CONTAINER="sandwich"

TASK=$(aws ecs list-tasks --cluster "$CLUSTER" --service-name "$SERVICE" --query "taskArns[0]" --output text)

exec aws ecs execute-command --cluster "$CLUSTER" --task "$TASK" --container "$CONTAINER" --interactive --command /bin/bash
