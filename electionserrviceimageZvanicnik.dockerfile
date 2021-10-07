FROM python:3

RUN mkdir -p /opt/src/elections
WORKDIR /opt/src/elections

COPY electionserviceZvanicnik/Configuration.py ./Configuration.py
COPY electionserviceZvanicnik/main.py ./main.py
COPY electionserviceZvanicnik/models.py ./models.py
COPY electionserviceZvanicnik/requirments.txt ./requirments.txt

RUN pip install -r ./requirments.txt

ENTRYPOINT ["python" , "./main.py"]