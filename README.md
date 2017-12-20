# Tornado Web Sockets + Celery Tasks
This repository is an example implementation of [Tordado](http://www.tornadoweb.org/en/stable/)
websockets used in conjuction with [Celery](http://www.celeryproject.org/) tasks.
This particular implementation uses [Redis](https://redis.io/) as the Celery message broker.

In the (trivial) example, a user can select two numbers from a dropdown and calculate
the total. The calculation is sent to a "long-running" task. Once the task completes,
a chain of yields and futures resolve and the value is sent via Websockets to the
UI.

## Usage
I've included a [Docker](https://www.docker.com/) configuration for this example.

Assuming you have Docker (and [Docker Compose](https://docs.docker.com/compose/)),
simply run `docker-compose up`.
