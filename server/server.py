#!/usr/bin/env python

import socket
import select
import logging

import db


"""
    Protocol:

    Initial responses:
    100 CONNECTED
    101 TAKEN
    102 HANDSHAKE EXPECTED

    Post responses:
    200 POST SUCCESS
    201 POST REJECTED
    202 TIME INVALID

    Lookup responses
    300 INFO <number_of_entries> <name> <time> <name> <time> ...
    301 BAD REQUEST

    Leave responses:
    400 BYE

    Generic Responses:
    500 BAD FORMAT

    Supported Requests:
    HELLO

    POST <name> <time>
    example : POST Andreas 72000000000
    post a time of 1:12.0000 under the name Andreas

    TOP <n>

    LEAVE
    Notify the server, that you are leaving.
"""

class HighscoreServer:
    IP = 'localhost'
    LISTEN_PORT = 6789
    BUFFERSIZE = 1024
    DEFAULT_TIMEOUT = 60
    DB_PATH = 'scoreboard.sqlite'

    def __init__(self):
        self.input_from = []
        self.socks = []

        logging.basicConfig(level=logging.DEBUG
                           , format = '[%(asctime)s] %(levelname)s: %(message)s'
                           )

        self.logger = logging.getLogger('NameServer')

        self.logger.info('Service initialized')

        # Setup socket needed for listening for incoming clients
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((self.IP, self.LISTEN_PORT))
        self.server.listen(self.BUFFERSIZE)
        self.server.setblocking(0)

        self.socks.append(self.server)

        self.scores = db.Scoreboard(self.DB_PATH)

    def test(self, sock):
        print sock.getsockname()

    def run(self):
        """
        The main loop of the name server
        """
        running = True

        while(running):
            # Listen to all connected client sockets and the server socket
            ready_to_read, _, _ = \
                    select.select(self.socks,
                    [],
                    [],
                    self.DEFAULT_TIMEOUT)
            for readable in ready_to_read:
                if readable == self.server:
                    self.connect_to_client(readable);
                else:
                    try:
                        request = readable.recv(self.BUFFERSIZE)
                        if request == '':
                            self.leave_client(readable)
                        else:
                            self.parse_request(request, readable)
                    except Exception as e:
                        self.logger.error(e)
                        self.leave_client(readable)
            
    def connect_to_client(self, sock):
        """
        Establish a connection to a new client and
        preform the required handshake
        """
        conn, addr = self.server.accept()
        readl, _, _ = select.select([conn], [], [], self.DEFAULT_TIMEOUT)
        msg = readl[0].recv(self.BUFFERSIZE)
        tokens = msg.split()
        if len(tokens) == 1 and tokens[0] == 'HELLO':
            response = '100 CONNECTED\n'
            self.socks.append(conn)
            self.logger.info("%s connected to the server" % str(addr))
        else:
            response = '102 HANDSHAKE EXPECTED\n'
        conn.send(response)

    def parse_request(self, request, sock):
        """
        Parse a request from a client and preform the appropriate actions
        """
        tokens = request.split()

        if tokens[0] == "POST" and len(tokens) == 3:
            self.logger.info("User wishes to post a time")
            self.post_time(sock, tokens[1], tokens[2])
        elif tokens[0] == "LEAVE":
            self.logger.info("User wishes to leave service")
            self.leave_client(sock)
        elif tokens[0] == "TOP" and len(tokens) == 2:
            self.logger.info("User requesting top-list")
            self.send_top(sock, tokens[1])
        else:
            self.logger.info("Unrecognized command '%s' ignored" % request)
            sock.send("500 BAD FORMAT\n")
    
    def post_time(self, sock, name, time):
        try:
            parsed_time = long(time)
            self.scores.post(name, parsed_time)
            response = '200 SUCCESS\n'
        except ValueError:
            response = '202 INVALID TIME\n'
        sock.send(response)

    def send_top(self, sock, unparsed_n):
        """
        Send a list of the top n entries. Response should comply with the protocol
        """
        try:
            n = int(unparsed_n)
            rows = self.scores.get_top(n)
            msg = "300 INFO %d" % len(rows)
            for row in rows:
                msg += " %s %d" % (row[0], row[1])
            msg += "\n"
        except Exception as e:
            msg = "301 BAD REQUEST\n"
            print e
        sock.send(msg)


    def leave_client(self, sock):
        """
        Close the connection properly to a leaving client
        """
        try:
            addr = sock.getsockname()
            sock.send('400 BYE\n')
            self.logger.info("%s successfully disconnected from the server", addr)
        except Exception as e:
            self.logger.info("forcebly disconnecting client %s",
                             addr if addr != None else "")
        finally:
            sock.close()
            self.socks.remove(sock)


# Run the server.
if __name__ == "__main__":
    hs = HighscoreServer()
    hs.scores.print_all_times()
    hs.run()

