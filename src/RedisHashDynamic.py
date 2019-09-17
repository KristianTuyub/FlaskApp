"""
Executes HASH queries on the Redis Server
Author: Christian Tuyub
Date: 2019-08-12
"""

from src.RedisConnection import connection

redis_server = connection()
pipeline = redis_server.pipeline()  # Generate a pipeline

POSTS_KEY_NAME_PATTERN = "post*"


def register_post_in_hash(hash_id, author, community, title, description, default_value):
    # Store a post in redis database
    # Key name will be a random id (hash_id) generated when posted, concatenated to the "post:" prefix
    # e.g. post:8753784537438478374
    pipeline.hset("post:" + hash_id, "author", author)
    pipeline.hset("post:" + hash_id, "community", "r/" + community)
    pipeline.hset("post:" + hash_id, "title", title)
    pipeline.hset("post:" + hash_id, "description", description)
    pipeline.hset("post:" + hash_id, "votes", default_value)

    pipeline.execute()


def get_all_post_ids():
    post_names = redis_server.keys(POSTS_KEY_NAME_PATTERN)

    return post_names


def get_posts_from_db(post_ids):
    result_list = []

    for post_id in post_ids:
        values = redis_server.hgetall(post_id)
        values["post_id"] = post_id
        values["url"] = "/" + values["community"] + "/" + post_id
        values["add_vote"] = "/add_vote/" + post_id
        values["remove_vote"] = "/remove_vote/" + post_id
        result_list.append(values)

    return result_list


def get_post_value_by_sub_key(post_id, sub_key):
    post_value = redis_server.hget(post_id, sub_key)

    return post_value
