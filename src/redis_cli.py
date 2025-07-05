import redis
import json

def get_redis_connection():
    """Connect to the Redis server."""
    return redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

def set_cache(key, value, ttl=None):
    """Store data in Redis."""
    r = get_redis_connection()
    # If TTL (time to live) is set, store with expiration
    if ttl:
        r.setex(key, ttl, json.dumps(value))  # Store with TTL
    else:
        r.set(key, json.dumps(value))  # Store without TTL

def get_cache(key):
    """Retrieve data from Redis."""
    r = get_redis_connection()
    cached_data = r.get(key)
    if cached_data:
        return json.loads(cached_data)  # Return parsed JSON data
    return None  # Return None if no data is found

def delete_cache(key):
    """Delete data from Redis."""
    r = get_redis_connection()
    r.delete(key)

def cache_exists(key):
    """Check if a key exists in Redis."""
    r = get_redis_connection()
    return r.exists(key)
