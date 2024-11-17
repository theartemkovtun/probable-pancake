FROM python:3.10.15-slim

ARG WORKDIR=anchoring-api

WORKDIR /${WORKDIR}

COPY ./requirements.txt /${WORKDIR}/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /${WORKDIR}/requirements.txt

COPY ./app /${WORKDIR}/app

CMD ["fastapi", "run", "app/main.py", "--port", "3001"]