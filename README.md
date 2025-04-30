# Sup de Vinci Travel Hub

Table of Contents

- [Sup de Vinci Travel Hub](#sup-de-vinci-travel-hub)
  - [Requirements](#requirements)
  - [Installation](#installation)
  - [Start the project](#start-the-project)
    - [Environment variables](#environment-variables)
    - [Locally](#locally)
    - [With docker](#with-docker)
  - [OpenAPI docs](#openapi-docs)
  - [Structure](#structure)

## Requirements

To run this project, you need to have python installed. If that is not the case, [download Python](https://www.python.org/downloads/).
This project also need access to :

- A Neo4J instance (you can get one for free with [Neo4J Aura](https://console.neo4j.io/))
- A MongoDB instance (you can get one cluster for free with [MongoDB Atlas](https://cloud.mongodb.com))
- A Redis instance (the `docker-compose.yml` starts one)

## Installation

A `docker-compose.yml` is available but if you want to install the project locally, use the following commands :

```bash
python3 -m virtualenv .venv
source ./.venv/bin/activate
pip install -r requirements.txt
```

## Start the project

### Environment variables

This project needs environment variables to run.
Take a look at `.env.example` to see the required variables.

### Locally

```bash
fastapi dev app/main.py
```

### With docker

```bash
docker compose up
```

The API will start and seed all the databases.

## OpenAPI docs

This is a FastAPI project, OpenAPI docs are accessible via `/docs` for Swagger and `/redoc` for Redoc.

## Structure

The structure is as follow :

```text
app
├── config.py
├── controllers
│   ├── cities.py
│   ├── __init__.py
│   ├── offers.py
│   └── recommendations.py
├── dependencies
│   ├── databases.py
│   ├── __init__.py
│   └── query_params.py
├── entities
│   ├── auth.py
│   ├── city.py
│   ├── __init__.py
│   ├── mongo.py
│   ├── offer.py
│   └── responses.py
├── helpers
│   ├── __init__.py
│   ├── json.py
│   ├── pydantic.py
│   └── query.py
├── __init__.py
├── logger.py
├── main.py
├── routers
│   ├── auth.py
│   ├── cities.py
│   ├── __init__.py
│   ├── offers.py
│   └── recommendations.py
└── seed.py
```

- `main.py`: entrypoint of the application and contains the api instance
- `config.py`: fetches the app config from the `.env` file or the environment if absent
- `logger.py`: logger
- `helpers` contains some reusable functions and types
- `controllers`: contains the routes logic
- `entities`: contains the pydantic model to describe incoming and outgoing data
- `routers` folder contains all routes divided per resource
- `dependencies` contains the pydantic models for dependency injection by FastAPI
