# redis-sitesearch

## About

redis-sitesearch is a package that indexes web sites into RediSearch.

<img src="images/redisearch.png" width="200">

RediSearch is a querying and indexing engine for Redis that supports full-text search. You can read more about it here: https://oss.redislabs.com/redisearch/

redis-sitesearch was originally developed by Redis Labs to provide a search API for our documentation. You can see it live at: https://docs.redislabs.com.

**Want to learn more?** Join the [Redis discord](https://discord.gg/yEbfGhqhsz) to meet other Redis and RediSearch users.

## Installing

The development environment is provided as a Docker container. Running and deploying it all involve using Docker, and this section describes how to do so.

**Note**: If you want to avoid using Docker, you can try to reverse-engineer the installation steps from the Dockerfile and docker-compose.yml file.

### Docker Requirements

This project was built and tested using the following Docker and docker-compose versions:

Docker version 19.03.13, build 4484c46d9d
docker-compose version 1.27.4, build 40524192

Ensure you are running at least these versions before you continue.

### Environment Variables

The app is configured using environment variables. For local development, you'll need a `.env` file, from which the app will read environment variables.

An example is included, which you should copy from `.env.example` to `.env` from the root directory of the repository:

        cp .env.example .env

**Deployment note**: If you deploy redis-sitesearch to Google Cloud Platform using the deploy.sh script, the script expects to configure environment variables from a .env.prod file. If you deploy to Amazon Lightsail, you need to configure environment variables in the Lightsail GUI.

### Redis Password-protection

This application expects to use a password to authenticate with Redis. The .env.example file includes the required environment variable, `REDIS_PASSWORD`.

In local development, running `docker-compose up` will start Redis in password-required mode using the password you set in the `REDIS_PASSWORD` environment variable, and the app will connect using that password. So, for local development, you shouldn't have to think about the password.

To connect to Redis using `redis-cli`, use the `-a` command-line flag or the `AUTH` command and enter the password from your .env file (or the password you manually set in the `REDIS_PASSWORD` environment variable, if you didn't use the .env file).

In production, the app will use whatever password you configure in the production environment's `REDIS_PASSWORD` environment variable.

### Virtualenv

If you want code completion to work in an IDE, or you want to run commands outside of Docker (like `pytest`), create a virtualenv:

        python 3.8 -m venv env

Then you can run the following to activate your virtualenv:

        source env/bin/activate

Finally, install dependencies:

        pip install -r requirements.txt

**Note**: This project was built with and is only tested to work on Python 3.8.

### Run docker-compose up

After you have the necessary Docker software, "install" the app with `docker-compose`:

        docker-compose up --build

This command builds the necessary images and brings up the app.

### Indexing Documents

As soon as the app finishes starting up, it begins indexing sites configured in the `DEV_SITES` dictionary in the file `sitesearch/config.py`.

You should see output like this, indicating that supervisor started the processes:

```
worker_1   | 2021-01-12 21:17:51,091 INFO success: worker entered RUNNING state, process has stayed up for > than 1 seconds (startsecs)
app_1   | 2021-01-12 21:17:51,092 INFO success: app entered RUNNING state, process has stayed up for > than 1 seconds (startsecs)
scheduler_1   | 2021-01-12 21:17:51,095 INFO success: scheduler entered RUNNING state, process has stayed up for > than 1 seconds (startsecs)
```

* The "app" process is the Python search API
* The "worker" process is an RQ worker that will process any indexing tasks it sees
* The "scheduler" worker is a process that runs an indexing task every 60 minutes

You will also see output from a Redis container.

You might see errors and warnings as the indexing job proceeds, like this:

```
worker_1   | 2021-01-12 21:18:07 [sitesearch.indexer] ERROR: Document parser error -- Could not find breadcrumbs: https://docs.redislabs.com/latest/
worker_1   | 2021-01-12 21:18:08 [sitesearch.indexer] ERROR: Document parser error -- Skipping 404 page: https://docs.redislabs.com/latest/404.html
```

This output is normal -- some pages don't have breadcrumbs, and we skip 404 pages. Other times, the scraper encounters PDF or other non-HTML files and gives up trying to index them.

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

        docker-compose exec app pytest -s

This runs `pytest` within the app container.

If you have a `.env` file, you can run `pytest` locally (after you've activated your virtualenv), and the tests will pick up the necessary environment variables from your `.env` file.

**NOTE**: The .env.example file in this repository configures the app to look at the Docker host for the Redis container, which is `redis`. To run the app and/or tests outside of Docker, you'll need to change the `REDIS_HOST` environment variable to "localhost".

### Local vs. Docker redis

The Redis container that this project starts runs on port 6379 _within Docker_. If you want to connect to it from tools like redis-cli on your localhost, you can do so using port 16379.

The app uses port 16379 to avoid conflicting with any Redis instances running on the default port on localhost.

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
