FROM python:3.8-slim-buster

RUN python3 -m venv /opt/venv

# Install dependencies:
RUN . venv/bin/activate && pip install -Ue

# Run the application:
COPY 
CMD 