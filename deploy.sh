#!/bin/bash

HASH=`git rev-parse --short HEAD`
TAG=docsearch-app:$HASH
IMAGE="gcr.io/redislabs-university/$TAG"

echo "Building $IMAGE..."
docker build -t $TAG --build-arg "REDIS_PASSWORD=$REDIS_PASSWORD" .

echo "Updating compute engine container"
docker push $IMAGE
gcloud compute instances update-container docsearch-west --container-image $IMAGE
