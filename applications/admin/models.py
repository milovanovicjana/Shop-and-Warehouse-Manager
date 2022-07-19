from flask_sqlalchemy import SQLAlchemy;

database = SQLAlchemy ( );

class OrderProduct ( database.Model ):
    __tablename__ = "orderproduct";

    id = database.Column ( database.Integer, primary_key = True );
    orderId = database.Column(database.Integer, database.ForeignKey("orders.id"), nullable=False);
    productId = database.Column ( database.Integer, database.ForeignKey ( "products.id" ), nullable = False );
    price = database.Column(database.Float, nullable=False);
    requested = database.Column(database.Integer, nullable=False);
    received = database.Column(database.Integer, nullable=False);


class ProductCategory ( database.Model ):
    __tablename__ = "productcategory";

    id = database.Column ( database.Integer, primary_key = True );
    productId = database.Column ( database.Integer, database.ForeignKey ( "products.id" ), nullable = False );
    categoryId = database.Column ( database.Integer, database.ForeignKey ( "categories.id" ), nullable = False );


class Product ( database.Model ):
    __tablename__ = "products";

    id = database.Column ( database.Integer, primary_key = True );
    name = database.Column ( database.String ( 256 ), nullable = False, unique = True );
    price = database.Column ( database.Float, nullable = False );
    quantity = database.Column ( database.Integer, nullable = False );

    categories = database.relationship ( "Category", secondary = ProductCategory.__table__, back_populates = "products" );

    #dodala
    orders = database.relationship("Order", secondary=OrderProduct.__table__, back_populates="products");

class Category ( database.Model ):
    __tablename__ = "categories";

    id = database.Column ( database.Integer, primary_key = True );
    name = database.Column ( database.String ( 256 ), nullable = False );

    products = database.relationship ( "Product", secondary = ProductCategory.__table__, back_populates = "categories" );

    def __repr__ ( self ):
        return self.name;

#za order

class Order ( database.Model ):
    __tablename__ = "orders";

    id = database.Column ( database.Integer, primary_key = True );
    price = database.Column(database.Float, nullable=False);
    status = database.Column ( database.String ( 256 ), nullable = False);
    timestamp = database.Column(database.DateTime, nullable=False);
    user = database.Column(database.String(256), nullable=False); #zbog search-a cuvamo koji je korisik porucio

    products = database.relationship("Product", secondary=OrderProduct.__table__, back_populates="orders");

