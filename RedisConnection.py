import redis


# Connect to Redis
def connect_to_redis():
    """Connect to a Redis database."""
    r = redis.Redis(host='localhost', port=6379, db=0)
    return r


if __name__ == '__main__':
    r = connect_to_redis()
    # Set a value in Redis
    r.set('mykey', 'Hello World')
    # Get the value from Redis
    value = r.get('mykey')
    # Print the value
    print(value)
