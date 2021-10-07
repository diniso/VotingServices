from flask import Flask
from authentificationmodels import database, Korisnik , KorisnickaUloga
from ConfigurationAuthentification import Configuration
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
            migrate(message="Production migration");
            upgrade();

            adminUloga = KorisnickaUloga(name="Administrator");
            ostaliUloga = KorisnickaUloga(name="Izborni zvanicnik");

            database.session.add(adminUloga);
            database.session.add(ostaliUloga);

            database.session.commit();

            korisnik = Korisnik(JMBG="0000000000000", forename="admin", surname="admin", email="admin@admin.com",
                                password="1",
                                idRole=adminUloga.id);

            database.session.add(korisnik);

            database.session.commit();
            finished = True;
    except Exception:
        pass





