from flask import Flask, request, Response, jsonify, json
from models import database, Ucesnik, Izbor, Ucestvuje, Glas, StatusGlasa
from Configuration import Configuration
from functools import wraps
from flask_jwt_extended import JWTManager , get_jwt, verify_jwt_in_request
from sqlalchemy import and_ , func
from datetime import datetime
import os


application = Flask(__name__);
application.config.from_object(Configuration)
jwt = JWTManager(application)

timezone = int(os.environ["mytimezone"])*3600

def datetime_valid(vreme):
    try:
        if vreme.find("+") != -1:
            posit = vreme.find(":" , vreme.find("+") + 1)
            if (posit == -1):
                posit = vreme.find("+") + 3
                vreme = vreme[:posit] + ":" + vreme[posit:]
        return datetime.fromisoformat(vreme)
    except:
        try:
            return datetime.fromisoformat(vreme.replace('Z', '+00:00'))
        except:
            return None

def roleCheck ( role ):
    def innerRole ( function ):
        @wraps ( function )
        def decorator ( *arguments, **keywordArguments ):
            verify_jwt_in_request ( );
            claims = get_jwt ( );
            if ( ( "uloga" in claims ) and ( claims["uloga"] == role) ):
                return function ( *arguments, **keywordArguments );
            else:
                return Response ( "permission denied!", status = 403 );

        return decorator;

    return innerRole;


@application.route("/createParticipant" , methods = ["POST"])
@roleCheck(Configuration.admininstrator)
def createParticipant():
    name = request.json.get("name" , "")
    individual = request.json.get("individual" , "")

    if (len(name) == 0):
        ret = {
            "message": "Field name is missing."
        }
        return application.response_class(response= json.dumps(ret),status=400,mimetype='application/json')

    if (type(individual) != type(True)):
        ret = {
            "message": "Field individual is missing."
        }
        return application.response_class(response=json.dumps(ret), status=400, mimetype='application/json')

    try:
        ucesnik = Ucesnik(name = name , individual = individual)
        database.session.add(ucesnik)
        database.session.commit()

        return jsonify(id = ucesnik.id)

    except Exception:
        ret = {
            "message": "Name is too long."
        }
        return application.response_class(response=json.dumps(ret), status=400, mimetype='application/json')


@application.route("/getParticipants", methods = ["GET"])
@roleCheck(Configuration.admininstrator)
def getParticipants():

    participants = Ucesnik.query.all();

    ret = {
        "participants" : []
    }

    for ucesnik in participants:
        data = {}
        data["id"] = ucesnik.id
        data["name"] = ucesnik.name
        data["individual"] = ucesnik.individual
        ret["participants"].append(data)

    return ret

@application.route("/createElection", methods = ["POST"])
@roleCheck(Configuration.admininstrator)
def createElection():
    start = request.json.get("start" , "")
    end = request.json.get("end", "")
    individual = request.json.get("individual" , "")
    participants = request.json.get("participants", "")

    if (len(start) == 0):
        ret = {
            "message": "Field start is missing."
        }
        return application.response_class(response= json.dumps(ret),status=400,mimetype='application/json')

    if (len(end) == 0):
        ret = {
            "message": "Field end is missing."
        }
        return application.response_class(response= json.dumps(ret),status=400,mimetype='application/json')

    if (type(individual) != type(True)):
        ret = {
            "message": "Field individual is missing."
        }
        return application.response_class(response=json.dumps(ret), status=400, mimetype='application/json')

    if (type(participants) != list):
        ret = {
            "message": "Field participants is missing."
        }
        return application.response_class(response=json.dumps(ret), status=400, mimetype='application/json')

    start = datetime_valid(start)
    end = datetime_valid(end) # izbaciti start < datetime.now() ako ne budu testovi prolazili
    if (start == None) or (end == None) or (start >= end):
        ret = {
            "message": "Invalid date and time."
        }
        return application.response_class(response=json.dumps(ret), status=400, mimetype='application/json')

    sviIzbori = Izbor.query.all();

    for izbor in sviIzbori:
        if start.timestamp() <= izbor.end.timestamp() and izbor.start.timestamp() <= end.timestamp():
            ret = {
                "message": "Invalid date and time."
            }
            return application.response_class(response=json.dumps(ret), status=400, mimetype='application/json')

    ucesnici = Ucesnik.query.all();

    try:
        if (len(participants) < 2):
            raise Exception("Nema dovoljno prijavljenih")
        brojPronadjenih = 0
        for uce in participants:
            idUcesnika = int(uce)
            pronasao = False
            for ucesnik in ucesnici:
                if ucesnik.id == idUcesnika:
                    pronasao = True
                    brojPronadjenih += 1
                    if (ucesnik.individual != individual):
                        raise Exception("Nisu istog tipa")
                    break

            if not pronasao:
                raise Exception("Ne postoji ucesnik sa tim idijem")

        if (brojPronadjenih < len(participants)):
            raise Exception("Ne postoje svi ucesnici")


    except Exception:
        ret = {
            "message": "Invalid participants."
        }
        return application.response_class(response=json.dumps(ret), status=400, mimetype='application/json')

    izbor = Izbor(individual = individual , start = str(start) , end = str(end) , ocenjen = False)
    database.session.add(izbor)
    database.session.commit()

    pullNumber = 1
    retList = []
    for idUcesnika in participants:
        ucestvuje = Ucestvuje(idUcesnik = int(idUcesnika) , idIzbor = izbor.id , pullNumber = pullNumber , result = 0 )
        retList.append(pullNumber)
        pullNumber += 1
        database.session.add(ucestvuje)

    database.session.commit()

    return jsonify(pollNumbers = retList)


@application.route("/getElections", methods = ["GET"])
@roleCheck(Configuration.admininstrator)
def getElections():
    izbori = Izbor.query.all()
    ucestvuje = Ucestvuje.query.all()

    ret = {
        "elections" : []
    }

    for izbor in izbori:
        izborJson = {}
        izborJson["id"] = izbor.id
        izborJson["start"] = str(izbor.start)
        izborJson["end"] = str(izbor.end)
        izborJson["individual"] = izbor.individual
        izborJson["participants"] = []

        for ucesnikIzbora in ucestvuje:
            if ucesnikIzbora.idIzbor != izbor.id:
                continue

            ucesnik = Ucesnik.query.filter(Ucesnik.id == ucesnikIzbora.idUcesnik).first()
            ucesnikJson = {}
            ucesnikJson["id"] = ucesnik.id;
            ucesnikJson["name"] = ucesnik.name
            izborJson["participants"].append(ucesnikJson)

        ret["elections"].append(izborJson);

    return ret


@application.route("/getResults", methods = ["GET"])
@roleCheck(Configuration.admininstrator)
def getResults():
    if "id" not in request.args:
        ret = {
            "message": "Field id is missing."
        }
        return application.response_class(response=json.dumps(ret), status=400, mimetype='application/json')

    idIzbora = None
    try:
        idIzbora = int(request.args.get("id"))
    except:
        ret = {
            "message": "Field id should be int."
        }
        return application.response_class(response=json.dumps(ret), status=400, mimetype='application/json')

    izbor = Izbor.query.filter(Izbor.id == idIzbora).first()
    if not izbor:
        ret = {
            "message": "Election does not exist."
        }
        return application.response_class(response=json.dumps(ret), status=400, mimetype='application/json')

    if izbor.end.timestamp() > (datetime.now().timestamp() + timezone):
        ret = {
            "message": "Election is ongoing."
        }
        return application.response_class(response=json.dumps(ret), status=400, mimetype='application/json')

    if not izbor.ocenjen:
        uspesanGlas = StatusGlasa.query.filter(StatusGlasa.name == Configuration.NazivStatusUspesnogGlasa).first()
        br = func.count(Glas.guid)
        brojGlasova = Glas.query.filter(and_(Glas.idIzbora == izbor.id, Glas.idStatus == uspesanGlas.id)).with_entities(br).first()
        brojGlasova = brojGlasova[0]

        ucesnici = Ucestvuje.query.filter(Ucestvuje.idIzbor == izbor.id).all()

        if brojGlasova > 0:
            if izbor.individual:
                for ucesnik in ucesnici:
                    brojGlasovaUcesnika = Glas.query.filter(and_(Glas.idIzbora == izbor.id  , Glas.idStatus == uspesanGlas.id , Glas.pullNumber == ucesnik.pullNumber)).with_entities(br).first()[0]
                    ucesnik.result = brojGlasovaUcesnika / brojGlasova
            else:
                glasovi = {}
                cenzusi = {}
                for ucesnik in ucesnici:
                    brojGlasovaUcesnika = Glas.query.filter(and_(Glas.idIzbora == izbor.id, Glas.idStatus == uspesanGlas.id, Glas.pullNumber == ucesnik.pullNumber)).with_entities( br).first()[0]
                    if brojGlasovaUcesnika < Configuration.Cenzus * brojGlasova:
                        continue

                    glasovi[ucesnik.pullNumber] = brojGlasovaUcesnika
                    cenzusi[ucesnik.pullNumber] = 0

                for i in range(Configuration.BrojMandata):
                    maxGlasova = 0
                    maxGlasovaUKrugu = 0
                    pullNumber = -1
                    for key in glasovi:
                        kol = glasovi[key] / (cenzusi[key] + 1)
                        # or (kol == maxGlasovaUKrugu and maxGlasova < glasovi[key])
                        if kol > maxGlasovaUKrugu :
                            maxGlasovaUKrugu = kol
                            pullNumber = key
                            maxGlasova = glasovi[key]

                    if pullNumber == -1:
                        break;

                    cenzusi[pullNumber] += 1

                for ucesnik in ucesnici:
                    if ucesnik.pullNumber not in glasovi.keys():
                        continue

                    ucesnik.result = cenzusi[ucesnik.pullNumber]

        izbor.ocenjen = True
        database.session.commit()


    ret = {
        "participants" : [],
        "invalidVotes": []
    }

    ucesnici = Ucestvuje.query.filter(Ucestvuje.idIzbor == izbor.id).all()
    for ucesnik in ucesnici:
        ucesnikJson = {}
        if izbor.individual:
            ucesnikJson["result"] = round(ucesnik.result,2)
        else:
            ucesnikJson["result"] = int(ucesnik.result)
        ucesnikJson["pollNumber"] = ucesnik.pullNumber
        ucesnikJson["name"] = Ucesnik.query.filter(Ucesnik.id == ucesnik.idUcesnik).first().name

        ret["participants"].append(ucesnikJson)

    statusGlasa = StatusGlasa.query.filter(StatusGlasa.name == Configuration.NazivStatusUspesnogGlasa).first()
    losiGlasovi = Glas.query.filter(and_(Glas.idStatus != statusGlasa.id , Glas.idIzbora == izbor.id)).all()

    for glas in losiGlasovi:
        data = {
            "electionOfficialJmbg" : glas.JMBGZvanicnika,
            "pollNumber" : glas.pullNumber,
             "ballotGuid" : glas.guid
        }
        data["reason"] = StatusGlasa.query.filter(StatusGlasa.id == glas.idStatus).first().name
        ret["invalidVotes"].append(data)

    return ret

@application.route("/" , methods = ["GET"])
def index():
    return "Hello world"

if (__name__ == "__main__"):
    database.init_app(application);
    application.run(debug= True ,host="0.0.0.0", port= 5001)