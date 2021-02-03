# redis-sitesearch

## About

redis-sitesearch is a package that indexes web sites into RediSearch.

<img src="images/redisearch.png" width="200">

RediSearch is a querying and indexing engine for Redis that supports full-text search. You can read more about it here: https://oss.redislabs.com/redisearch/

redis-sitesearch was originally developed by Redis Labs to provide a search API for our documentation. You can see it live at: https://docs.redislabs.com.

**Want to learn more?** Join the [Redis discord](https://discord.gg/yEbfGhqhsz) to meet other Redis and RediSearch users.

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

### Redis Passwords

This application expects to use a password to authenticate with Redis. Both .env.prod.example and .env.example include the environment variable `REDIS_PASSWORD`.

In local development, running `docker-compose up` will start Redis in password-required mode with the password you set in the `REDIS_PASSWORD` environment variable from the `.env` file.

In production, the app will use the password from the `.env.prod` file.

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

### Indexing Documents

As soon as the app finishes starting up, it begins indexing site content.

You should see output like this, indicating that supervisor started the processes:

```
app_1   | 2021-01-12 21:17:51,091 INFO success: worker entered RUNNING state, process has stayed up for > than 1 seconds (startsecs)
app_1   | 2021-01-12 21:17:51,092 INFO success: app entered RUNNING state, process has stayed up for > than 1 seconds (startsecs)
app_1   | 2021-01-12 21:17:51,093 INFO success: redis entered RUNNING state, process has stayed up for > than 1 seconds (startsecs)
app_1   | 2021-01-12 21:17:51,095 INFO success: scheduler entered RUNNING state, process has stayed up for > than 1 seconds (startsecs)
```

* The "app" process is the Python search API
* The "worker" process is an RQ worker that will process any indexing tasks it sees
* The "scheduler" worker is a process that runs an indexing task every 60 minutes

You might see errors and warnings as the indexing job proceeds, like this:

```
app_1   | 2021-01-12 21:18:07 [sitesearch.indexer] ERROR: Document parser error -- Could not find breadcrumbs: https://docs.redislabs.com/latest/
app_1   | 2021-01-12 21:18:08 [sitesearch.indexer] ERROR: Document parser error -- Skipping 404 page: https://docs.redislabs.com/latest/404.html
```

This output is normal -- some pages don't have breadcrumbs, and we skip 404 pages.

#### Scheduled indexing

The app indexes on a schedule, every 60 minutes. So if you leave it running, it will reindex once per hour.

#### Manually indexing

While you work, you might want to reindex to test a change to the indexing process.

You have two options to force the app to reindex:
* Restart the app: `docker-compose restart`
* Manually trigger reindexing with the `index` CLI command: `docker-compose exec app index`

### New Relic

The Python app tries to use New Relic. If you don't specify a valid NEW_RELIC_LICENSE_KEY environment variable in your .env or .env.prod files, the New Relic Agent will log errors. This is ok -- the app will continue to function without New Relic.

```
app_1   | 2021-01-12 22:36:16,867 (61/NR-Activate-Session/sitesearch) newrelic.core.agent_protocol CRITICAL - Disconnection of the agent has been requested by the data collector for the application where the agent run was None. Please contact New Relic support for further information.
```

## Searching

The app maps localhost port 8080 to the search API. After you start the app with `docker-compose up`, can search using this URL:

        localhost:8080/search?q=<your search terms>

For example:

        $ curl localhost:8080/search?q=redis

Every response includes the total number of hits and a configurable number of results.

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
