#!/bin/bash

HASH=`git rev-parse --short HEAD`
APP_TAG="abrookins/docsearch-app:$HASH-$RANDOM"
WORKER_TAG="abrookins/docsearch-worker:$HASH-$RANDOM"
SCHEDULER_TAG="abrookins/docsearch-scheduler:$HASH-$RANDOM"

echo "Building $APP_TAG..."
docker build -t $APP_TAG . -f docker/app/Dockerfile

echo "Building $WORKER_TAG..."
docker build -t $WORKER_TAG . -f docker/worker/Dockerfile

echo "Building $SCHEDULER_TAG..."
docker build -t $SCHEDULER_TAG . -f docker/scheduler/Dockerfile


echo "Pushing tags..."
docker push $APP_TAG
docker push $WORKER_TAG
docker push $SCHEDULER_TAG

