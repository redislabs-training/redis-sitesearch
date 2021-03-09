#!/bin/bash

HASH=`git rev-parse --short HEAD`
TAG="gcr.io/redislabs-university/docsearch-app-staging:$HASH-$RANDOM"
NEW_TEMPLATE="docsearch-app-staging-$HASH-$RANDOM"
SERVICE_ACCOUNT="279443788353-compute@developer.gserviceaccount.com"
US_WEST_DISK="docsearch-app-west-2"

echo "Building $TAG..."
docker build -t $TAG .

echo "Updating compute engine container"
docker push $TAG

echo "Creating new instance template $NEW_TEMPLATE from $TAG"
gcloud beta compute --project=redislabs-university instance-templates \
    create-with-container $NEW_TEMPLATE \
    --container-image $TAG \
    --machine-type=e2-micro \
    --network=projects/redislabs-university/global/networks/docsearch \
    --network-tier=PREMIUM \
    --metadata=google-logging-enabled=false \
    --can-ip-forward \
    --maintenance-policy=MIGRATE \
    --service-account=$SERVICE_ACCOUNT \
    --scopes=https://www.googleapis.com/auth/devstorage.read_only,https://www.googleapis.com/auth/logging.write,https://www.googleapis.com/auth/monitoring.write,https://www.googleapis.com/auth/servicecontrol,https://www.googleapis.com/auth/service.management.readonly,https://www.googleapis.com/auth/trace.append \
    --image=cos-stable-81-12871-1196-0 \
    --image-project=cos-cloud \
    --boot-disk-size=10GB \
    --boot-disk-type=pd-standard \
    --boot-disk-device-name=$US_WEST_DISK \
    --container-image=$TAG \
    --container-restart-policy=always \
    --container-mount-host-path=mount-path=/data,host-path=/var/data/redis,mode=rw \
    --container-env-file ./.env.staging \
    --labels=container-vm=cos-stable-81-12871-1196-0

echo
echo "Start rolling update of staging us-west1"
echo "--------------------------------"
gcloud compute instance-groups managed rolling-action start-update docsearch-app-staging \
        --version template=$NEW_TEMPLATE --zone us-west1-a
