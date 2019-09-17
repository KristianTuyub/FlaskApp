"""
Executes ZSET queries on the Redis Server
Author: Christian Tuyub
Date: 2019-08-10
"""

from src.RedisConnection import connection

redis_server = connection()

ZSET_NAME = 'zset:posts_votes'
ZSET_START_INDEX = 0
ZSET_NUMBER_OF_POSTS_TO_RETRIEVE = 5

ZSET_MIN_SCORE = "-inf"  # - infinite
ZSET_MAX_SCORE = "+inf"  # + infinite


def register_post_in_zset_ordered_by_votes(post_id, votes):
    redis_server.zadd(ZSET_NAME, {post_id: votes})


def delete_post_in_zset_ordered_by_votes(post_id):
    redis_server.zrem(ZSET_NAME, post_id)


def get_posts_by_ranking():
    posts_sorted_by_votes = redis_server.zrevrangebyscore(ZSET_NAME,
                                                          ZSET_MAX_SCORE,
                                                          ZSET_MIN_SCORE,
                                                          withscores=True,
                                                          start=ZSET_START_INDEX,
                                                          num=ZSET_NUMBER_OF_POSTS_TO_RETRIEVE)
    return posts_sorted_by_votes
