import os

databaseURL = os.environ["DATABASE_URL"]

class Configuration():
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:root@{}/izboriDatabase".format(databaseURL);