"""
Executes CRUD on the Redis Server
Author: Christian Tuyub
Date: 2019-08-10
"""

from RedisConnection import connection

redis_server = connection()

ZSET_NAME = 'zset:posts_votes'
ZSET_START_RANGE = 0
ZSET_END_RANGE = -1


def register_post_to_zset_ordered_by_votes(post_id, votes):
    redis_server.zadd(ZSET_NAME, {post_id: votes})


def delete_post_on_zset_ordered_by_votes(post_id):
    redis_server.zrem(ZSET_NAME, post_id)


def get_posts_by_ranking():
    posts_sorted_by_votes = redis_server.zrange(ZSET_NAME, ZSET_START_RANGE, ZSET_END_RANGE, withscores=True)
    inverted_list_posts = list(reversed(posts_sorted_by_votes))
    return inverted_list_posts
