#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
from urllib.parse import urlparse
from urllib.parse import urlencode

REQUEST = """{} {} HTTP/1.1\r\nHost: {}\r\nConnection: close\r\nUser-Agent: myagent\r\nAccept: */*\r\n{}\r\n{}"""

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        return int(data.splitlines()[0].split()[1])

    def get_headers(self,data):
        return data.split("\r\n\r\n")[0]

    def get_body(self, data):
        return data.split('\r\n\r\n')[1]
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def _parse_url(self, url):
        # https://docs.python.org/3/library/urllib.parse.html
        o = urlparse(url)
        hostname = o.hostname
        port = o.port
        path = o.path

        if o.port is None:
            port = 80
        if o.path is '':
            path = '/'
        if o.query is not '':
            path += '?' + o.query
        if o.fragment is not '':
            path += '#' + o.fragment
        return hostname, port, path

    def _send_data(self,request, hostname, port):
        self.connect(hostname, port)
        self.sendall(request)
        data = self.recvall(self.socket)
        self.close()

        code = self.get_code(data)
        body = self.get_body(data)
        print(body)
        return HTTPResponse(code, body)

    def GET(self, url, args=None):
        hostname, port, path = self._parse_url(url)
        _request = REQUEST.format("GET", path, hostname, "", "")
        return self._send_data(_request, hostname, port)


    def POST(self, url, args=None):
        hostname, port, path = self._parse_url(url)

        if args is not None:
            args = urlencode(args) 
            headers = "Content-Length: " + str(len(args)) + "\r\n"
            headers += "Content-Type: application/x-www-form-urlencoded\r\n"
        else:
            args = ""
            headers = "Content-Length: 0\r\n"
        _request = REQUEST.format("POST", path, hostname, headers, args)

        return self._send_data(_request, hostname, port)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
