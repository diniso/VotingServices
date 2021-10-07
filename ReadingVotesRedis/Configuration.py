import os

databaseURL = os.environ["DATABASE_URL"]
redisURL = os.environ["REDIS_URL"]


class Configuration():
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:root@{}/izboriDatabase".format(databaseURL);
    NazivStatusUspesnogGlasa = 'Uspesno'
    NazivStatusDuplogGlasa = 'Duplicate ballot.'
    NazivStatusNepostojecegKorisnika = 'Invalid poll number.'
    RedisVoteList = "votes"
    RedisIpAdress = redisURL