import redis
import json

r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

def get_cachesd_data(key: str):
    return r.get(key)

def set_cashed_data(key: str, data: dict, ttl_seconds: int = 300):
    r.set(key, json.dumps(data), ex=ttl_seconds)