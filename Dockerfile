FROM python:3.8-buster

COPY . /app

WORKDIR /app

# Install dependencies:
RUN apt update && apt install build-essential
RUN pip install -U setuptools wheel
RUN pip install -U .[staging]

# Run the application:
CMD uwsgi --http :9090 --module messenger:APP
