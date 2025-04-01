import redis
import os

redis_host = os.getenv("REDIS_HOST", "localhost")
redis_port = os.getenv("REDIS_PORT", 6379)

# Initialize Redis client
redis_client = redis.Redis(host=redis_host, port=redis_port, db=0, decode_responses=True)

# Test the connection
try:
    redis_client.ping()
    print("Redis connected successfully!")
except redis.ConnectionError:
    print("Failed to connect to Redis")
