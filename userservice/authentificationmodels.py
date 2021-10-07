from flask_sqlalchemy import SQLAlchemy

database = SQLAlchemy();

class KorisnickaUloga(database.Model):
    __tablename__ = "uloge";
    id = database.Column(database.Integer , primary_key = True)
    name = database.Column(database.String(256), nullable = False);
    def __repr__(self):
        return self.name;

class Korisnik(database.Model):
    __tablename__ = "korisnici";
    JMBG = database.Column(database.String(13) , primary_key = True);
    email = database.Column(database.String(256), nullable = False, unique = True);
    surname = database.Column(database.String(256), nullable = False);
    forename = database.Column(database.String(256), nullable = False);
    password = database.Column(database.String(256), nullable=False);
    idRole = database.Column(database.Integer , database.ForeignKey("uloge.id") , nullable = False);

    def __repr__(self):
        return "({} {})".format(self.JMBG , self.email);