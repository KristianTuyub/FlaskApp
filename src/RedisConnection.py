"""
Executes the connection to the Redis Server
Author: Christian Tuyub
Date: 2019-08-08
"""

# step 1: import the redis-py client package
import redis
import os

# step 2: define our connection information for Redis
url = os.environ.get("REDIS_URL")

if url is None:
    redis_host = "localhost"
    redis_port = 6379
    redis_password = ""
elif isinstance(url, str):
    temp_string = url.replace("@", ":")
    temp_string = temp_string.replace("redis://", "")
    temp_list = temp_string.split(":")

    environ_user_index = 0
    environ_password_index = 1
    environ_host_index = 2
    environ_host_port = 3

    redis_host = temp_list[environ_host_index]
    redis_port = temp_list[environ_host_port]
    redis_password = temp_list[environ_password_index]


def connection():
    """Establishes a connection to redis server"""
    redis_env = None
    # step 3: create the Redis Connection object
    try:
        print("Connecting to redis...")
        # The decode_responses flag here directs the client to convert the responses from Redis into Python strings
        # using the default encoding utf-8.  This is client specific.
        redis_env = redis.StrictRedis(host=redis_host,
                                      port=redis_port,
                                      password=redis_password,
                                      decode_responses=True)

    except redis.ConnectionError:
        print("Redis isn't running. try command 'redis-server' to start the Redis Server")
        exit(0)

    print("Connection Successful!")

    return redis_env
