FROM python:3
ENV PYTHONUNBUFFERED = 1
WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip install install -r requirements.txt