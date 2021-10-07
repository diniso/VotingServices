FROM python:3

RUN mkdir -p /opt/src/migrations
WORKDIR /opt/src/migrations

COPY createDatabase/Configuration.py ./Configuration.py
COPY createDatabase/main.py ./main.py
COPY createDatabase/models.py ./models.py
COPY createDatabase/requirments.txt ./requirments.txt

RUN pip install -r ./requirments.txt

ENTRYPOINT ["python" , "./main.py"]