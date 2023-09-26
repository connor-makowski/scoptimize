FROM python:3.11.3-bullseye
WORKDIR /app
COPY . /app
RUN pip install -e .