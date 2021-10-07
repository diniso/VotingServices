from datetime import timedelta
import os

databaseAuthentificationURL = os.environ["DATABASE_URL_AUTHENTIFICATION"]

class Configuration():
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:root@{}/authentificationDatabase".format(databaseAuthentificationURL);
    zvanicnik = "Izborni zvanicnik";
    admininstrator = "Administrator"
    JWT_SECRET_KEY = "ared43ldieaa021";
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1);
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30);