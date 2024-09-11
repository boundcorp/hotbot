ARG image_version=python:3.10.9

#
#
# Base stage
FROM ${image_version} AS base

ENV PATH=/app/.venv/bin:$PATH
ENV LANG=C.UTF-8
ENV PYTHONUNBUFFERED=1

RUN apt update -yq && apt install -yq \
    libpq-dev \
    libjpeg-dev \
    libcurl4-openssl-dev \
    bash \
    libxml2-dev \
    libxslt-dev \
    curl 

RUN pip install --no-cache-dir --upgrade pipenv pip uv poetry setuptools

# GeoDjango dependencies - commented out to keep the image lightweight, but easy to add
# from: https://stackoverflow.com/questions/58403178/geodjango-cant-find-gdal-on-docker-python-alpine-based-image

# RUN apk add --no-cache --upgrade postgresql-client libpq \
#      && apk add --no-cache --upgrade --virtual .build-deps postgresql-dev zlib-dev jpeg-dev alpine-sdk \
#      && apk add --no-cache --upgrade geos proj gdal binutils

# RUN ln -s /usr/lib/libproj.so.25 /usr/lib/libproj.so \
#    && ln -s /usr/lib/libgdal.so.31 /usr/lib/libgdal.so \
#    && ln -s /usr/lib/libgeos_c.so.1 /usr/lib/libgeos_c.so

#ENV GDAL_LIBRARY_PATH='/usr/lib/libgdal.so'

#
#
# Builder stage
FROM base AS builder

RUN apt update -yq && apt install -yq \
    netcat gcc python3-dev libpq-dev libxml2-dev libxslt-dev \
    libcurl4-openssl-dev libssl-dev libffi-dev curl

# Copy only requirements file first to leverage Docker cache
COPY requirements.freeze.txt /app/

WORKDIR /app
RUN uv venv /app/.venv
ENV PATH=/app/.venv/bin:$PATH
RUN . /app/.venv/bin/activate

# Copy the rest of the application
COPY pyproject.toml README.md /app/
COPY hotbot/ /app/hotbot
COPY infra /app/infra

# Install the application
RUN uv pip install -e .



#
#
# Release
FROM base AS release

RUN apt update -yq && apt install -yq libfreetype6-dev libjpeg62-turbo-dev libpng-dev

COPY --from=builder /app /app
COPY --from=builder /app/.venv /app/.venv
COPY hotbot/ /app/hotbot
COPY scripts/ /app/scripts
COPY infra /app/infra
COPY manage.py /app/
RUN mkdir -p /app/frontend

WORKDIR /app
RUN mkdir -p /app/static/uploads && chmod 777 /app/static/uploads
RUN chmod -R 777 /app/.venv/lib/python3.10/site-packages/mountaineer/views/
ENV PATH=/app/.venv/bin:$PATH
RUN /app/.venv/bin/python manage.py collectstatic --noinput
ENV PYTHONSTARTUP=/app/.pythonrc


#
#
# Developer image stage - ubuntu based instead of alpine
FROM ${image_version} AS dev

ENV LANG C.UTF-8
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH=/app:$PYTHONPATH
ENV PYTHONSTARTUP=/app/.pythonrc
ENV PYTHONHISTORY=/app/.python_history

RUN apt update -yq && apt install -yq \
    netcat gcc python3-dev libpq-dev libxml2-dev libxslt-dev \
    libcurl4-openssl-dev libssl-dev libffi-dev curl

RUN pip install --no-cache-dir --upgrade pipenv pip poetry uv setuptools \
    && mkdir /app

# postgis dependencies - uncomment for postgis in development
# RUN apt install -yq libgdal-dev libproj-dev

WORKDIR /app

# In dev, pipfile is installed with --system, so it persists even if we mount /app from outside
ENV VIRTUAL_ENV=/venv
RUN uv venv /venv

ENV NODE_VERSION=v18.17.1
RUN apt install -y curl socat
ENV NVM_DIR=/nvm
RUN mkdir -p $NVM_DIR
RUN curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
RUN . "$NVM_DIR/nvm.sh" && nvm install ${NODE_VERSION}
RUN . "$NVM_DIR/nvm.sh" && nvm use ${NODE_VERSION}
RUN . "$NVM_DIR/nvm.sh" && nvm alias default ${NODE_VERSION}
ENV PATH="${NVM_DIR}/versions/node/${NODE_VERSION}/bin/:/venv/bin/:${PATH}"
RUN node --version
RUN npm --version
RUN npm install --global yarn

# symlink yarn because it won't be on the path when we change UID/GID!
RUN ln -sf /root/.nvm/versions/node/${NODE_VERSION}/bin /usr/yarn

COPY pyproject.toml README.md /app/
RUN . /venv/bin/activate
# install the dependencies
RUN uv pip install -r /app/pyproject.toml
RUN chmod -R 777 /venv/lib/python3.10/site-packages/mountaineer/views/

# now install the package
COPY hotbot/ /app/hotbot
COPY infra /app/infra
RUN uv pip install -e .

#
#
# This make release the default stage
FROM release
