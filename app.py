"""
A Rest API that simulates the Reddit Posting Dynamic
Author: Christian Tuyub
Date: 2019-08-08
"""

import uuid

from flask import Flask, render_template, jsonify, request, make_response, redirect, url_for
# from flask_cors import CORS, cross_origin

from RedisConnection import connection
from RedisDynamic import register_post_to_zset_ordered_by_votes, delete_post_on_zset_ordered_by_votes, \
    get_posts_by_ranking

app = Flask(__name__)
app.config['CORS_HEADERS'] = 'Content-Type'

redis_server = connection()
ZERO_STR = str(0)

# cors = CORS(app, resources={r"/": {"origins": "http://localhost:port"}})


@app.route('/')
def main_page():
    github_repo = 'https://github.com/KristianTuyub/RedditCopyCat'
    return render_template('home.html', github_repo=github_repo)


@app.route('/api/posts')
# @cross_origin(origin='localhost', headers=['Content- Type', 'Authorization'])
def get_posts():
    keys = redis_server.keys('post*')

    result_list = []

    for key in keys:
        values = redis_server.hgetall(key)
        values["post_id"] = key
        values["url"] = "/" + values["community"] + "/" + key
        values["add_vote"] = "/add_vote/" + key
        values["remove_vote"] = "/remove_vote/" + key
        result_list.append(values)

    json_to_return = jsonify(result_list)

    return json_to_return


@app.route('/posts')
def get_posts_html():
    keys = redis_server.keys('post*')

    result_list = []

    for key in keys:
        values = redis_server.hgetall(key)
        values["post_id"] = key
        values["url"] = "/" + values["community"] + "/" + key
        values["add_vote"] = "/add_vote/" + key
        values["remove_vote"] = "/remove_vote/" + key
        result_list.append(values)

    # get posts sorted by votes to render posts by ranking section on main page
    posts_sorted_by_votes = get_posts_by_ranking()
    # posts_sorted_by_votes is a list with tuples inside, one by every post. Ex. ("post:9893894834", 21.0)
    #   were first value is the post_id and the second is its number of votes on float format.
    # Next step is to replace post_id by its url
    # posts_sorted_by_votes_with_id_replaced_by_its_url =
    rank_list = []
    for tuple_post in posts_sorted_by_votes:
        post_id = tuple_post[0]
        post_community = redis_server.hget(post_id, "community")
        post_title = redis_server.hget(post_id, "title")
        built_post_url = "/" + post_community + "/" + post_id
        tuple_post = tuple_post + (built_post_url, post_title, )

        rank_list.append(tuple_post)

    # rank_list is a list with tuples with the following elements:
    #   (post_id, votes, post_url, post_title)

    return render_template("posts.html", posts=result_list, posts_sorted_by_votes=rank_list)


@app.route('/api/r/<community>/<post_id>')
def get_post(community, post_id):
    keys = redis_server.keys(post_id)

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
    return render_template("post.html", post=result_list)


@app.route('/add_vote/<post_id>')
def add_vote(post_id):
    redis_server.hincrby(post_id, "votes", 1)
    # update on the vote ordered zset
    votes = redis_server.hget(post_id, "votes")
    register_post_to_zset_ordered_by_votes(post_id, votes)

    return redirect(url_for("get_posts_html"))


@app.route('/remove_vote/<post_id>')
def remove_vote(post_id):
    redis_server.hincrby(post_id, "votes", -1)
    # update on the vote ordered zset
    votes = redis_server.hget(post_id, "votes")
    register_post_to_zset_ordered_by_votes(post_id, votes)

    return redirect(url_for("get_posts_html"))


@app.route('/delete_post/<post_id>')
def delete_post(post_id):
    all_keys = list(redis_server.hgetall(post_id).keys())
    if len(all_keys) > 0:
        redis_server.hdel(post_id, *all_keys)
        # deletion on votes ordered zset
        delete_post_on_zset_ordered_by_votes(post_id)

        return render_template('deleted_post.html', post_id=post_id)
    else:
        return render_template('post_not_found.html', post_id=post_id)


@app.route('/create_new_post', methods=['GET', 'POST'])
def create_new_post():
    if request.method == 'GET':
        # send the user the form
        return render_template("new_post.html")
    elif request.method == 'POST':
        # read form data and save it
        post_id = uuid.uuid4()
        post_id_int = post_id.int
        hash_id = str(post_id_int)

        author = request.form['author']
        community = request.form['community']
        title = request.form['title']
        description = request.form['description']

        # Store data in database
        # Key name will be a random id generated when posted, concatenated to the post: prefix
        # e.g. post:8753784537438478374

        redis_server.hset("post:" + hash_id, "author", author)
        redis_server.hset("post:" + hash_id, "community", "r/" + community)
        redis_server.hset("post:" + hash_id, "title", title)
        redis_server.hset("post:" + hash_id, "description", description)
        redis_server.hset("post:" + hash_id, "votes", ZERO_STR)

        register_post_to_zset_ordered_by_votes("post:" + hash_id, ZERO_STR)

        return render_template('created_post.html', post_id=post_id_int)
    else:
        return "<h2>Invalid request</h2>"


@app.errorhandler(404)
def notfound(error):
    """Serve 404 template."""
    return render_template("404.html"), 404


if __name__ == '__main__':
    app.run()
