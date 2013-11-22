import sqlite3

class Scoreboard(object):
    def __init__(self, path):
        self.conn = sqlite3.connect(path)

    def post(self, name, time):
        """
        Post at time in the scoreboard
        """
        c = self.conn.cursor()
        c.execute('INSERT INTO times VALUES (?, ?)', (name, time))
        self.conn.commit()

    def get_top(self, n=10):
        """
        Return the top n rows from the scoreboard, sorted by time
        """
        c = self.conn.cursor()
        c.execute("SELECT * FROM times ORDER BY time LIMIT ?", (n,))
        return c.fetchall()

    def print_all_times(self):
        """
        Print all recorded times
        """
        c = self.conn.cursor()
        c.execute('SELECT * FROM `times`')
        for row in c.fetchall():
            print row



