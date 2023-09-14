"""
Commands to deploy the application.

Deploying builds and pushes new app and worker images,
new instance templates that use the new images, and finally,
starts a rolling update of several managed instance groups
in Google Cloud Platform:

1. The docsearch-app-production-uswest instance group deployed in zone us-west1-a
2. The docsearch-worker-production-uswest instance group deployed in zone us-west1-a
3. The docsearch-app-production-europe instance group deployed in zone europe-west6-a
4. The docsearch-app-production-mumbai instance group deployed in zone asia-south1-c
5. The docsearch-app-production-useast instance group deployed in zone us-east4-c

There are a few things to note about this:

1. The Redis primary runs in us-west-a. Applications in other zones look at zone-local
   Redis replicas that replicate from the primary in us-west.
2. Only one worker instance group exists, and it writes to the Redis primary in us-west.
3. Every time we deploy a new version of the  application or worker, we have to create
   a new instance template that points to the new Docker image to use. This means we
   leave behind many stale templates -- and there is no automatic way to clean those up.
"""
import logging
import os
import random
import subprocess
import sys

import click
from dotenv import load_dotenv

load_dotenv()

log = logging.getLogger(__name__)

# Secrets must be loaded as environment variables.
REQUIRED_ENV = ('SERVICE_ACCOUNT', 'REDIS_HOST', 'REDIS_PASSWORD', 'NEW_RELIC_LICENSE_KEY', 'API_KEY')
for key in REQUIRED_ENV:
    if key not in os.environ:
        print(f"Hold up! Your environment is misconfigured. Please set the {key} environment "
              "variable and try again.", file=sys.stderr)
        exit(1)

HASH = subprocess.check_output("git rev-parse --short HEAD", shell=True).decode("utf-8").strip()
APP_TAG = f"gcr.io/redislabs-university/docsearch-app-production:{HASH}"
WORKER_TAG = f"gcr.io/redislabs-university/docsearch-worker-production:{HASH}"
SERVICE_ACCOUNT = os.environ.get('SERVICE_ACCOUNT', None)
DEFAULT_DISK = "docsearch-app-west-2"
RANDOM = random.randrange(1000)

REDIS_HOST = os.environ.get('REDIS_HOST')
REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD')
NEW_RELIC_LICENSE_KEY = os.environ.get('NEW_RELIC_LICENSE_KEY')
API_KEY = os.environ.get('API_KEY')
# TODO: Some or all of these should probably be configurable.
REDIS_PORT = 6379
KEY_PREFIX = 'sitesearch:dev'
ENV = 'production'
NEW_RELIC_MONITOR_MODE = 'on'
INSTANCE_GROUPS = {
    "docsearch-staging-app-west": "us-west1-a",
    "docsearch-app-production-uswest": "us-west1-a",
    "docsearch-worker-production-uswest": "us-west1-a",
    "docsearch-app-production-europe": "europe-west6-a",
    "docsearch-app-production-mumbai": "asia-south1-c",
    "docsearch-app-production-useast": "us-east4-c"
}

@click.command()
def build_images():
    print(f"Building {APP_TAG}...")
    subprocess.run(f"docker build -t {APP_TAG} . -f docker/app/Dockerfile", shell=True, check=True)

    print(f"Building {WORKER_TAG}...")
    subprocess.run(f"docker build -t {WORKER_TAG} . -f docker/worker/Dockerfile", shell=True, check=True)

    print("Pushing tags...")
    subprocess.run(f"docker push {APP_TAG}", shell=True, check=True)
    subprocess.run(f"docker push {WORKER_TAG}", shell=True, check=True)


def validate_instance_group(ctx, param, value):
    if value not in INSTANCE_GROUPS:
        raise click.BadParameter(f'Invalid instance group. Valid options are: '
                                 f'{", ".join(INSTANCE_GROUPS.keys())}')
    return value


@click.argument('instance-group', callback=validate_instance_group)
@click.option('--machine-type', default='e2-medium', help="The machine type to use", show_default=True)
@click.option('--build', default=False, help="Build and push application image?", show_default=False)
@click.option('--image', default='cos-97-16919-353-44', help="The GCP container OS image", show_default=True)
@click.option('--disk', default=DEFAULT_DISK, help="The GCP boot disk to use", show_default=True)
@click.option('--network', default='docsearch', help="The GCP network to use", show_default=True)
@click.command()
def deploy_app(instance_group, machine_type, build, image, disk, network):
    print(f"Deploying to {instance_group}")

    if build:
        build_images()

    zone = INSTANCE_GROUPS[instance_group]

    # We can't use the hash because a template could already exist
    # for the same git hash, so we always append a random integer.
    new_template = f"docsearch-app-production-{HASH}-{RANDOM}-{zone}"

    create_instance_template_cmd = f"""
        gcloud compute --project=redislabs-university instance-templates \
            create-with-container {new_template} \
            --machine-type={machine_type} \
            --network=projects/redislabs-university/global/networks/{network} \
            --network-tier=PREMIUM \
            --metadata=google-logging-enabled=false \
            --can-ip-forward \
            --maintenance-policy=MIGRATE \
            --service-account={SERVICE_ACCOUNT} \
            --scopes=https://www.googleapis.com/auth/devstorage.read_only,https://www.googleapis.com/auth/logging.write,https://www.googleapis.com/auth/monitoring.write,https://www.googleapis.com/auth/servicecontrol,https://www.googleapis.com/auth/service.management.readonly,https://www.googleapis.com/auth/trace.append \
            --image={image} \
            --image-project=cos-cloud \
            --boot-disk-size=10GB \
            --boot-disk-type=pd-standard \
            --boot-disk-device-name={disk} \
            --container-image={APP_TAG} \
            --container-restart-policy=always \
            --container-mount-host-path=mount-path=/data,host-path=/var/data/redis,mode=rw \
            --container-env=REDIS_HOST={REDIS_HOST},REDIS_PORT=6379,REDIS_PASSWORD={REDIS_PASSWORD},NEW_RELIC_LICENSE_KEY={NEW_RELIC_LICENSE_KEY},KEY_PREFIX={KEY_PREFIX},ENV={ENV},API_KEY={API_KEY},NEW_RELIC_MONITOR_MODE={NEW_RELIC_MONITOR_MODE} \
            --labels=container-vm=cos-97-16919-353-44
    """
    subprocess.run(create_instance_template_cmd, shell=True, check=True)

    message = f"Start rolling update of production app servers in {zone}"
    print(message)
    print("-" * len(message))
    rolling_update_cmd = f"""
        gcloud compute instance-groups managed rolling-action start-update {instance_group} \
                --version template={new_template} --zone {zone}
    """
    subprocess.run(rolling_update_cmd, shell=True, check=True)


@click.argument('worker-instance-group')
@click.option('--machine-type', default='e2-medium', help="The machine type to use", show_default=True)
@click.option('--build', default=False, help="Build and push application images?", show_default=False)
@click.option('--image', default='cos-97-16919-353-44', help="The GCP container OS image", show_default=True)
@click.option('--disk', default=DEFAULT_DISK, help="The GCP boot disk to use", show_default=True)
@click.option('--network', default='docsearch', help="The GCP network to use", show_default=True)
@click.command()
def deploy_worker(worker_instance_group, machine_type, build, image, disk, network):
    print(f"Deploying worker")

    if build:
        build_images()

    new_template = f"docsearch-worker-production-{HASH}-{RANDOM}"
    # We only deploy the worker to us-west.
    zone = "us-west1-a"

    create_instance_template_cmd = f"""
        gcloud --quiet beta compute --project=redislabs-university instance-templates \
            create-with-container {new_template} \
            --machine-type={machine_type} \
            --network=projects/redislabs-university/global/networks/{network} \
            --network-tier=PREMIUM \
            --metadata=google-logging-enabled=false \
            --can-ip-forward \
            --maintenance-policy=MIGRATE \
            --service-account={SERVICE_ACCOUNT} \
            --scopes=https://www.googleapis.com/auth/devstorage.read_only,https://www.googleapis.com/auth/logging.write,https://www.googleapis.com/auth/monitoring.write,https://www.googleapis.com/auth/servicecontrol,https://www.googleapis.com/auth/service.management.readonly,https://www.googleapis.com/auth/trace.append \
            --image={image} \
            --image-project=cos-cloud \
            --boot-disk-size=10GB \
            --boot-disk-type=pd-standard \
            --boot-disk-device-name={disk} \
            --container-image={WORKER_TAG} \
            --container-restart-policy=always \
            --container-mount-host-path=mount-path=/data,host-path=/var/data/redis,mode=rw \
            --container-env=REDIS_HOST={REDIS_HOST},REDIS_PORT=6379,REDIS_PASSWORD={REDIS_PASSWORD},NEW_RELIC_LICENSE_KEY={NEW_RELIC_LICENSE_KEY},KEY_PREFIX={KEY_PREFIX},ENV={ENV},API_KEY={API_KEY},NEW_RELIC_MONITOR_MODE={NEW_RELIC_MONITOR_MODE} \
            --labels=container-vm=cos-97-16919-353-44
    """
    subprocess.run(create_instance_template_cmd, shell=True, check=True)

    message = f"Start rolling update of production worker in {zone}"
    print(message)
    print("-" * len(message))
    rolling_update_cmd = f"""
        gcloud --quiet beta compute instance-groups managed rolling-action start-update {worker_instance_group} \
                --version template={new_template} --zone {zone}
    """
    subprocess.run(rolling_update_cmd, shell=True, check=True)
