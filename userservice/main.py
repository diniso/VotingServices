from flask import Flask, request, Response, jsonify, json
from authentificationmodels import database, Korisnik, KorisnickaUloga
from Configuration import Configuration
import re
from sqlalchemy import and_
from functools import wraps
from flask_jwt_extended import JWTManager, create_access_token , create_refresh_token, jwt_required, get_jwt_identity , get_jwt, verify_jwt_in_request

def passwordCheck(password):
    if (len(password)) < 8:
        return False;

    lowerCase = False;
    upperCase = False;
    number = False;

    for ch in password:
        if ch.islower():
            lowerCase = True;

        if ch.isupper():
            upperCase = True;

        if ch.isdigit():
            number = True;

    return lowerCase and upperCase and number

def checkJmbg(jmbg):
    if len(jmbg) != 13 or (not jmbg.isdigit()):
        return False;

    days = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    day = int(jmbg[0:2])
    month = int(jmbg[2:4])

    if month < 1 or month > 12:
        return False;

    if day < 1 or day > days[month]:
        return False

    control = int(jmbg[12:13])
    calControl = 11 - (
            (7*(int(jmbg[0]) + int(jmbg[6])) +
             6 * (int(jmbg[1]) + int(jmbg[7])) +
             5 * (int(jmbg[2]) + int(jmbg[8])) +
             4 * (int(jmbg[3]) + int(jmbg[9])) +
             3 * (int(jmbg[4]) + int(jmbg[10])) +
             2 * (int(jmbg[5]) + int(jmbg[11]))
             ) % 11)

    if (calControl > 9):
        calControl = 0

    return calControl == control

application = Flask(__name__);
application.config.from_object(Configuration)
jwt = JWTManager(application)

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

def checkemail(email):
   # result = parseaddr(email);
   # return (len(result[1]) != 0)
   regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
   if (re.match(regex, email)):
       return True

   return False

@application.route("/register" , methods = ["POST"])
def register():
    jmbg = request.json.get("jmbg" , "")
    forename = request.json.get("forename", "")
    surname = request.json.get("surname", "")
    email = request.json.get("email", "")
    password = request.json.get("password", "")

    if (len(jmbg) == 0):
        ret = {
            "message": "Field jmbg is missing."
        }
        return application.response_class(response= json.dumps(ret),status=400,mimetype='application/json')

    if (len(forename) == 0):
        ret = {
            "message": "Field forename is missing."
        }
        return application.response_class(response= json.dumps(ret),status=400,mimetype='application/json')

    if (len(surname) == 0):
        ret = {
            "message": "Field surname is missing."
        }
        return application.response_class(response= json.dumps(ret),status=400,mimetype='application/json')

    if (len(email) == 0):
        ret = {
            "message": "Field email is missing."
        }
        return application.response_class(response= json.dumps(ret),status=400,mimetype='application/json')

    if (len(password) == 0):
        ret = {
            "message": "Field password is missing."
        }
        return application.response_class(response= json.dumps(ret),status=400,mimetype='application/json')


    if not checkJmbg(jmbg):
        ret = {
            "message": "Invalid jmbg."
        }
        return application.response_class(response=json.dumps(ret), status=400, mimetype='application/json')



    if (not checkemail(email)):
        ret = {
            "message": "Invalid email."
        }
        return application.response_class(response= json.dumps(ret),status=400,mimetype='application/json')

    if not passwordCheck(password):
        ret = {
            "message": "Invalid password."
        }
        return application.response_class(response= json.dumps(ret),status=400,mimetype='application/json')

    try:
        zv = KorisnickaUloga.query.filter(KorisnickaUloga.name == Configuration.zvanicnik).first()
        korisnik = Korisnik(JMBG = jmbg , surname = surname, forename = forename, email = email , password = password , idRole = zv.id)

        database.session.add(korisnik)
        database.session.commit()

    except Exception:
        ret = {
            "message": "Email already exists."
        }
        return application.response_class(response=json.dumps(ret), status=400, mimetype='application/json')

    return Response(status= 200);


@application.route("/login" , methods = ["POST"])
def login():
    email = request.json.get("email", "")
    password = request.json.get("password", "")

    if (len(email) == 0):
        ret = {
            "message": "Field email is missing."
        }
        return application.response_class(response= json.dumps(ret),status=400,mimetype='application/json')

    if (len(password) == 0):
        ret = {
            "message": "Field password is missing."
        }
        return application.response_class(response= json.dumps(ret),status=400,mimetype='application/json')

    if (not checkemail(email)):
        ret = {
            "message": "Invalid email."
        }
        return application.response_class(response=json.dumps(ret), status=400, mimetype='application/json')

    korisnik = Korisnik.query.filter(and_(Korisnik.email == email , Korisnik.password == password)).first()

    if (not korisnik):
        ret = {
            "message": "Invalid credentials."
        }
        return application.response_class(response=json.dumps(ret), status=400, mimetype='application/json')

    rola = KorisnickaUloga.query.filter(KorisnickaUloga.id == korisnik.idRole).first();

    additionalClaims = {
        "forename": korisnik.forename,
        "jmbg": korisnik.JMBG,
        "surname": korisnik.surname,
        "email": korisnik.email,
        "uloga": str(rola)
    }

    accessToken = create_access_token(identity=korisnik.email, additional_claims=additionalClaims);
    refreshToken = create_refresh_token(identity=korisnik.email, additional_claims=additionalClaims);

    return jsonify(accessToken=accessToken, refreshToken=refreshToken);


@application.route("/refresh", methods = ["POST"])
@jwt_required(refresh=True)
def refreshToken():
    identity = get_jwt_identity();
    refreshClaims = get_jwt();

    additionalClaims = {
        "forename": refreshClaims["forename"],
        "surname": refreshClaims["surname"],
        "jmbg": refreshClaims["jmbg"],
        "email": refreshClaims["email"],
        "uloga": refreshClaims["uloga"]
    };

    return jsonify(accessToken = create_access_token(identity=identity, additional_claims=additionalClaims));


@application.route("/delete" , methods= ["POST"])
@jwt_required()
@roleCheck(Configuration.admininstrator)
def deleteUser():
    email = request.json.get("email", "")

    if (len(email) == 0):
        ret = {
            "message": "Field email is missing."
        }
        return application.response_class(response= json.dumps(ret),status=400,mimetype='application/json')

    if (not checkemail(email)):
        ret = {
            "message": "Invalid email."
        }
        return application.response_class(response=json.dumps(ret), status=400, mimetype='application/json')

    korZaBrisanje = Korisnik.query.filter(Korisnik.email == email).first();
    if (not korZaBrisanje):
        ret = {
            "message": "Unknown user."
        }
        return application.response_class(response=json.dumps(ret), status=400, mimetype='application/json')

    database.session.delete(korZaBrisanje);
    database.session.commit();

    return Response(status=200)

@application.route("/" , methods = ["GET"])
def index():
    return "Hello world"


if (__name__ == "__main__"):
    database.init_app(application);
    application.run(debug= True ,host="0.0.0.0", port= 5000)