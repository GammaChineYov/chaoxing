import redis

class RedisClient:
    def __init__(self, host='localhost', port=6379, db=0, password=None):
        self.client = redis.StrictRedis(host=host, port=port, db=db, password=password, decode_responses=True)

    def set(self, key, value):
        return self.client.set(key, value)

    def get(self, key):
        return self.client.get(key)

    def delete(self, key):
        return self.client.delete(key)
    
    def lpop(self, key):
        return self.client.lpop(key)

    def exists(self, key):
        return self.client.exists(key)

    def lpush(self, key, value):
        return self.client.lpush(key, value)

    def rpop(self, key):
        return self.client.rpop(key)

    def keys(self, pattern='*'):
        return self.client.keys(pattern)

    def flushdb(self):
        return self.client.flushdb()

    def sadd(self, key, value):
        return self.client.sadd(key, value)

    def sismember(self, key, value):
        return self.client.sismember(key, value)