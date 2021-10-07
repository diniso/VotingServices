from datetime import timedelta
import os

databaseURL = os.environ["DATABASE_URL"]

class Configuration():
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:root@{}/izboriDatabase".format(databaseURL);
    zvanicnik = "Izborni zvanicnik";
    admininstrator = "Administrator"
    JWT_SECRET_KEY = "ared43ldieaa021";
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1);
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30);
    NazivStatusUspesnogGlasa = "Uspesno"
    NazivStatusDuplogGlasa = "Duplicate ballot."
    NazivStatusNepostojecegKorisnika = "Invalid poll number."
    BrojMandata = 250
    Cenzus = 0.05
    RedisVoteList = "votes"