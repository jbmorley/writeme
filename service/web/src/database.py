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

import logging
import os
import psycopg2
import psycopg2.extras

class Metadata(object):
    SCHEMA_VERSION = "schema_version"


class Transaction(object):

    def __init__(self, connection, **kwargs):
        self.connection = connection
        self.kwargs = kwargs

    def __enter__(self):
        self.cursor = self.connection.cursor(**self.kwargs)
        return self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None and exc_val is None and exc_tb is None:
            self.connection.commit()
        else:
            self.connection.rollback()
        self.cursor.close()


def empty_migration(cursor):
    pass


def create_image_table(cursor):
    cursor.execute("""CREATE TABLE data (
                          id BIGSERIAL PRIMARY KEY,
                          uuid text NOT NULL,
                          data bytea NOT NULL,
                          last_modified timestamptz NOT NULL DEFAULT current_timestamp,
                          UNIQUE(uuid)
                      )""")


class Database(object):

    SCHEMA_VERSION = 1

    MIGRATIONS = {
        1:  create_image_table,
    }

    def __init__(self, database_url=None, readonly=False):

        if database_url is None:
            database_url = os.environ['DATABASE_URL']

        self.connection = psycopg2.connect(database_url)
        self.connection.set_session(readonly=readonly)

        # Migrations are disabled on readonly connections.
        if readonly:
            return

        # Create the metadata table (used for versioning).
        with Transaction(self.connection) as cursor:
            cursor.execute("CREATE TABLE IF NOT EXISTS metadata (key TEXT NOT NULL, value INT, UNIQUE(key))")

        self.migrate()

    def migrate(self):
        with Transaction(self.connection) as cursor:
            cursor.execute("SELECT value FROM metadata WHERE key=%s",
                           (Metadata.SCHEMA_VERSION, ))
            result = cursor.fetchone()
            schema_version = result[0] if result else 0
            logging.info(f"Current schema at version {schema_version}")
            if schema_version >= self.SCHEMA_VERSION:
                return
            for i in range(schema_version + 1, self.SCHEMA_VERSION + 1):
                logging.info(f"Performing migration to version {i}...")
                self.MIGRATIONS[i](cursor)
            cursor.execute("""INSERT INTO metadata(key, value)
                              VALUES (%s, %s)
                              ON CONFLICT (key)
                              DO
                              UPDATE SET value=%s""",
                           (Metadata.SCHEMA_VERSION, self.SCHEMA_VERSION,
                            self.SCHEMA_VERSION))
            logging.info(f"Updated schema to version {self.SCHEMA_VERSION}")

    def set_data(self, key, value):
        with Transaction(self.connection) as cursor:
            cursor.execute("INSERT INTO data (uuid, data, last_modified) VALUES (%s, %s, current_timestamp)",
                           (key, psycopg2.Binary(value)))

    def get_data(self, uuid):
        with Transaction(self.connection) as cursor:
            cursor.execute("SELECT data, last_modified FROM data WHERE uuid = %s",
                           (uuid, ))
            result = cursor.fetchone()
            if result is None:
                raise KeyError(f"No data for key '{key}'")
            return result[0].tobytes(), result[1]

    def get_queue(self, last_anchor, page_size):
        with Transaction(self.connection) as cursor:
            cursor.execute("SELECT id, uuid FROM data WHERE id > %s", (last_anchor, ))
            result = cursor.fetchmany(min(page_size, 20))
            if result is None:
                raise KeyError(f"No data")
            return  [{"anchor": id, "identifier": uuid} for (id, uuid) in result]

    def close(self):
        self.connection.close()
