#!/bin/bash

HASH=`git rev-parse --short HEAD`
TAG="gcr.io/redislabs-university/docsearch-app:$HASH"

echo "Building $TAG..."
docker build -t $TAG --build-arg REDIS_PASSWORD=$REDIS_PASSWORD .

echo "Updating compute engine container"
docker push $TAG
gcloud compute instances update-container docsearch-app-west --container-image $TAG
