import os;
redisHost = os.environ["REDIS_URL"];

class Configuration ( ):
    REDIS_HOST = redisHost;
    #REDIS_HOST = "localhost";
    REDIS_PRODUCTS_LIST = "products";
    JWT_SECRET_KEY = "JWT_SECRET_KEY"
