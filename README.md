# redis-sitesearch

## About

redis-sitesearch is a package that indexes web sites into RediSearch.

RediSearch was originally developed by Redis Labs to provide a search API for our documentation. You can see it live at: https://docs.redislabs.com.

## Installing

The development environment is provided as a Docker container. Running and deploying it all involve using Docker, and this section describes how to do so.

**Note**: If you desire not to use Docker, you can reverse-engineer the installation steps from the Dockerfile and docker-compose.yml file.

### Docker Requirements

This project was built and tested using the following Docker and docker-compose versions:

Docker version 19.03.13, build 4484c46d9d
docker-compose version 1.27.4, build 40524192

Ensure you are running at least these versions before you continue.

### .env files

The app is configured using environment variables, so you'll need two different `.env` files depending on what you want to do:

- `.env`: Environment variables for local development
- `.env.prod`: Environment variables to deploy to production

Examples are included, which you can copy from `.env.example` to `.env` and from `.env.prod.example` to `.env.prod`.

### Virtualenv

If you want code completion to work in an IDE, or you want to run commands outside of Docker (like `pytest`), create a virtualenv:

        python 3.8 -m venv env

Then you can run the following to activate your virtualenv:

        source env/bin/activate

**Note**: This project was built with and is only tested to work on Python 3.8.

### Run docker-compose up

After you have the necessary Docker software, "install" the app with `docker-compose`:

        docker-compose up --build

This command builds the necessary images and brings up the app.

## Developing

Assuming you have already brought up the app with `docker-compose up` per the installation instructions, this section describes things to know about for local development.

### Writing Code

Once the application is running, you can write code using a local text editor, and your changes will sync to the container over a volume mount.

The WSGI server running the app is set to reload when code changes, so if you have `docker-compose up` running (so you can see output), and you change code in the project, you will see output about workers being "reaped."

This is well and good -- they are restarting.

### Tests

To run tests, use this command:

        docker-compose run test

This runs `pytest` within the container.

If you have a `.env` file, you can run `pytest` locally (after you've activated your virtualenv), and the tests will pick up the necessary environment variables from your `.env` file.

### Local vs. Docker redis

The redis instance that this project's container starts exposes the default redis port locally (6379). So, after you run `docker-compose up` you can connect to redis outside of the Docker container on that port.

However, note that this won't work if you're already running redis locally on the default port -- so make sure you stop that if you want to connect to the redis running on Docker.

## Deploying

This project includes a deployment script for Google Cloud Platform that is specific to Redis Labs' deployment.

If you want to use this script to deploy, follow these steps:

1. Install the [Cloud SDK](https://cloud.google.com/sdk)
2. Authenticate and select the appropriate project (ask Education for access!)
3. Make sure you have a `.env.prod` file -- this is important, and deploying will fail without it
4. Make sure you've committed your local changes
5. Run the deployment script: `./deploy.sh`

The deployment script does the following:

1. Builds a new image based on the code in your working directory, which includes the git hash as part of the tag
2. Pushes the image to Google Container Registry
3. Creates a new instance template using the image and the contents of your .env.prod -- all env vars there will be sent to containers run from that template
4. Starts a rolling update in our production regions: US-West (us-west-1a), Mumbai (asia-south-1c), and Zurich (europe-west6-a)

When the rolling update completes, the script will terminate.

However, the rolling update is not technically complete. Each search node will reindex as it comes online, and the new node's health check will only succeed once that completes, in about **20 minutes**.

Until the update completes, the past version of the search service remains available.

## Questions

If you have any questions, ask the Education team!
