import http.server
import urllib3
import json
import urllib.request
from urllib.parse import urlparse

PORT = 9999
UPSTREAM = 'httpbin.org/headers'

class MyHandler(http.server.BaseHTTPRequestHandler):

    def writeFile(self, str):
        self.wfile.write(str.encode("utf-8"))
        pass

    def do_GET(self):
        url = 'http://{}'.format(UPSTREAM)
        try:    
            headers = {x[0]:x[1] for x in self.headers._headers if x[0] not in ('Host')}
            req = urllib.request.Request(url, headers=headers)
            r = urllib.request.urlopen(req, timeout=1)
            data = r.read()
            d = {'code': r.status, 'headers': {k:v for k,v in r.headers._headers }}

            try:
                d['json'] = json.loads(data.decode('utf8').replace("'", '"'))
            except ValueError:
                d['content'] = data.decode('utf8')
            
            self.send_response(r.status)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            message = json.dumps(d)
            self.wfile.write(message.encode())
        except:
            pass
    
    def do_POST(self):
        try:
            # Doesn't do anything with posted data
            content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
            post_data = self.rfile.read(content_length) # <--- Gets the data itself
            my_json = json.loads(post_data.decode('utf8').replace("'", '"'))

            headers = my_json['headers']
            url = my_json['url']
            request_type = my_json['type']
            timeout = int(my_json['timeout']) if 'timeout' in my_json.keys() else 1
            content = None
            if request_type == 'POST':
                content = my_json['content']


            req = urllib.request.Request(url, headers=headers, data=content)
            r = urllib.request.urlopen(req, timeout=timeout)

            data = r.read()
            d = {'code': r.status, 'headers': {k:v for k,v in r.headers._headers }}

            try:
                d['json'] = json.loads(data.decode('utf8').replace("'", '"'))
            except ValueError:
                d['content'] = data.decode('utf8')

            self.send_response(r.status)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            message = json.dumps(d)
            self.wfile.write(message.encode())
        except:
            pass



server_address = ('127.0.0.1', PORT)

try:
    server = http.server.HTTPServer(server_address, MyHandler)
    print('Started http server')
    server.serve_forever()
except KeyboardInterrupt:
    print('^C received, shutting down server')
    server.socket.close()