#!/usr/bin/env python

"""
Copyright (C) 2014 TopCoder Inc., All Rights Reserved.

Mock backend response

@author: TCSASSEMBLER
@version: 1.0
"""
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import os

class CustomHTTPRequestHandler(BaseHTTPRequestHandler):
    BASE_DATA_PATH = os.path.dirname(os.path.abspath(__file__)) + '/data'
    def do_GET(self):
        print 'data' + self.BASE_DATA_PATH
        try:
            if self.path == "/epa/cyano/blooming/":
                print self.BASE_DATA_PATH
                with open(self.BASE_DATA_PATH + "/prediction_result.json", 'r') as f:

                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(f.read())
            elif self.path == "/epa/cyano/analysis/":
                with open(self.BASE_DATA_PATH + "/aggregate_data.json", 'r') as f:

                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(f.read())
            else:
                with open(self.BASE_DATA_PATH + "/err.html", 'r') as f:
                    self.send_response(404)
                    self.send_header('Content-type', 'text-html')
                    self.end_headers()
                    self.wfile.write(f.read())
        except IOError:
            self.send_error(404, "File Not Found")


def run():
    print('http server is starting on port 8989')

    server_address = ('127.0.0.1', 8989)
    httpd = HTTPServer(server_address, CustomHTTPRequestHandler)
    print('http server is running...')
    httpd.serve_forever()

if __name__ == '__main__':
    run()