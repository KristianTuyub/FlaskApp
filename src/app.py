"""
A Rest API that simulates the Reddit Posting Dynamic
Author: Christian Tuyub
Date: 2019-08-08
"""

import uuid

from flask import Flask, render_template, jsonify, request, redirect, url_for
# from flask_cors import CORS, cross_origin
from src.RedisConnection import connection
from src.RedisHashDynamic import register_post_in_hash, get_all_post_ids, get_posts_from_db, get_post_value_by_sub_key
from src.RedisZsetDynamic import register_post_in_zset_ordered_by_votes, delete_post_in_zset_ordered_by_votes, \
    get_posts_by_ranking
from src.TemplateNames import TemplateNames

app = Flask(__name__)
# app.config['CORS_HEADERS'] = 'Content-Type'

redis_server = connection()
ZERO_STR = str(0)

# cors = CORS(app, resources={r"/": {"origins": "http://localhost:port"}})


@app.route('/')
def main_page():
    github_repo = 'https://github.com/KristianTuyub/RedditCopyCat'
    return render_template(TemplateNames.HOME_PAGE.value, github_repo=github_repo)


@app.route('/api/posts')
# @cross_origin(origin='localhost', headers=['Content- Type', 'Authorization'])
def get_posts():
    post_ids = get_all_post_ids()
    posts_with_key_values = get_posts_from_db(post_ids)

    json_to_return = jsonify(posts_with_key_values)

    return json_to_return


@app.route('/posts')
def get_posts_html():
    post_ids = get_all_post_ids()
    posts_with_key_values = get_posts_from_db(post_ids)

    # get posts sorted by votes to render posts by ranking section on main page
    posts_sorted_by_votes = get_posts_by_ranking()
    # posts_sorted_by_votes is a list with tuples inside, one by every post. Ex. ("post:9893894834", 21.0)
    #   were first value is the post_id and the second is its number of votes on float format.
    # Next step is to replace post_id by its url
    # posts_sorted_by_votes_with_id_replaced_by_its_url =
    rank_list = []
    for tuple_post in posts_sorted_by_votes:
        post_id = tuple_post[0]
        post_vote_int = int(tuple_post[1])  # casting of number of votes in float to int type
        post_community = get_post_value_by_sub_key(post_id, "community")
        post_title = get_post_value_by_sub_key(post_id, "title")
        built_post_url = "/" + post_community + "/" + post_id
        tuple_post = (post_id, post_vote_int, built_post_url, post_title,)

        rank_list.append(tuple_post)
        # rank_list is a list with tuples with the following elements: (post_id, votes, post_url, post_title)

    return render_template(TemplateNames.POSTS_PAGE.value, posts=posts_with_key_values, posts_sorted_by_votes=rank_list)


@app.route('/api/r/<community>/<post_id>')
def get_post(community, post_id):
    keys = redis_server.keys(post_id)

    if not keys:
        return render_template(TemplateNames.POST_NOT_FOUND.value, post_id=post_id)

    result_list = []

    for key in keys:
        values = redis_server.hgetall(key)
        values["post_id"] = key
        values["url"] = "/" + values["community"] + "/" + key
        values["delete_url"] = "/delete_post/" + key
        result_list.append(values)

    json_to_return = jsonify(result_list)

    return json_to_return


@app.route('/r/<community>/<post_id>')
def get_post_html(community, post_id):
    keys = redis_server.keys(post_id)

    if not keys:
        return render_template(TemplateNames.POST_NOT_FOUND.value, post_id=post_id)

    result_list = []

    for key in keys:
        values = redis_server.hgetall(key)
        values["post_id"] = key
        values["url"] = "/" + values["community"] + "/" + key
        values["add_vote"] = "/add_vote/" + key
        values["remove_vote"] = "/remove_vote/" + key
        values["delete_url"] = "/delete_post/" + key
        result_list.append(values)

    print(result_list[0])
    return render_template(TemplateNames.POST_PAGE.value, post=result_list)


@app.route('/add_vote/<post_id>')
def add_vote(post_id):
    keys = redis_server.keys(post_id)

    if not keys:
        return render_template(TemplateNames.POST_NOT_FOUND.value, post_id=post_id)

    redis_server.hincrby(post_id, "votes", 1)
    # update on the vote ordered zset
    votes = redis_server.hget(post_id, "votes")
    register_post_in_zset_ordered_by_votes(post_id, votes)

    return redirect(url_for("get_posts_html"))


@app.route('/remove_vote/<post_id>')
def remove_vote(post_id):
    keys = redis_server.keys(post_id)

    if not keys:
        return render_template(TemplateNames.POST_NOT_FOUND.value, post_id=post_id)

    redis_server.hincrby(post_id, "votes", -1)
    # update on the vote ordered zset
    votes = redis_server.hget(post_id, "votes")
    register_post_in_zset_ordered_by_votes(post_id, votes)

    return redirect(url_for("get_posts_html"))


@app.route('/delete_post/<post_id>')
def delete_post(post_id):
    all_keys = list(redis_server.hgetall(post_id).keys())

    if len(all_keys) > 0:
        redis_server.hdel(post_id, *all_keys)
        # deletion in votes ordered zset structure
        delete_post_in_zset_ordered_by_votes(post_id)

        return render_template(TemplateNames.DELETED_POST.value, post_id=post_id)
    else:
        return render_template(TemplateNames.POST_NOT_FOUND.value, post_id=post_id)


@app.route('/create_new_post', methods=['GET', 'POST'])
def create_new_post():
    if request.method == 'GET':
        # send the user the form
        return render_template(TemplateNames.NEW_POST.value)
    elif request.method == 'POST':
        # read form data and save it

        post_id = uuid.uuid4()  # Generates a Universally Unique Identifier v4 as a random number
        post_id_int = post_id.int  # Gets the integer version of the UUID (initially is made up Hex Digits)
        hash_id = str(post_id_int)  # Conversion to string for our purposes

        author = request.form['author']
        community = request.form['community']
        title = request.form['title']
        description = request.form['description']

        register_post_in_hash(hash_id, author, community, title, description, ZERO_STR)

        register_post_in_zset_ordered_by_votes("post:" + hash_id, ZERO_STR)

        return render_template(TemplateNames.CREATED_POST.value, post_id=hash_id,
                               post_url="r/" + community + "/" + "post:" + hash_id)
    else:
        return "<h2>Invalid request</h2>"


@app.errorhandler(404)
def notfound(error):
    error_404_code = 404
    """Serve 404 template."""
    return render_template(TemplateNames.ERROR_404.value), error_404_code


if __name__ == '__main__':
    app.run()
