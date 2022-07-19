from configuration import Configuration;
from flask import Flask;
from models import database,Product,ProductCategory,Category,OrderProduct,Order;
from redis import Redis;
from sqlalchemy import and_;

application = Flask ( __name__ );
application.config.from_object ( Configuration );
database.init_app(application);

#proverava validnost podataka o proizvodima
while True:
    try:
            with Redis(host=Configuration.REDIS_HOST) as redis:
                while True:
                                bytes = redis.blpop(Configuration.REDIS_PRODUCTS_LIST)[1];

                                with application.app_context() as context:
                                    product = bytes.decode("utf-8");
                                    productItems=product.split("*");
                                    categories=productItems[0].split("|");
                                    name=productItems[1];
                                    quantity=productItems[2];
                                    price=productItems[3]


                                    prod = Product.query.filter(Product.name == name).first();



                                    if(not prod): #ako ne postoji proizvod u bazi, dodajemo ga
                                        newProduct = Product(name=name, price=price, quantity=quantity);
                                        database.session.add(newProduct);
                                        database.session.commit();
                                        for cat in categories:
                                            c = Category.query.filter(Category.name == cat).first();
                                            if (not c):#ako ne postoji kategorija dodajemo i nju
                                                newCategory = Category(name=cat);
                                                database.session.add(newCategory);
                                                database.session.commit();
                                                newProductCategory = ProductCategory(productId=newProduct.id,categoryId=newCategory.id);
                                            else:
                                                newProductCategory = ProductCategory(productId=newProduct.id, categoryId=c.id);
                                            #dodajemo i u veznu tabelu kategoriju za proizvod
                                            database.session.add(newProductCategory);
                                            database.session.commit();
                                            prod=newProduct;#dodala
                                    else: #prozivod postoji
                                        #provera da li se liste slazu
                                        productCategory=ProductCategory.query.filter(ProductCategory.productId==prod.id).all(); #vraca sve kateogrije proizvoda
                                        if(len(productCategory)!=len(categories)):
                                            continue;
                                        found = False;
                                        for pc in productCategory:
                                            found=False;
                                            category=Category.query.filter(Category.id==pc.categoryId).first();
                                            for nameCategory in categories:
                                                if(nameCategory==category.name):
                                                    found=True;
                                                    break;
                                            if(not found):
                                                break;
                                        if(not found):
                                            continue;

                                        #update cene i kolicine proizvoda
                                        quantity=int(quantity);
                                        price=float(price);
                                        newPrice=(prod.quantity*prod.price+quantity*price)/(prod.quantity+quantity);

                                        prod.price=newPrice;
                                        prod.quantity+=quantity;
                                        database.session.commit();



                                    #daemon proverava da li neko ceka
                                    #dohvatamo sve narucene proizvode koji su na cekanju
                                    waintings=OrderProduct.query.filter(OrderProduct.productId==prod.id).filter(OrderProduct.requested>OrderProduct.received).all();
                                    numOfProduct=prod.quantity;

                                    #azuriramo narudzbine po redosledu kreiranja
                                    for wainting in waintings:
                                            if(wainting.requested-wainting.received>numOfProduct):
                                                wainting.received+=numOfProduct;
                                                numOfProduct=0;
                                            else:
                                                numOfProduct-=(wainting.requested-wainting.received);
                                                wainting.received=wainting.requested;
                                            prod.quantity=numOfProduct;
                                            #potencijalna izmena stanja porudzbine
                                            orderProducts=OrderProduct.query.filter(and_(OrderProduct.orderId==wainting.orderId,OrderProduct.requested>OrderProduct.received)).all();#svi proizvodi neke porudzbine koji su na cekanju

                                            if(not orderProducts): #ako nema proizvoda na cekanju u toj narudzbini
                                                order=Order.query.filter(Order.id==wainting.orderId).first();
                                                order.status="COMPLETE";
                                                database.session.commit();

                                            if (numOfProduct == 0):
                                                break;
                                    #cuvanje izmena
                                    database.session.commit();



    except Exception as exception:
        print(exception)
