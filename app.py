"""
A Rest API that simulates the Reddit Posting Dynamic
Author: Christian Tuyub
Date: 2019-08-08
"""

import uuid

from flask import Flask, render_template, jsonify, request, make_response, redirect
from flask_cors import CORS, cross_origin

from RedisConnection import connection

app = Flask(__name__)
app.config['CORS_HEADERS'] = 'Content-Type'

redis_server = connection()
ZERO_STR = str(0)

cors = CORS(app, resources={r"/": {"origins": "http://localhost:port"}})


@app.route('/')
def main_page():
    return render_template('home.html')


@app.route('/posts')
@cross_origin(origin='localhost', headers=['Content- Type', 'Authorization'])
def get_posts():
    keys = redis_server.keys('*')

    result_list = []

    for key in keys:
        values = redis_server.hgetall(key)
        values["post_id"] = key
        values["url"] = "/" + values["community"] + "/" + key
        result_list.append(values)

    json_to_return = jsonify(result_list)

    return json_to_return


@app.route('/r/<community>/<post_id>')
def get_post(community, post_id):
    keys = redis_server.keys(post_id)

    result_list = []

    for key in keys:
        values = redis_server.hgetall(key)
        values["post_id"] = key
        values["url"] = "/" + values["community"] + "/" + key
        values["delete_url"] = "/delete_post/" + key
        result_list.append(values)
        print(result_list)

    json_to_return = jsonify(result_list)

    return json_to_return


@app.route('/add_vote/<post_id>', methods=['PUT'])
def add_vote(post_id):
    redis_server.hincrby(post_id, "votes", 1)

    return redirect('/', 200, None)


@app.route('/remove_vote/<post_id>', methods=['PUT'])
def remove_vote(post_id):
    redis_server.hincrby(post_id, "votes", -1)

    return redirect('/', 200, None)


@app.route('/delete_post/<post_id>', methods=['DELETE'])
def delete_post(post_id):
    all_keys = list(redis_server.hgetall(post_id).keys())
    if len(all_keys) > 0:
        redis_server.hdel(post_id, *all_keys)
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

        # Store data in data store
        # Key name will be whatever title they typed in : Question
        # e.g. music:question countries:question
        # e.g. music:answer countries:answer

        redis_server.hset("post:" + hash_id, "author", author)
        redis_server.hset("post:" + hash_id, "community", "r/" + community)
        redis_server.hset("post:" + hash_id, "title", title)
        redis_server.hset("post:" + hash_id, "description", description)
        redis_server.hset("post:" + hash_id, "votes", ZERO_STR)

        return render_template('created_post.html', post_id=post_id_int)
    else:
        return "<h2>Invalid request</h2>"


@app.errorhandler(404)
def notfound(error):
    """Serve 404 template."""
    return render_template("404.html"), 404


if __name__ == '__main__':
    app.run()
