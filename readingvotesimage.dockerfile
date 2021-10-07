FROM python:3

RUN mkdir -p /opt/src/readingvotes
WORKDIR /opt/src/readingvotes

COPY ReadingVotesRedis/Configuration.py ./Configuration.py
COPY ReadingVotesRedis/main.py ./main.py
COPY ReadingVotesRedis/requirments.txt ./requirments.txt

RUN pip install -r ./requirments.txt

ENTRYPOINT ["python" , "./main.py"]