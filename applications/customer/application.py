from flask import Flask, request, jsonify,Response;
from checkRole import roleCheck;
from configuration import Configuration;
from models import database,Product,Category,ProductCategory,OrderProduct,Order;
from flask_jwt_extended import JWTManager,get_jwt;
from sqlalchemy_utils.types.json import json
import re
from datetime import datetime

application = Flask ( __name__ );
application.config.from_object ( Configuration );

jwt = JWTManager ( application );


@application.route("/search",methods=["GET"])
@roleCheck(role="customer")
def search():
    name = request.args.get("name", "");
    category = request.args.get("category", "");

    #sve kateogorije
    allCategories =[str(c) for c in Category.query.join(ProductCategory).join(Product).filter(Product.name.like(f'%{name}%')).filter(Category.name.like(f'%{category}%')).all()];

    #svi proizvodi
    products = Product.query.join(ProductCategory).join(Category).filter(Product.name.like(f'%{name}%')).filter(Category.name.like(f'%{category}%')).all();
    allProducts=[];
    for p in products:
        categoriesForProduct=[str(category) for category in p.categories];
        product={
            "categories":categoriesForProduct,
            "id":p.id,
            "name":p.name,
            "price":p.price,
            "quantity":p.quantity

        };
        allProducts.append(product);

    return jsonify(categories=allCategories,products=allProducts);


@application.route("/order",methods=["POST"])
@roleCheck(role="customer")
def order():
    requests = request.json.get("requests", "");
    if(len(requests) == 0): #provera da li je poslat request
        return Response(json.dumps({ "message": "Field requests is missing." }), status=400);

    #provera svih requestova
    line=0;
    for req in requests:
        if("id" not in req) :
            return Response(json.dumps({"message": "Product id is missing for request number "+str(line)+"."}), status=400);
        if ("quantity" not in req):
            return Response(json.dumps({"message": "Product quantity is missing for request number " + str(line) + "."}),status=400);
        if(not re.search("[1-9]+",str(req["id"])) or int(req["id"]<0)):
            return Response(json.dumps({"message": "Invalid product id for request number " + str(line) + "."}),status=400);
        if (not re.search("[1-9]+", str(req["quantity"])) or int(req["quantity"]<0)):
            return Response(json.dumps({"message": "Invalid product quantity for request number " + str(line) + "."}),status=400);
        product=Product.query.filter(Product.id == int(req["id"])).all();
        if(not product):
            return Response(json.dumps({"message": "Invalid product for request number " + str(line) + "."}),status=400);
        line+=1;


    #nema gresaka
    orderPrice=0;
    orderStatus="COMPLETE";
    timestamp=datetime.now();
    user=get_jwt()["sub"];

    order=Order(price=orderPrice,status=orderStatus,timestamp=timestamp,user=user);
    database.session.add(order); #dodajemo order zbog idOrder, posle cemo azurirati price i status
    database.session.commit();

    for req in requests:
        productId=int(req["id"]);
        quantity=int(req["quantity"]);
        product = Product.query.filter(Product.id == productId).first();
        orderPrice+=product.price*quantity;
        received=0;
        if(product.quantity<quantity):
            orderStatus="PENDING";
            received=product.quantity;
            product.quantity=0;
        else:
            received=quantity;
            product.quantity -=quantity;
        database.session.commit(); #promena kolicine proizvoda

        orderProduct=OrderProduct(orderId=order.id,productId=product.id,price=product.price,requested=quantity,received=received);
        database.session.add(orderProduct);
        database.session.commit();

    order.status=orderStatus;
    order.price=orderPrice;
    database.session.commit();

    return Response(json.dumps({"id": order.id}), status=200);

@application.route("/status",methods=["GET"])
@roleCheck(role="customer")
def status():
    user = get_jwt()["sub"];
    allOrdersForUser=Order.query.filter(Order.user==user).all();
    orders=[];

    for order in allOrdersForUser:
        products = []; #svi proizvodi odredjene narudzbine
        for orderProduct in OrderProduct.query.filter(OrderProduct.orderId==order.id).all():
           product=Product.query.filter(Product.id==orderProduct.productId).first();
           p={
               "categories": [str(category) for category in product.categories],
               "name":product.name,
               "price":orderProduct.price,
               "received": orderProduct.received,
               "requested":orderProduct.requested
           };
           products.append(p);
        o={
            "products":products,
            "price":order.price,
            "status":order.status,
            "timestamp":order.timestamp.strftime("%Y-%m-%dT%H:%M:%SZ")
        };
        orders.append(o);
    return jsonify(orders=orders);


if ( __name__ == "__main__" ):
    database.init_app ( application );
    application.run ( debug = True,host="0.0.0.0", port = 5002);