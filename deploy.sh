#!/bin/bash

HASH=`git rev-parse --short HEAD`
TAG="gcr.io/redislabs-university/docsearch-app:$HASH"
NEW_TEMPLATE="docsearch-app-west-$HASH"
SERVICE_ACCOUNT="279443788353-compute@developer.gserviceaccount.com"
US_WEST_DISK="docsearch-app-west-2"

#echo "Building $TAG..."
#docker build -t $TAG --build-arg REDIS_PASSWORD=$REDIS_PASSWORD .

#echo "Updating compute engine container"
#docker push $TAG

echo "Creating new us-west instance template $NEW_TEMPLATE from $TAG"
gcloud beta compute --project=redislabs-university instance-templates \
    create-with-container $NEW_TEMPLATE \
    --container-image $TAG \
    --machine-type=e2-standard-4 \
    --network=projects/redislabs-university/global/networks/docsearch \
    --network-tier=PREMIUM \
    --metadata=google-logging-enabled=true \
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
    --disk name=docsearch-data-west \
    --container-mount-disk mount-path="/data",name=docsearch-data-west,mode=rw \
    --labels=container-vm=cos-stable-81-12871-1196-0

echo "Start rolling update"
gcloud compute instance-groups managed rolling-action start-update docsearch-managed-app-1 \
        --version template=$NEW_TEMPLATE --zone us-west1-a

