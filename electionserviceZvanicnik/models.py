from flask_sqlalchemy import SQLAlchemy

database = SQLAlchemy();


class Ucesnik(database.Model):
    __tablename__ = "ucesnici";
    id = database.Column(database.Integer , primary_key = True);
    name = database.Column(database.String(256) , nullable = False);
    individual = database.Column(database.Boolean , nullable = False);

    def __repr__(self):
        ret = "({} {} ". format(self.id , self.name ) ;
        if self.individual:
            ret = ret + "pojedinac )";
        else:
            ret = ret + "stranka )";
        return ret;


class Izbor(database.Model):
    __tablename__ = "izbori";
    id = database.Column(database.Integer , primary_key = True);
    individual = database.Column(database.Boolean, nullable=False);
    start = database.Column(database.DateTime , nullable = False);
    end = database.Column(database.DateTime, nullable=False);
    ocenjen = database.Column(database.Boolean, nullable=False);

    def __repr__(self):
        ret = "({} {}-{} ". format(self.id , str(self.start) ,  str(self.end) ) ;
        if self.individual:
            ret = ret + "predsednicki )";
        else:
            ret = ret + "parlamentarni )";
        return ret;


class Ucestvuje(database.Model):
    __tablename__ = "ucestvuje";
    id = database.Column(database.Integer , primary_key = True);
    idIzbor = database.Column(database.Integer, database.ForeignKey("izbori.id"), nullable = False );
    idUcesnik = database.Column(database.Integer, database.ForeignKey("ucesnici.id"), nullable=False);
    pullNumber = database.Column(database.Integer , nullable = False);
    result = database.Column(database.Float, nullable=False);


class StatusGlasa(database.Model):
    __tablename__ = "statusglasa";
    id = database.Column(database.Integer, primary_key=True)
    name = database.Column(database.String(256), nullable=False);

    def __repr__(self):
        return self.name;

class Glas(database.Model):
    __tablename__ = "glas";
    id = database.Column(database.Integer , primary_key = True)
    guid = database.Column(database.String(256), nullable = False);
    pullNumber = database.Column(database.Integer, nullable=False);
    idStatus = database.Column(database.Integer, database.ForeignKey("statusglasa.id"), nullable=False);
    idIzbora = database.Column(database.Integer, database.ForeignKey("izbori.id"), nullable=False);
    JMBGZvanicnika = database.Column(database.String(13), nullable=False);