import http.server
import http.client
import json

PORT = 9999
UPSTREAM = 'www.google.com'

class MyHandler(http.server.BaseHTTPRequestHandler):

    def writeFile(self, str):
        self.wfile.write(str.encode("utf-8"))
        pass

    def do_GET(self):
        connection = http.client.HTTPConnection(UPSTREAM, timeout=1)
        print(connection)
        
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()



try:
    server = http.server.HTTPServer(('localhost', PORT), MyHandler)
    print('Started http server')
    server.serve_forever()
except KeyboardInterrupt:
    print('^C received, shutting down server')
    server.socket.close()