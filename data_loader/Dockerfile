FROM pypy:3-5.10-slim
ARG BASE_DIR

RUN apk update
RUN apk add --no-cache postgresql-dev build-base

WORKDIR $BASE_DIR/
RUN mkdir ./tmp

COPY requirements.txt $BASE_DIR/
RUN pip install --no-cache-dir -r requirements.txt

COPY loader.py .
COPY models.py .
COPY docker-entrypoint.sh .
RUN chmod +x ./docker-entrypoint.sh

ENTRYPOINT ["./docker-entrypoint.sh"]
