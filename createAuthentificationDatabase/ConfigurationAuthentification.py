import os

databaseAuthentificationURL = os.environ["DATABASE_URL_AUTHENTIFICATION"]

class Configuration():
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:root@{}/authentificationDatabase".format(databaseAuthentificationURL);