#!/bin/bash

HASH=`git rev-parse --short HEAD`
SERVICE_ACCOUNT="279443788353-compute@developer.gserviceaccount.com"
US_WEST_DISK="docsearch-app-west-2"

APP_TAG="gcr.io/redislabs-university/docsearch-app-production:$HASH-$RANDOM"
WORKER_TAG="gcr.io/redislabs-university/docsearch-worker-production:$HASH-$RANDOM"

NEW_APP_TEMPLATE_USWEST="docsearch-app-production-$HASH-$RANDOM-uswest"
NEW_WORKER_TEMPLATE_USWEST="docsearch-worker-production-$HASH-$RANDOM-uswest"

NEW_APP_TEMPLATE_MUMBAI="docsearch-app-production-$HASH-$RANDOM-mumbai"
NEW_WORKER_TEMPLATE_MUMBAI="docsearch-worker-production-$HASH-$RANDOM-mumbai"

NEW_APP_TEMPLATE_ZURICH="docsearch-app-production-$HASH-$RANDOM-zurich"
NEW_WORKER_TEMPLATE_ZURICH="docsearch-worker-production-$HASH-$RANDOM-zurich"


echo "Building $APP_TAG..."
docker build -t $APP_TAG . -f docker/app/Dockerfile

echo "Building $WORKER_TAG..."
docker build -t $WORKER_TAG . -f docker/worker/Dockerfile

echo "Pushing tags..."
docker push $APP_TAG
docker push $WORKER_TAG


us-west
echo "Deploying to US-WEST"

echo "Creating new app instance template $NEW_APP_TEMPLATE_USWEST from $APP_TAG"

gcloud beta compute --project=redislabs-university instance-templates \
create-with-container $NEW_APP_TEMPLATE_USWEST \
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
--container-image=$APP_TAG \
--container-restart-policy=always \
--container-mount-host-path=mount-path=/data,host-path=/var/data/redis,mode=rw \
--container-env-file ./.env.prod.uswest \
--labels=container-vm=cos-stable-81-12871-1196-0


echo "Creating new worker instance template $NEW_WORKER_TEMPLATE_USWEST from $WORKER_TAG"
gcloud beta compute --project=redislabs-university instance-templates \
create-with-container $NEW_WORKER_TEMPLATE_USWEST \
--container-image $WORKER_TAG \
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
--container-restart-policy=always \
--container-mount-host-path=mount-path=/data,host-path=/var/data/redis,mode=rw \
--container-env-file ./.env.prod.uswest \
--labels=container-vm=cos-stable-81-12871-1196-0



echo
echo "Start rolling update of production app servers in us-west1-a"
echo "--------------------------------"
gcloud compute instance-groups managed rolling-action start-update docsearch-app-production-uswest \
        --version template=$NEW_APP_TEMPLATE_USWEST --zone us-west1-a

echo
echo "Start rolling update of production worker servers in us-west1-a"
echo "--------------------------------"
gcloud compute instance-groups managed rolling-action start-update docsearch-worker-production-uswest \
        --version template=$NEW_WORKER_TEMPLATE_USWEST --zone us-west1-a



# # us-east

# echo "Deploying to US-EAST"

# gcloud beta compute --project=redislabs-university instance-templates \
# create-with-container $NEW_APP_TEMPLATE \
# --machine-type=e2-medium \
# --network=projects/redislabs-university/global/networks/docsearch \
# --network-tier=PREMIUM \
# --metadata=google-logging-enabled=false \
# --can-ip-forward \
# --maintenance-policy=MIGRATE \
# --service-account=$SERVICE_ACCOUNT \
# --scopes=https://www.googleapis.com/auth/devstorage.read_only,https://www.googleapis.com/auth/logging.write,https://www.googleapis.com/auth/monitoring.write,https://www.googleapis.com/auth/servicecontrol,https://www.googleapis.com/auth/service.management.readonly,https://www.googleapis.com/auth/trace.append \
# --image=cos-stable-81-12871-1196-0 \
# --image-project=cos-cloud \
# --boot-disk-size=10GB \
# --boot-disk-type=pd-standard \
# --boot-disk-device-name=$US_WEST_DISK \
# --container-image=$APP_TAG \
# --container-restart-policy=always \
# --container-mount-host-path=mount-path=/data,host-path=/var/data/redis,mode=rw \
# --container-env-file ./.env.prod.useast \
# --labels=container-vm=cos-stable-81-12871-1196-0


# echo "Creating new worker instance template $NEW_WORKER_TEMPLATE from $WORKER_TAG"
# gcloud beta compute --project=redislabs-university instance-templates \
# create-with-container $NEW_WORKER_TEMPLATE \
# --container-image $WORKER_TAG \
# --machine-type=e2-medium \
# --network=projects/redislabs-university/global/networks/docsearch \
# --network-tier=PREMIUM \
# --metadata=google-logging-enabled=false \
# --can-ip-forward \
# --maintenance-policy=MIGRATE \
# --service-account=$SERVICE_ACCOUNT \
# --scopes=https://www.googleapis.com/auth/devstorage.read_only,https://www.googleapis.com/auth/logging.write,https://www.googleapis.com/auth/monitoring.write,https://www.googleapis.com/auth/servicecontrol,https://www.googleapis.com/auth/service.management.readonly,https://www.googleapis.com/auth/trace.append \
# --image=cos-stable-81-12871-1196-0 \
# --image-project=cos-cloud \
# --boot-disk-size=10GB \
# --boot-disk-type=pd-standard \
# --boot-disk-device-name=$US_WEST_DISK \
# --container-restart-policy=always \
# --container-mount-host-path=mount-path=/data,host-path=/var/data/redis,mode=rw \
# --container-env-file ./.env.prod.useast \
# --labels=container-vm=cos-stable-81-12871-1196-0


# echo
# echo "Start rolling update of production app servers in us-east4-c"
# echo "--------------------------------"
# gcloud compute instance-groups managed rolling-action start-update docsearch-app-production-useast \
#         --version template=$NEW_TEMPLATE --zone us-east4-c

# echo
# echo "Start rolling update of production worker servers in us-east4-c"
# echo "--------------------------------"
# gcloud compute instance-groups managed rolling-action start-update docsearch-worker-production-useast \
#         --version template=$NEW_WORKER_TEMPLATE --zone us-east4-c


# mumbai
echo "Deploying to MUMBAI"

gcloud beta compute --project=redislabs-university instance-templates \
create-with-container $NEW_APP_TEMPLATE_MUMBAI \
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
--container-image=$APP_TAG \
--container-restart-policy=always \
--container-mount-host-path=mount-path=/data,host-path=/var/data/redis,mode=rw \
--container-env-file ./.env.prod.mumbai \
--labels=container-vm=cos-stable-81-12871-1196-0


echo "Creating new worker instance template $NEW_WORKER_TEMPLATE_MUMBAI from $WORKER_TAG"
gcloud beta compute --project=redislabs-university instance-templates \
create-with-container $NEW_WORKER_TEMPLATE_MUMBAI \
--container-image $WORKER_TAG \
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
--container-restart-policy=always \
--container-mount-host-path=mount-path=/data,host-path=/var/data/redis,mode=rw \
--container-env-file ./.env.prod.mumbai \
--labels=container-vm=cos-stable-81-12871-1196-0



echo
echo "Start rolling update of production app servers in asia-south1-c"
echo "--------------------------------"
gcloud compute instance-groups managed rolling-action start-update docsearch-app-production-mumbai \
        --version template=$NEW_APP_TEMPLATE_MUMBAI --zone asia-south1-c

echo
echo "Start rolling update of production worker servers in asia-south1-c"
echo "--------------------------------"
gcloud compute instance-groups managed rolling-action start-update docsearch-worker-production-mumbai \
        --version template=$NEW_WORKER_TEMPLATE_MUMBAI --zone asia-south1-c


# zurich
echo "Deploying to ZURICH"

echo "Creating new app instance template $NEW_WORKER_TEMPLATE_ZURICH from $WORKER_TAG"
gcloud beta compute --project=redislabs-university instance-templates \
create-with-container $NEW_APP_TEMPLATE_ZURICH \
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
--container-image=$APP_TAG \
--container-restart-policy=always \
--container-mount-host-path=mount-path=/data,host-path=/var/data/redis,mode=rw \
--container-env-file ./.env.prod.zurich \
--labels=container-vm=cos-stable-81-12871-1196-0


echo "Creating new worker instance template $NEW_WORKER_TEMPLATE_ZURICH from $WORKER_TAG"
gcloud beta compute --project=redislabs-university instance-templates \
create-with-container $NEW_WORKER_TEMPLATE_ZURICH \
--container-image $WORKER_TAG \
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
--container-restart-policy=always \
--container-mount-host-path=mount-path=/data,host-path=/var/data/redis,mode=rw \
--container-env-file ./.env.prod.zurich \
--labels=container-vm=cos-stable-81-12871-1196-0


echo
echo "Start rolling update of production app servers in europe-west6-a"
echo "--------------------------------"
gcloud compute instance-groups managed rolling-action start-update docsearch-app-production-europe  \
        --version template=$NEW_APP_TEMPLATE_ZURICH --zone europe-west6-a

echo
echo "Start rolling update of production worker servers in europe-west6-a"
echo "--------------------------------"
gcloud compute instance-groups managed rolling-action start-update docsearch-worker-production-europe  \
        --version template=$NEWNEW_APP_TEMPLATE_ZURICH --zone europe-west6-a
