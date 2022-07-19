import os;
#redisHost = os.environ["REDIS_URL"];

class Configuration ( ):
    #REDIS_HOST = redisHost;
    REDIS_HOST = "localhost";
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://root:root@localhost:3307/shop";  # proba
    REDIS_PRODUCTS_LIST = "products";
    JWT_SECRET_KEY = "JWT_SECRET_KEY"
