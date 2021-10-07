FROM python:3

RUN mkdir -p /opt/src/elections
WORKDIR /opt/src/elections

COPY electionserviceAdmin/Configuration.py ./Configuration.py
COPY electionserviceAdmin/main.py ./main.py
COPY electionserviceAdmin/models.py ./models.py
COPY electionserviceAdmin/requirments.txt ./requirments.txt

RUN pip install -r ./requirments.txt

ENTRYPOINT ["python" , "./main.py"]