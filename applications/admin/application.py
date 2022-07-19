from flask import Flask, request, Response, jsonify;
from checkRole import roleCheck;
from configuration import Configuration;
from models import database,OrderProduct,Product,Category,ProductCategory;
from flask_jwt_extended import JWTManager;
from sqlalchemy import desc,asc,func,and_

application = Flask ( __name__ );
application.config.from_object ( Configuration );

jwt = JWTManager ( application );

@application.route("/productStatistics",methods=["GET"])
@roleCheck(role="admin")
def productStatistics():
    statistics=[];

    count1 = func.sum(OrderProduct.requested);
    count2 = func.sum(OrderProduct.requested-OrderProduct.received);

    products=Product.query.join(OrderProduct,OrderProduct.productId==Product.id) \
        .group_by(Product.id).with_entities(Product.name, count1, count2)\
        .all(); #svi proizvodi koji su prodati

    for p in products:
        statistics.append({
            "name":p[0],
            "sold":int(p[1]),
            "waiting":int(p[2])
        })

    return jsonify(statistics=statistics);

@application.route("/categoryStatistics",methods=["GET"])
@roleCheck(role="admin")
def categoryStatistics():
    statistics=[];

    count=func.sum(func.coalesce(OrderProduct.requested,0));

    categories=Category.query.join(ProductCategory,ProductCategory.categoryId==Category.id,isouter=True).\
        join(Product,Product.id==ProductCategory.productId,isouter=True).\
        join(OrderProduct,OrderProduct.productId==ProductCategory.productId,isouter=True).\
        group_by(Category.id).with_entities(Category.id,count,Category.name).\
        order_by(desc(count)).order_by(asc(Category.name)).all();

    print(categories);
    for category in categories:
        statistics.append(category[2]);

    return jsonify(statistics=statistics);


#za probu admin image-a
@application.route("/index",methods=["GET"])
def index():
    return "novo nesto!";

#modifikacija jun
@application.route("/modifikacija",methods=["GET"])
def modifikacija():
   # kategorije= database.session.query(Category.name,func.sum(OrderProduct.received))\
   # .filter(and_(Category.id==ProductCategory.categoryId,ProductCategory.productId==OrderProduct.productId))\
    #.group_by(Category.id)\
  #  .all();

    kategorije = Category.query.join(ProductCategory,ProductCategory.categoryId==Category.id,isouter=True). \
        join(OrderProduct, OrderProduct.productId == ProductCategory.productId, isouter=True). \
        group_by(Category.id).with_entities(Category.name, func.sum(func.coalesce(OrderProduct.requested-OrderProduct.received,0))).all();
    rezultat=[];
    for k in kategorije:
        rezultat.append({
            "kategorija":k[0],
            "broj cekanja":int(k[1])
        });

    return jsonify(rezultat);




if ( __name__ == "__main__" ):
    database.init_app ( application );
    application.run ( debug = True,host="0.0.0.0", port = 5003 );