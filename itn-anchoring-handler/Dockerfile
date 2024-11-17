FROM python:3.10.15-slim

ARG WORKDIR=/anchoring-handler

WORKDIR ${WORKDIR}

COPY ./requirements.txt ${WORKDIR}/requirements.txt

RUN pip install --no-cache-dir --upgrade -r ${WORKDIR}/requirements.txt

COPY . ${WORKDIR}

CMD ["python", "/anchoring-handler/runner.py"]