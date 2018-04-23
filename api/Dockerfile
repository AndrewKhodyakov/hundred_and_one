FROM python:3.6-slim
ARG BASE_DIR

RUN apt-get -y update
RUN apt-get -y install build-essential libpq-dev

WORKDIR $BASE_DIR/

COPY requirements.txt $BASE_DIR/
RUN pip install --no-cache-dir -r requirements.txt

COPY src .
COPY docker-entrypoint.sh .
RUN chmod +x ./docker-entrypoint.sh
RUN apt-get purge -y build-essential

ENTRYPOINT ["./docker-entrypoint.sh"]
