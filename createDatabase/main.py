from flask import Flask
from models import database , StatusGlasa
from Configuration import Configuration
from flask_migrate import Migrate , init , migrate , upgrade
from sqlalchemy_utils import database_exists , create_database

application = Flask(__name__);
application.config.from_object(Configuration);

migrateObject = Migrate ( application, database );

finished = False
while not finished:
    try:
        if (not database_exists(application.config["SQLALCHEMY_DATABASE_URI"])):
            create_database(application.config["SQLALCHEMY_DATABASE_URI"]);

        database.init_app(application);

        with application.app_context() as context:
            init();
            migrate(message="Production migration init");
            upgrade();

            statusGlasa1 = StatusGlasa(name="Uspesno");
            statusGlasa2 = StatusGlasa(name="Duplicate ballot.");
            statusGlasa3 = StatusGlasa(name="Invalid poll number.");

            database.session.add(statusGlasa1);
            database.session.add(statusGlasa2);
            database.session.add(statusGlasa3);

            database.session.commit();
            finished = True;
    except Exception as e:
        print(e)





