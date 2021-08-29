FROM python:3.9.6-slim

RUN apt-get update
RUN apt-get install -y curl zip 

WORKDIR /app
COPY ./ ./
ADD bin bin
RUN pip install -r requirements.txt

RUN /app/bin/compile.sh

ENV PYTHONPATH=/app
ENTRYPOINT python ./action_service.py