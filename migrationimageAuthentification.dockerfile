FROM python:3

RUN mkdir -p /opt/src/migrations
WORKDIR /opt/src/migrations

COPY createAuthentificationDatabase/ConfigurationAuthentification.py ./ConfigurationAuthentification.py
COPY createAuthentificationDatabase/main.py ./main.py
COPY createAuthentificationDatabase/authentificationmodels.py ./authentificationmodels.py
COPY createAuthentificationDatabase/requirments.txt ./requirments.txt

RUN pip install -r ./requirments.txt

ENTRYPOINT ["python" , "./main.py"]