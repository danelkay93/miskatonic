FROM pytorch/pytorch:latest

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=0 \
    POETRY_VIRTUALENVS_CREATE=0 \
    POETRY_REQUESTS_TIMEOUT=60 \
    POETRY_CACHE_DIR=/tmp/poetry_cache
#
#RUN apt -y update && apt -y upgrade
#RUN apt -y install software-properties-common
#RUN apt -y update
#RUN apt-get -y install linux-headers-generic
#RUN add-apt-repository contrib
#RUN #apt-key del 7fa2af80
#RUN #cp /var/cuda-repo-debian-11-4-local/cuda-*-keyring.gpg /usr/share/keyrings/
#RUN #cp /var/cuda-repo-wsl-debian-11-4-local/*.gpg /usr/share/keyrings/
#RUN apt-get update
#RUN apt-get install -y cuda-toolkit-12-2

WORKDIR /usr/src/miskatonic

COPY poetry.lock pyproject.toml /usr/src/miskatonic/

RUN pip3 install poetry

RUN poetry config virtualenvs.create false
RUN --mount=type=cache,target=$POETRY_CACHE_DIR poetry install -n --no-ansi --no-root

#RUN poetry run ipython kernel install --user --name=miskatonic_kernel
#RUN jupyter notebook --generate-config
#RUN echo "c.NotebookApp.password='password'">>/root/.jupyter/jupyter_notebook_config.py
#RUN echo "c.NotebookApp.allow_root=True">>/root/.jupyter/jupyter_notebook_config.py

