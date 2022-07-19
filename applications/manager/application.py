from flask import Flask, request, Response, jsonify;
from sqlalchemy_utils.types.json import json
import re
import io;
import csv;
from checkRole import roleCheck;
from configuration import Configuration;
from models import database;
from redis import Redis;
from flask_jwt_extended import JWTManager;


application = Flask ( __name__ );
application.config.from_object ( Configuration );

jwt = JWTManager ( application );

@application.route("/update",methods=["POST"])
@roleCheck(role="manager")
def uploadFileWithProducts():

    #nije poslat fajl
    if not request.files:
        return Response(json.dumps({"message": "Field file is missing."}), status=400)

    content = request.files["file"].stream.read().decode("utf-8");
    stream = io.StringIO(content);
    reader = csv.reader(stream);

    products = [];
    numberOfLines=0;
    for row in reader:
        if(len(row)!=4):
            return Response(json.dumps({"message": "Incorrect number of values on line "+str(numberOfLines)+"."}), status=400);
        if(not re.search("[0-9]+",row[2])):
            return Response(json.dumps({"message": "Incorrect quantity on line " + str(numberOfLines) + "."}),status=400);
        quantity=int(row[2]);
        if(quantity<=0):
            return Response(json.dumps({"message": "Incorrect quantity on line " + str(numberOfLines) + "."}),status=400);
        if (not re.search("[0-9]+\.[0-9]+", row[3])):
            return Response(json.dumps({"message": "Incorrect price on line " + str(numberOfLines) + "."}),status=400);
        price = float(row[3]);
        if (price <= 0):
            return Response(json.dumps({"message": "Incorrect price on line " + str(numberOfLines) + "."}),status=400);
        products.append(row);
        numberOfLines+=1;

    #ceo fajl dobar
    #dodavanje u redis

    with Redis ( host = Configuration.REDIS_HOST ) as redis:
        for product in products:
            line=product[0]+"*"+product[1]+"*"+product[2]+"*"+product[3];
            redis.rpush ( Configuration.REDIS_PRODUCTS_LIST, line);

    return Response("", status=200);



if ( __name__ == "__main__" ):
    database.init_app ( application );
    application.run ( debug = True,host="0.0.0.0", port = 5001 );