import http.server
import urllib3
import json

PORT = 9999
UPSTREAM = 'httpbin.org/ip'

class MyHandler(http.server.BaseHTTPRequestHandler):

    def writeFile(self, str):
        self.wfile.write(str.encode("utf-8"))
        pass

    def do_GET(self):
        url = 'http://{}'.format(UPSTREAM)
        try:
            http = urllib3.PoolManager()
            headers = {x[0]:x[1] for x in self.headers._headers if x[0] not in ('Connection','User-Agent', 'Host')}
            r = http.request('GET', url, headers=headers)
            self.send_response(r.status)
            for key, value in r.headers._container.items():
                self.send_header(*value)
            self.end_headers()
            self.wfile.write(r.data)
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