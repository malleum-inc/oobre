import sqlite3
from oobre.config import config

__author__ = 'Nadeem Douba'
__copyright__ = 'Copyright 2012, OOBRE Project'
__credits__ = []

__license__ = 'GPL'
__version__ = '0.1'
__maintainer__ = 'Nadeem Douba'
__email__ = 'ndouba@gmail.com'
__status__ = 'Development'


class Collector(object):

    def dataReceived(self, source, data):
        raise NotImplementedError("Please implement this method.")


class SqliteCollector(Collector):

    create_table_statement = """CREATE TABLE IF NOT EXISTS data(
                                    ID INTEGER PRIMARY KEY AUTOINCREMENT,
                                    src VARCHAR(15),
                                    sport INTEGER,
                                    dst VARCHAR(15),
                                    dport INTEGER,
                                    data BLOB);"""

    def __init__(self, name):
        self.db = sqlite3.connect(config.get(name, 'db_file'))
        self.db.execute(self.create_table_statement)

    def dataReceived(self, connection, data):
        self.db.execute(
            "INSERT INTO data(src, sport, dst, dport, data) VALUES (?,?,?,?,?);",
            (connection.src, connection.sport, connection.dst, connection.dport, data)
        )
        self.db.commit()