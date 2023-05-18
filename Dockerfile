FROM python:3.10-bullseye
USER root

ENV POETRY_VERSION 1.4.1
# Clean up APT when done.
RUN apt-get update && \
    apt-get -y install \
        build-essential \
        zlib1g-dev \
        libssl-dev \
        libffi-dev \
        git \
        curl \
        wget \
        gcc \
        gfortran \
        libpq-dev \
        libbz2-dev \
        liblzma-dev \
        postgresql-client --no-install-recommends && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUN pip3 install --upgrade pip
RUN pip3 install --no-cache-dir poetry==$POETRY_VERSION \
    && poetry config virtualenvs.create false

ENV NIKE_LAB222_PROJECT knockoff-factory
RUN mkdir -p /opt/nike-lab222/$NIKE_LAB222_PROJECT/
WORKDIR /opt/nike-lab222/$NIKE_LAB222_PROJECT/
COPY . /opt/nike-lab222/$NIKE_LAB222_PROJECT/

###########
RUN wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add - \
    && echo 'deb http://apt.postgresql.org/pub/repos/apt/ bionic-pgdg main' | tee /etc/apt/sources.list.d/pgdg.list
############
RUN poetry install --extras complete \
     && poetry cache clear --all .
