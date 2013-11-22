#!/usr/bin/env python

import socket
import sys
import select
import errno
import pdb

class Chatclient:
    BUFFERSIZE = 1024

    def __init__(self):
        self.input_from = []
        self.ns_socket = None

        self.input_from.append(sys.stdin)

    def connect_to_ns(self, ns_ip, ns_port):
        """
        Establish a connection to the name server and
        preform the required handshake
        """
        try:
            self.ns_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.ns_socket.connect((ns_ip, int(ns_port)))
            self.ns_socket.send("HELLO")
            msg = self.ns_socket.recv(self.BUFFERSIZE)
            if msg != '100 CONNECTED':
                self.ns_socket = None
            print msg
        except Exception as e:
            self.ns_socket = None
            print "failed to connect to the given address"
            print e

    def disconnect_from_server(self):
        """
        Close the connection properly to the name server
        """
        self.ns_socket.send('LEAVE')
        response = self.ns_socket.recv(self.BUFFERSIZE)
        if response.split()[0] == '400':
            self.ns_socket.close()
            self.ns_socket = None
            print "Successfully disconnected from name server"


    def request_post(self, name, time):
        """
        Request the connected highscore server to post a time on it's scoreboard
        """
        self.ns_socket.send('POST %s %d' % (name, time))
        print self.ns_socket.recv(self.BUFFERSIZE)


    def request_top(self, n=10):
        """
        Get the list of online users and print it using nice formating
        """
        #pdb.set_trace()
        self.ns_socket.send('TOP %d' % n)
        response = self.ns_socket.recv(self.BUFFERSIZE)
        tokens = response.split()
        if tokens[0] == '300':
            print 'Top %s:' % tokens[2]
            for i in xrange(3, len(tokens)-1, 2):
                print "%s: %s" % (tokens[i], tokens[i+1])
        else:
            print "Something went wrong"
            print response

# Run the client.
if __name__ == "__main__":
    client = Chatclient()
    print 1
    client.connect_to_ns('localhost', 6789)
    print 2
    client.request_top()
