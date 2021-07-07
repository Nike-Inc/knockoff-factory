FROM phusion/baseimage:bionic-1.0.0
CMD ["/sbin/my_init"]
USER root
ENV PYTHON_VERSION 3.7.7
ENV PYTHON_CONFIGURE_OPTS "--enable-shared"
ENV PYENV_ROOT "/pyenv"
ENV PATH "$PYENV_ROOT/bin:$PYENV_ROOT/shims:$PYENV_ROOT/versions/$PYTHON_VERSION/bin/:$PATH"
ENV PYENV_VERSION $PYTHON_VERSION
ENV POETRY_VERSION 1.1.6
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
RUN git clone https://github.com/pyenv/pyenv.git $PYENV_ROOT && pyenv rehash &&  eval "$(pyenv init -)"
RUN pyenv install $PYENV_VERSION && pyenv global $PYENV_VERSION
RUN pip install --upgrade pip
RUN pip install --upgrade setuptools
RUN pip3 install --no-cache-dir poetry==$POETRY_VERSION && poetry config virtualenvs.create false

ENV NIKE_LAB222_PROJECT knockoff-factory
RUN mkdir -p /opt/nike-lab222/$NIKE_LAB222_PROJECT/
WORKDIR /opt/nike-lab222/$NIKE_LAB222_PROJECT/
COPY . /opt/nike-lab222/$NIKE_LAB222_PROJECT/

###########
RUN wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add - \
    && echo 'deb http://apt.postgresql.org/pub/repos/apt/ bionic-pgdg main' | tee /etc/apt/sources.list.d/pgdg.list
############
RUN poetry install --extras complete
