#!/usr/bin/env bash
# Helper script to build and push Docker image
set -euo pipefail
IMAGE=${1:-"${DOCKERHUB_USER:-youruser}/predyktor:latest"}

echo "Building image $IMAGE"
docker build -t "$IMAGE" .

echo "Pushing $IMAGE"
docker push "$IMAGE"

echo "Done"
