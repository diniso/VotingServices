from Configuration import Configuration
from redis import Redis
import json
import sqlalchemy
from sqlalchemy import text
from datetime import  datetime
import time
import os

if (__name__ == "__main__"):

    timezone = int(os.environ["mytimezone"])*3600
    finished = False
    while not finished:
        try:
            engine = sqlalchemy.create_engine(Configuration.SQLALCHEMY_DATABASE_URI)
            connection = engine.connect()

            finished = True
        except Exception:
            time.sleep(30)

    finished = False
    while not finished:
        try:
            statusUspesne = connection.execute("select id from statusglasa where name = '{}'".format(Configuration.NazivStatusUspesnogGlasa)).fetchall()[0][0]
            statusDuplogGlasa = connection.execute("select id from statusglasa where name = '{}'".format(Configuration.NazivStatusDuplogGlasa)).fetchall()[0][0]
            statusNepostojecegKorisnika = connection.execute("select id from statusglasa where name = '{}'".format(Configuration.NazivStatusNepostojecegKorisnika)).fetchall()[0][0]
            finished = True
        except:
            pass

    connection.close()

    with Redis(Configuration.RedisIpAdress) as rd:
        while True:
            vote = rd.lpop(Configuration.RedisVoteList)
            if (vote == None):
                continue

            vote = vote.decode("utf-8").replace("'", '"')
            vote = json.loads(vote)
            sada = datetime.now().timestamp() + timezone
            sada = str(datetime.fromtimestamp(sada))
            connection = engine.connect()
            izbori = connection.execute(text("select * from izbori where start <= :datum and end >= :datum").bindparams( datum = sada)).fetchall()
            if len(izbori) == 0:
                continue

            idStatus = statusUspesne
            idTrenutnoIzbora = izbori[0][0]
            brojGlasovaSaGuid = connection.execute(text("select * from glas where guid = :guid").bindparams(guid = vote["guid"])).fetchall()
            if (len(brojGlasovaSaGuid) != 0):
                idStatus = statusDuplogGlasa
                vote["pollNumber"] = brojGlasovaSaGuid[0][2]
            else:
                postoji = connection.execute(text("select * from ucestvuje where pullNumber = :poll and idIzbor = :id").bindparams(poll = vote["pollNumber"] , id = idTrenutnoIzbora)).fetchall()
                if len(postoji) == 0:
                    idStatus = statusNepostojecegKorisnika
            insertQuery = text("insert into glas(guid, pullNumber , idStatus , idIzbora , JMBGZvanicnika) value( :guid,:poll  ,:status ,:id  , :jmbg )").bindparams(guid = vote["guid"] , poll = vote["pollNumber"],status =  idStatus , id = idTrenutnoIzbora ,jmbg = vote["jmbgZvanicnika"])
            connection.execute(insertQuery)
            connection.close()


