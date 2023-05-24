FROM python:3.8
WORKDIR /code
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
RUN apt-get update
RUN apt-get install gcc musl-dev
RUN /usr/local/bin/python -m pip install --upgrade pip
RUN apt-get update && apt-get install openssh-client && apt-get clean && rm -rf /var/lib/apt/lists/*
COPY src/requirements.txt requirements.txt
RUN pip install -r requirements.txt
EXPOSE 5000
COPY . .
WORKDIR /code/src
CMD ["flask", "run"]
