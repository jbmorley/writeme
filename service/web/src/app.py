# Copyright (c) 2024 Jason Morley
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import atexit
import datetime
import errno
import functools
import logging
import os
import re
import sys
import time
import uuid

import psycopg2
import werkzeug

from flask import Flask, send_from_directory, request, redirect, abort, jsonify, g, make_response

import collections.abc
collections.Iterable = collections.abc.Iterable
collections.Mapping = collections.abc.Mapping
collections.MutableSet = collections.abc.MutableSet
collections.MutableMapping = collections.abc.MutableMapping

import database

logging.basicConfig(level=logging.INFO,
                    format="[%(asctime)s] [%(process)d] [%(levelname)s] %(message)s",
                    datefmt='%Y-%m-%d %H:%M:%S %z')


SERVICE_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
VERSION_PATH = os.path.join(SERVICE_DIRECTORY, "VERSION")


# Read the version.
METADATA = {
    "version": "Unknown"
}
if os.path.exists(VERSION_PATH):
    with open(VERSION_PATH) as fh:
        METADATA["version"] = fh.read().strip()

logging.info("Starting service...")
logging.info("Version %s", METADATA["version"])

# Log the build details.
build_number = METADATA["version"]
date_string, sha_string = build_number[:10], build_number[10:]
date = datetime.datetime.strptime(date_string, "%y%m%d%H%M")
sha = "%06x" % int(sha_string)
logging.info("%s (UTC)" % date)
logging.info("https://github.com/jbmorley/writeme/commit/" + sha)

# Create the Flask app.
app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024

def get_database():
    if 'database' not in g:
        logging.info("Connecting to the database...")
        while True:
            try:
                g.database = database.Database()
                break
            except psycopg2.OperationalError:
                time.sleep(0.1)
    return g.database


@app.teardown_appcontext
def close_database(exception):
    db = g.pop('database', None)
    if db is not None:
        logging.info("Closing database connection...")
        db.close()


@app.route('/')
def homepage():
    return send_from_directory('static', 'index.html')


@app.route('/api/v1/queue', methods=['POST'])
def queue_post():
    identifier = str(uuid.uuid4())
    get_database().set_data(identifier, request.files['file'].read())
    return jsonify({})


@app.route('/api/v1/queue/<identifier>', methods=['GET'])
def queue_get(identifier):
    try:
        data, last_modified = get_database().get_data(identifier)
        response = make_response(data)
        response.headers.set('Content-Type', 'application/octet-stream')
        response.headers.set("Access-Control-Allow-Origin", "*")
        response.last_modified = last_modified
        response.cache_control.max_age = 0
        response.make_conditional(request)
        return response
    except KeyError:
        abort(404)


@app.route('/api/v1/queue', methods=['GET'])
def queue():
    args = request.args
    last_anchor = args.get("last_anchor", default=-1, type=int)
    page_size = args.get("page_size", default=20, type=int)
    data = get_database().get_queue(last_anchor=last_anchor, page_size=page_size)
    return jsonify(data)


@app.route('/api/v1/service/about', methods=['GET'])
def service_about():
    return jsonify(METADATA)


if __name__ == '__main__':
    app.run(host='0.0.0.0')
