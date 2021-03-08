#!/bin/bash

HASH=`git rev-parse --short HEAD`
TAG="gcr.io/redislabs-university/docsearch-app:$HASH-$RANDOM"
NEW_TEMPLATE="docsearch-app-global-$HASH-$RANDOM"
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
    --machine-type=e2-medium \
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
    --container-env-file ./.env.prod \
    --labels=container-vm=cos-stable-81-12871-1196-0

echo
echo "Start rolling update of US-West"
echo "--------------------------------"
gcloud compute instance-groups managed rolling-action start-update docsearch-managed-app-1 \
        --version template=$NEW_TEMPLATE --zone us-west1-a

echo
echo "GOOD IDEA: Wait until the instance group updates, make some test requests. "
read -p "Press enter to continue deploying to to other regions..."

echo
echo "Start rolling update of Mumbai"
echo "-------------------------------"
gcloud compute instance-groups managed rolling-action start-update docsearch-managed-app-mumbai \
        --version template=$NEW_TEMPLATE --zone asia-south1-c

echo
echo "Start rolling update of US-East"
echo "--------------------------------"
gcloud compute instance-groups managed rolling-action start-update docsearch-managed-app-us-east \
        --version template=$NEW_TEMPLATE --zone us-east4-c

echo
echo "Start rolling update of Zurich"
echo "-------------------------------"
gcloud compute instance-groups managed rolling-action start-update docsearch-managed-app-zurich \
        --version template=$NEW_TEMPLATE --zone europe-west6-a
