FROM python:3.10.19

WORKDIR /code

RUN groupadd -r web && useradd -r -g web web

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt update && apt install -y netcat
RUN pip install --upgrade pip \
    && pip install --no-cache-dir poetry==1.8.3 \
    && poetry config virtualenvs.create false

ENV TZ=Europe/Moscow
RUN apt install tzdata
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

COPY ./movies_admin/pyproject.toml pyproject.toml

RUN poetry install --no-interaction --no-ansi --no-root

COPY ./docker/admin/entrypoint.sh /web/entrypoint.sh
COPY movies_admin/ .

RUN python manage.py collectstatic --no-input

USER web

ENTRYPOINT ["/web/entrypoint.sh"]