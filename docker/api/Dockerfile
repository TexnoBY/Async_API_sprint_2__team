FROM python:3.10.19

WORKDIR /opt/app

RUN apt-get update \
     &&  apt-get install -y procps="2:4.0.2-3" \
     && rm -rf /var/lib/apt/lists/*

COPY ./app/pyproject.toml pyproject.toml

RUN pip install --upgrade pip \
      && pip install --no-cache-dir poetry==1.8.3 \
     && poetry config virtualenvs.create false \
     && poetry install --no-interaction --no-ansi --no-root

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY ./app .

RUN chmod +x ./main.py

RUN groupadd -r app_group \
     && useradd -d /opt/app -r -g app_group app \
     && chown app:app_group -R /opt/app/ \
     && chown app:app_group -R /var/log/

USER app
ENTRYPOINT ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
