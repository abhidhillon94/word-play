# Word Play
### An backend that exposes APIs to ingest paragraphs of text from metaphorpsum.com into the system, provide ability to perform full text search on the text in various ways and find the definitions of these words from dictionaryapi.dev.

## Requirements

Create an API with the following 3 endpoints:
- get/
    - Fetch a paragraph and store it
    - No params are needed.
    - When this endpoint is hit, it should fetch 1 paragraph from http://metaphorpsum.com/ with 50 sentences and store it in a persistent storage layer and return it.
- search/
    - search through stored paragraphs
    - allow providing multiple words and one of the two operators: 'or' or 'and'
        -“one”, “two”, “three”, with the “or” operator should return any paragraphs that have at least one the words “one”, “two” or “three”
        -“one”, “two”, “three”, with the “or” operator should return paragraphs that have all the words “one”, “two” or “three”
- dictionary/
    - Should return the definition of the top 10 words (frequency) found in the all the paragraphs currently store in the system.
    - Word definition should retrieved from https://dictionaryapi.dev/

## Technologies used
- MongoDb for persistent storage.
- Elasticsearch to index the data that can be searched.
- Python for the backend. Libraries and dependencies are listed:
    - Flask to run the HTTP server
    - Celery to run the background/async jobs worker
    - Redis as broker for celery and to perform rate limiting on external APIs in a horizontally scalabale environment running multiple instances of the API servers or background/async task wrokers.
    - python-dotenv to conviniently manage the environment variables across various environments
    - elasticsearch to integrate with elasticsearch
    - mongoengine to integrate with MongoDB

## Steps to run the system locally
- Install docker and docker-compose. Follow the installation instructions [here](https://docs.docker.com/compose/install/) depending on your platform (Linux, Mac, Windows)
- Make sure that you have git installed.
- Checkout the github repo on your machine by running the following command:
    ```sh
    git clone git@github.com:abhidhillon94/word-play.git
    ```
- In the root of the repo, clone build.env to a new file named .env. It contains environment variables that need to be passed to docker-compose to set up mongoDB, elasticsearch and redis. All of these variables expose the standard ports of each service for this setup on the host. You can choose to change the ports binding in case you already have any of the services/tools mentioned here running on your machine.
- Use docker-compose to set up all of the services required to run this app by running the following command from the root of the repo:
    ```sh
    docker-compose up
    ```
- The API endpoints would be accessible on http://localhost:5000 by default. Explore the endpoints using this [postman collection](https://drive.google.com/file/d/12VcrAEyb0Qg93Kcjv0RCpmVNAMstx1YO/view?usp=drive_link). This collection can be downloaded and imported in the postman app. However, since the app is really straightforward with the just 3 endpoints as mentioned in the beginning, you can simply hit those endpoints to see the results. If any API required parameters, you would clearly know it by looking at the error reponse of the API if you don't provide it.

## Steps to run the backend app outside of docker container:

- install pipenv to isolate the dependencies in a virtual environment of this repo by running the following command.
    ```sh
    pip install pipenv
    ```
- Switch to the pipenv shell by running the following command from the root of the repository.
    ```sh
    pipenv shell
    ```
- Install the dependencies in your virtual environment by running the following command:
    ```sh
    pipenv install
    ```
- Run the following command to run the unit test cases.
    ```sh
    python -m unittest discover tests/unit -p '*_test.py'
    ```
    Make sure to run them as you make any changes in order to find out if any code change broke any functionality. Please note that you do not need any dependecies like Elasticsearch, MongoDB or redis running on the system in order to run the unit tests since unit tests are completely independent.
- While we run web and worker processes out side of docker container, we can still choose to run other components like redis, MongoDB and elasticsearch using docker compose up. To proceed, please comment out the api and worker service sections from the docker-compose.yml file on line 55 and 73. You can choose to run kibana by uncommenting the kibana service section that starts on line 21 in docker-compose.yml if you need to inspect data in elastic search using an interctive UI. Copy the contents of env.example to .env file (please note it's not build.env unlike last step). All of the hostnames point to the localhost in this file (instead of virtual hostnames of the services in docker-compose environment) and that's how we need it if we run the api and worker outside of docker network since docker's virtual hostnames (mentioned in build.env) would not be accessible here. After the aforementioned steps, start the services on which our backend app and worker depend using the following command:
    ```sh
    docker-compose up
    ```
- Run the following command to start the API server that serves your APIs:
    ```sh
    python app.py
    ```
- Open a separate terminal tab/window to run the background job worker. Run the following command to start the celery process that serves as background/async task worker:
    ```sh
    pipenv shell
    celery --app src.jobs.precompute_words_count.celery  worker --loglevel=info --logfile=logs/celery.log -E
    ```

## Insights into code structure:
- The entry point of the code is app.py file in the root directory of the repo.
- All of the code resides in src directory and split into the following subdirectories:
    - controllers: It contains files that are starting point for the APIs. We have used flask blueprint to manage and define the routes. This is the layer that contains our input sanitization and validation logic, response formatting logic and calls to our service layer that contains the core business logic.
    - services: Files in this directory contains the core business logic of our application. It also includes database interaction/queries since our codebase is quite small and we use mongoEngine ODM that makes querying easier eliminating the need to have a repository layer at this point. We can consider moving the database operations out of this layer into repository layer if the codebase grows or if we feel the need to have reusable database operations/queries.
    - models: This direectory contains classes/entities that represent the documents in our database. Each model currently also maps to a collection in the database and the classes present in this layer also provide interface to perform database operations on the corresponding collections.
    - jobs: This directory contains our async/background jobs that are currently being run using celery workers. These jobs are long running tasks that we want to perform in a separate process outside of the API server process to reduce the latency of the APIs.
    - bootstrap_resources: This directory contains logic to setup any shared resources like MongoDB or Elasticsearch connections and operations that we usually do while bootstraping the application process.
- Our test cases reside in the tests directory available in the root of the repo. We currently have only unit test cases in the unit subdirectory here. Integration test cases will be added to the integration subdirectory.

## Limitations and scope of improvement:
This app is nowhere close to production ready in the current state and the sole purpose of this code is to demonstrate knowledge of python, various tools and their usage. In the interest of time, the following features/implementation/improvments have not been done:
- We currently index the paragraph content in elastic search from our application which is not reliable. The original system design included usage of [mongo-connector](https://pypi.org/project/mongo-connector/) to sync data from MongoDB to elastic search. Due to this, we currently do not have a mechanism to perform initial seeding of the data in elasticsearch if our MongoDB has data that elasticsearch doesn't. If an elastic search index is deleted, the initial sync of data can not be done at the moment.
- Some of the files in the bootstrap_resources directory do not have a function to bootstrap or create a resource. This makes the code run during module imports which makes the order of imports significant and not something that we want. I plan to add functions to initialise resources in each file and make a single function to bootstrap the resources that can be called from the entry points of the API server, async/background worker or test cases.
- From the security aspect, the system has been set up to optimise for easier local container based deployment. We have disabled the security on elasticsearch to reduce the scope of work.
- The external API calls to fetch paragraphs and dictionary would ideally be rate limited. We should have rate limiting in place to deal with it exceeding our rate limits. Redis can be utilised for the same.
- There are few IO operations like database access and external API calls that can be performed in a non blocking manner by usage of Asyncio or threading.
- Usage of app.logger for logging to log instead of print statements. We have very few logs at the moment that are mostly logged during application startup. Hence we choose not to set up the logging config in order to use app.logger.
- Our async tasks processing system is currently being run in it's implest form. We have not configured retry in it. Usage of DLQ or ability to retry failed celery jobs round and to track failed jobs so that we can formulate a plan to retry failed maessges needs to be added.
- The celery worker currently uses redis broker for demonstration purpose. This is not an ideal choice for high traffic and redis needs to be configrued with AOF backups in order to make the messages persistent/durble across crashes or restarts. However, we can easily switch to any other broker with minimal changes in the code but we do not want to set up the infra right now in order to prevent application from being too heay by running too many containers. Redis is an optimal choice for now since it has multiple usages in the app in near future like rate limiting.
- Usage of a tool like supervisorD to run the celery worker in a reliable manner.
- Observability of the infra and all of the components needs to be added.
- Our flask server is currently being run only for the purpose of debugging. We need to use a production WSGI server like waitress or gevent.
- There are no healthchecks for any of the services at the moment for demo purpose. Those need to be added in order to imporve our deployment stability.
- Integration test cases have not been written so far. We only have unit test cases. The reasoning here is to display ability to write good unit test cases as that's harder than integration test cases considering requirement to mocking lot more functions/modules unlike integration testing where you only need to mock the external dependencies like DBs and external API calls.
- Our elasticsearch runs as a single node server for demonstration purpose which should ideally run a as a multi node cluster to reap all of the benefits. Same goes for mongoDB as well.
- We use a basic english language analyzer for word stemming in elastic search for demonstration purpose of how we can smartly index subset of data instead of the entire data. While it is better than the standard analyzer, we still need to configure our own anlyzer for production grade use cases.
- Pagination capability can be added to the /search API to limit the results returned by the API that would help with performance in multiple ways. Pagination requirement has not been mentioned in the requirements though.
- We haven't set up indexes in MongoDB or supported replication or sharding for this demo. However, the technical choices made here make this job only an incremental effort.
- Some non critical passwords to speed up the process of local environment setup have been checkin to the repo in .env files. This was a concious choice to avoid having to share the .env files separately for this specific instance.


## Assumptions:
- The problem statement states that the /dictionary API should return the definition of the top 10 words by frequency. We have assumed that the frequency is computed by considering the occurances of the words only once in a single paragraph. For example, if a word appears 2 time in paragraph 1 and 5 times in paragraph 2, the total occurance assumed would be 2. This is done to avoid getting common filler words in the top words.
- We have assumed that variations of a single word in singular/plural format or with change in tenses shoudln't be considered as separate words. We reduce words to their root form for frequency calculation. We are currently using the english language analyzer in elasticsearch to reduce the word but we can choose to extend it with custom dictionaries of stop words and filler words and algorithms related to word reduction for real production usage.
- We have assumed that it's fine for the dictionary API to return eventul consistent data or the words frequency computation to not be realtime. However, it is near realtime.
