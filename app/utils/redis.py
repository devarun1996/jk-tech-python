import redis

# Initialize Redis client
redis_client = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

# Test the connection
try:
    redis_client.ping()
    print("Redis connected successfully!")
except redis.ConnectionError:
    print("Failed to connect to Redis")
