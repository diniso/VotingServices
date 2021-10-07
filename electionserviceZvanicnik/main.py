from flask import Flask, request, Response, jsonify, json
from models import database
from Configuration import Configuration
from functools import wraps
from flask_jwt_extended import JWTManager , get_jwt, verify_jwt_in_request
import csv
import io
from redis import Redis


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

@application.route("/vote", methods = ["POST"])
@roleCheck(Configuration.zvanicnik)
def vote():
    if "file" not in request.files:
        ret = {
            "message": "Field file is missing."
        }
        return application.response_class(response=json.dumps(ret), status=400, mimetype='application/json')

    content = request.files["file"].stream.read().decode("utf-8");
    stream = io.StringIO(content);
    reader = csv.reader(stream);

    data = []
    numOfLine = 0
    for row in reader:
        if len(row) != 2:
            ret = {
                "message": "Incorrect number of values on line " + str(numOfLine) + "."
            }
            return application.response_class(response=json.dumps(ret), status=400, mimetype='application/json')

        try:
            brojKolone = int(row[1])
            if (brojKolone < 1):
                raise Exception("Broj poll manji od 1")

            data.append({
                "guid" : row[0],
                "pollNumber": brojKolone
            })
            numOfLine += 1

        except Exception:
            ret = {
                "message": "Incorrect poll number on line " + str(numOfLine) + "."
            }
            return application.response_class(response=json.dumps(ret), status=400, mimetype='application/json')


    jmbgZvanicnika = get_jwt()["jmbg"]
    with Redis(Configuration.RedisIpAdress) as rd:
        for i in range(len(data)):
            data[i]["jmbgZvanicnika"] = jmbgZvanicnika
            rd.lpush(Configuration.RedisVoteList , str(data[i]))

    return Response(status=200)

@application.route("/" , methods = ["GET"])
def index():
    return "Hello world"

if (__name__ == "__main__"):
    database.init_app(application);
    application.run(debug= True ,host="0.0.0.0", port= 5002)