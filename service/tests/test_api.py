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

import contextlib
import datetime
import io
import os
import shutil
import subprocess
import sys
import tempfile
import time
import uuid
import unittest
import urllib

import dateutil.parser
import pytz
import requests


TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
SERVICE_DIR = os.path.dirname(TESTS_DIR)
WEB_SERVICE_DIR = os.path.join(SERVICE_DIR, "web", "src")
BUILD_DIR = os.path.join(SERVICE_DIR, "build")

sys.path.append(WEB_SERVICE_DIR)

import database


class RemoteClient(object):

    def __init__(self, base_url):
        self.base_url = base_url
        self.session = requests.Session()

    def get(self, url, *args, **kwargs):
        url = urllib.parse.urljoin(self.base_url, url)
        return self.session.get(url, allow_redirects=False, *args, **kwargs)

    def post(self, url, *args, **kwargs):
        url = urllib.parse.urljoin(self.base_url, url)
        return self.session.post(url, allow_redirects=False, *args, **kwargs)

    def upload(self, url, data):
        return self.post(url, files={'file': io.BytesIO(data)})

    def close(self):
        self.session.close()


@contextlib.contextmanager
def chdir(path):
    pwd = os.getcwd()
    try:
        os.chdir(path)
        yield path
    except:
        os.chdir(pwd)


class TestAPI(unittest.TestCase):

    def setUp(self):
        self.client = RemoteClient(os.environ["TEST_BASE_URL"])

    def tearDown(self):
        self.client.close()

    def test_index(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200, "Fetching index succeeds")

    def test_service_about(self):
        response = self.client.get("/api/v1/service/about")
        self.assertTrue("version" in response.json())


if __name__ == "__main__":
    unittest.main()
