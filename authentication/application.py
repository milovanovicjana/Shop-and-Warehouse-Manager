from flask import Flask, request, Response, jsonify;
from sqlalchemy_utils.types.json import json
import re

from configuration import Configuration;
from models import database, User, UserRole,Role;
from email.utils import parseaddr;
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, create_refresh_token, get_jwt, get_jwt_identity;
from sqlalchemy import and_;
from checkRole import roleCheck;

application = Flask ( __name__ );
application.config.from_object ( Configuration );


@application.route ( "/register", methods = ["POST"] )
def register( ):

    forename=request.json.get("forename","");
    surname = request.json.get("surname","");
    email = request.json.get("email","");
    password = request.json.get("password","");
    isCustomer = request.json.get("isCustomer","");

    #ako bilo koje polje nije uneseno
    if(len(forename) == 0):
        return Response(json.dumps({"message":"Field forename is missing."}), status = 400)
    if (len(surname) == 0):
        return Response(json.dumps({"message": "Field surname is missing."}), status=400)
    if (len(email) == 0):
        return Response(json.dumps({"message": "Field email is missing."}), status=400)
    if (len(password) == 0):
        return Response(json.dumps({"message": "Field password is missing."}), status=400)
    if (len(str(isCustomer)) == 0):
        return Response(json.dumps({"message": "Field isCustomer is missing."}), status=400)

    #provera mejla
    checkEmail=parseaddr(email);
    if(not re.search("^[a-z0-9]+[\._]?[ a-z0-9]+[@]\w+[. ]\w{2,3}$",email)):
         return Response(json.dumps({"message": "Invalid email."}), status=400)

    #provera lozinke
    if(len(password)<8 or len(password)>256 or not re.search("[0-9]",password) or not re.search("[A-Z]",password) or not re.search("[a-z]",password)):
        return Response(json.dumps({"message": "Invalid password."}), status=400)

    #provera da li postoji vec neki korisnik sa zadatim mejlom
    user=User.query.filter(User.email==email).all();
    if(user):
        return Response(json.dumps({"message": "Email already exists."}), status=400)

    #sve provere uspesno prosle

    #dodavanje korisnika
    user=User(
        email=email,
        password=password,
        surname=surname,
        forename=forename
    );
    database.session.add(user);
    database.session.commit();

    if(str(isCustomer)=="True"):
        roleId=2;
    else: roleId=3;

    #dodavanje u veznu tabelu
    userrole=UserRole(userId=user.id,roleId=roleId);
    database.session.add(userrole);
    database.session.commit();

    return     Response("",status = 200);
jwt = JWTManager ( application );
@application.route("/login",methods=["POST"])
def login():

    email = request.json.get("email","");
    password = request.json.get("password","");

    if (len(email) == 0):
        return Response(json.dumps({"message": "Field email is missing."}), status=400)
    if (len(password) == 0):
        return Response(json.dumps({"message": "Field password is missing."}), status=400)

    if (not re.search("^[a-z0-9]+[\._]?[ a-z0-9]+[@]\w+[. ]\w{2,3}$", email)):
        return Response(json.dumps({"message": "Invalid email."}), status=400)

    #provera da li postoji korisnik
    user = User.query.filter(and_(User.email == email,User.password==password)).first();
    if (not user):
        return Response(json.dumps({"message": "Invalid credentials."}), status=400)

    #sve provere uspesno prosle

    #pravljenje access i refresh tokena
    additionalClaims = {
        "forename": user.forename,
        "surname": user.surname,
        "roles": [str(role) for role in user.roles]
    }

    accessToken=create_access_token(identity=user.email,additional_claims=additionalClaims);
    refreshToken = create_refresh_token(identity=user.email, additional_claims=additionalClaims);

    return Response(json.dumps({"accessToken": accessToken,"refreshToken":refreshToken}), status=200)

@application.route("/refresh",methods=["POST"])
@jwt_required ( refresh = True )
def refresh():
    identity=get_jwt_identity();
    refreshClaims=get_jwt();
    additionalClaims={
        "forename": refreshClaims["forename"],
        "surname":  refreshClaims["surname"],
        "roles":  refreshClaims["roles"]
    };

    accessToken=create_access_token(identity=identity,additional_claims=additionalClaims);

    return Response(json.dumps({"accessToken": accessToken}), status=200)

#samo admin moze da vrsi brisanje korisnika, potreban access token pri pozivu

@application.route("/delete",methods=["POST"])
@roleCheck(role="admin")
def delete():
    email = request.json.get("email", "");

    if(len(email)==0):
        return Response(json.dumps({"message": "Field email is missing."}), status=400)

    if (not re.search("^[a-z0-9]+[\._]?[ a-z0-9]+[@]\w+[. ]\w{2,3}$", email)):
        return Response(json.dumps({"message": "Invalid email."}), status=400)

    user = User.query.filter(User.email == email).first();
    if (not user):
        return Response(json.dumps({"message": "Unknown user."}), status=400)

    #sve provere prosle
    #brisanje korisnika(iz obe tabele)
    database.session.delete(user);
    database.session.commit();



    return Response("", status=200);


@application.route("/check",methods=["POST"])
@jwt_required()
def check():
    return "tocken is valid";



#za probu authentication image-a
@application.route("/index",methods=["GET"])
def index():
    return "zdravo svete!";


if ( __name__ == "__main__" ):
    database.init_app ( application );
    application.run ( debug = True, host="0.0.0.0", port = 5000);