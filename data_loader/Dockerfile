FROM pypy:3-5.10-slim
ARG BASE_DIR

RUN apt-get -y update
RUN apt-get -y install build-essential libpq-dev
WORKDIR $BASE_DIR/
RUN mkdir ./tmp

COPY requirements.txt $BASE_DIR/
RUN pip install --no-cache-dir -r requirements.txt

COPY loader.py .
COPY models.py .
COPY docker-entrypoint.sh .
RUN chmod +x ./docker-entrypoint.sh
RUN apt-get purge -y build-essential

ENTRYPOINT ["./docker-entrypoint.sh"]
