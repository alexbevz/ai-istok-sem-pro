FROM savyaznikov/cuda12.1-cudnn8-python3.11:latest

RUN pip install pipenv

ENV PIPENV_VENV_IN_PROJECT=1
WORKDIR /app

COPY ./Pipfile .
RUN python3.11 -m pip install --upgrade pip

RUN pipenv install

COPY ./alembic ./alembic
COPY ./src ./src
COPY ./test ./test
COPY ./alembic.ini .
COPY ./main.py .
COPY ./docker-entrypoint.sh .


ENTRYPOINT ["./docker-entrypoint.sh"]