# OCEAN Decentralized Backend Storage

## Description
Initial repository implementing a solution for the Ocean Decentralized Backend storage management service [explained here](https://github.com/oceanprotocol/decentralized_storage_backend/issues/1)

It is a django-based solution benefitting from django-rest-framework for the class based API Views implementation and drf-spectacular for the Swagger based auto documentation of the API usage. 

## Badges
To Be Added after configuration of the CI on Github

## Installation
This is a server-side API based on Python and Django/DRF so first make sure you have python and pip installed.

First, clone this project in the appropriate location in your workspace.

Then, use virtualenv to isolate your development environment and setup the virtual env for this project: `python -m virtualenv venv`

The server can be run using the `./manage.py runserver` method from the `./server/` directory.

Tests can be launched using `./manage.py test`

You can create a superuser with `./manage.py createsuperuser` to be able to access the back-office on `http://localhost:8000/admin` by default or everything else you previously defined.

## Usage
You can navigate the API using the url `http://myserver.com/docs/` (Swagger based OpenAPI documentation, default on localhost:8000).

## ENVS

- DEBUG = False  (if we should enable debug mode in django)
- SECRET_KEY = secret key for django

# Dockerfile usage
You can also just build the available Dockerfile and run the server from there using the following commands:

```sh
docker build -t ocean-dbs .
docker compose up
```

## Support
Please open issues on github if you need support of have any questions.

## Roadmap
More integrations/services to be added.

## Contributing
This project is fully open-source, backed by the $OCEAN community and is obviously open for contributions.

The first version has been implemented following the TDD strategy, so please first familiarize yourself with the test suite, which can be run using the `./manage.py test` command, directly from the root of your server in the context of your virtual environment.

## Authors and acknowledgment
Thanks to the $OCEAN community for the funding and the $OCEAN core team for the technical support and insights.

## License
This project is delivered under an Apache License

## Additional projects
 - DBS Filecoin microservice (https://github.com/oceanprotocol/dbs_filecoin)
 - DBS Arweave microservice (https://github.com/oceanprotocol/dbs_arweave)
