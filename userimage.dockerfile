FROM python:3

RUN mkdir -p /opt/src/userservice
WORKDIR /opt/src/userservice

COPY userservice/Configuration.py ./Configuration.py
COPY userservice/main.py ./main.py
COPY userservice/authentificationmodels.py ./authentificationmodels.py
COPY userservice/requirments.txt ./requirments.txt

RUN pip install -r ./requirments.txt

ENTRYPOINT ["python" , "./main.py"]