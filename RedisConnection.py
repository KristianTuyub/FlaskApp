"""
Executes the connection to the Redis Server
Author: Christian Tuyub
Date: 2019-08-08
"""

# step 1: import the redis-py client package
import sys

import redis

# step 2: define our connection information for Redis
redis_host = "localhost"
redis_port = 6379
redis_password = ""


def connection():
    """Establishes a connection to redis server"""
    redis_env = None
    # step 3: create the Redis Connection object
    try:
        print("Connecting to redis...")
        # The decode_responses flag here directs the client to convert the responses from Redis into Python strings
        # using the default encoding utf-8.  This is client specific.
        redis_env = redis.StrictRedis(host=redis_host, port=redis_port, password=redis_password,
                                      decode_responses=True)

    except redis.ConnectionError:
        print("Redis isn't running. try command 'redis-server' to start the Redis Server")
        exit(0)

    print("Connection Successful!")

    return redis_env
