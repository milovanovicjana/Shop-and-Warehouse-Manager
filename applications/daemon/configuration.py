import os;
redisHost = os.environ["REDIS_URL"];
databaseUrl = os.environ["DATABASE_URL"];

class Configuration ( ):
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://root:root@{databaseUrl}/shop";
    REDIS_HOST = redisHost;
    #SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://root:root@localhost:3307/shop";  # proba
    #REDIS_HOST = "localhost"; #proba
    REDIS_PRODUCTS_LIST = "products";
    JWT_SECRET_KEY = "JWT_SECRET_KEY"
