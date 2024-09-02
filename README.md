# hotbot

> Copyright BoundCorp 2023

## Running the Dev Environment

We've setup a few quality-of-life utilities in the `bin/` folder to make running the dev environment easier.

For convenience, you can find aliases for common tasks in the `Makefile`.

### Direnv and .envrc

It is highly recommended to install the [direnv](https://direnv.net/) utility. This will automatically load the
environment variables in the `.envrc` file when you `cd` into the project directory.

### Installing Dependencies

`make deps` will run `bin/setup.dev`, which:

+ Creates a new virtualenv (probably in `./.venv/`)
+ Installs the python dependencies from `pyproject.toml` (and updates `requirements.freeze.txt`)
+ (in `hotbot/views/`) Installs the frontend npm dependencies from `package.json` using `yarn`
+ Builds development docker containers for the backend
+ Launches the docker containers

```bash
make deps
```

## Running the project

If you just ran `make deps` above, it should have started the project for you.

If not, you can run `dcleanup` to cleanly start the project (or a specific container) at any time.
`dcleanup` is a helper for running `docker compose kill`, `docker compose rm -f`, and `docker compose up -d` in order,
followed by `docker compose logs -f` (which can safely be terminated without stopping the containers).

Now you can run `dc ps` to see the running containers:

```bash
$ dc ps

NAME                 SERVICE             CREATED             STATUS              PORTS
hotbot-backend-1   backend             3 seconds ago       Up 1 second         8000/tcp
hotbot-ingress-1   ingress             2 seconds ago       Up 1 second         443/tcp, 2019/tcp, 0.0.0.0:3388->80/tcp, :::3388->80/tcp
hotbot-psql-1      psql                3 seconds ago       Up 2 seconds        5432/tcp
```

Great! Now just run `bin/browser` to open the application in your browser
(or click here http://localhost:3388)

### Why Docker and Pipenv Together?

It may seem redundant to use both Docker devcontainers and local Pipenv, but there are a few reasons why we do this:

+ For many developer commands, starting the application with a local `Pipenv` is much faster than using the devcontainer
+ However the local `Pipenv` is not able to connect to `psql` or `redis` docker containers (without some extra setup,
  not performed here)
+ The devcontainer is able to connect to the `psql` and `redis` containers, but is slower to start
+ Many external commands (such as `flake8` and `manage.py test`) can be run from the local `Pipenv` without starting the
  devcontainer
+ The entire git precommit hook must be run from the local `Pipenv` (because `docker compose exec` does not work in a
  git hook due to TTY issues)

### .envrc Variables Explained

This project uses .envrc to load the virtual environment and expose several key variables, including the following
defaults:

```
export CI_PROJECT_NAME=hotbot # Used to name the docker image and docker-compose application
export CI_REGISTRY_IMAGE=gitlab.com/boundcorp/hotbot # Docker registry for helm deployments
export PYTHON_VERSION=3.10 # 
export DEVELOP_BACKEND_PORT=8833 # Port for the backend to run on - not exposed by default, check compose/dev.yml
export DEVELOP_INGRESS_PORT=3388 # USE THIS PORT - Caddy ingress port (proxies traffic to minio and backend)
export KUBE_CLUSTER=hotbot # Change this to whatever your kubectl cluster context is named
export SECRET_KEY=123_development_key # You can leave this as unsafe garbage in development, but secure it for production
export ROLE=dev # Used to determine which docker-compose file to use, check compose/dev.yml and compose/prod.yml
export PATH=$(pwd)/bin:$PATH # Add the bin folder to the path so we can use the utilities by name
export PROJECT_KUBECONFIG=$HOME/.kube/clusters/$KUBE_CLUSTER # used by bin/kx_gke to set the kubeconfig context
```

## Cookiecutter

This project was built using
the [boundcorp/cookiecutter-django-mountaineer](https://github.com/boundcorp/cookiecutter-django-mountaineer) template.
