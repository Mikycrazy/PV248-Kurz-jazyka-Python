import http.server
import urllib3
import json
import urllib.request
import socket
from urllib.error import HTTPError, URLError

PORT = 9999
UPSTREAM = 'httpbin.org/ip'

class MyHandler(http.server.BaseHTTPRequestHandler):

    def do_GET(self):
        url = 'http://{}'.format(UPSTREAM)
        d={}
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

        except socket.timeout:
            d = {'code': "timeout"}
        except (URLError, HTTPError) as error:
            d = {'code': "500", 'content': error.__str__()}
        except Exception as ex:
            print(ex)
        finally:
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            message = json.dumps(d)
            self.wfile.write(message.encode())
    
    def do_POST(self):
        
            content_length = int(self.headers['Content-Length'])    # <--- Gets the size of data
            post_data = self.rfile.read(content_length)             # <--- Gets the data itself
            d={}
            try:
                my_json = json.loads(post_data.decode('utf8').replace("'", '"'))
                url = my_json['url']
                headers = my_json['headers'] if 'headers' in my_json.keys() else {}
                timeout = int(my_json['timeout']) if 'timeout' in my_json.keys() else 1
                request_type = my_json['type'] if 'type' in my_json.keys() else 'GET'
                content = None
                if request_type == 'POST':
                    content = my_json['content'].encode('utf8')        

                req = urllib.request.Request(url, headers=headers, data=content)
                r = urllib.request.urlopen(req, timeout=timeout)
                data = r.read()

                d = {'code': r.status, 'headers': {k:v for k,v in r.headers._headers}}
                try:
                    d['json'] = json.loads(data.decode('utf8').replace("'", '"'))
                except ValueError:
                    d['content'] = data.decode('utf8')

            except (ValueError, KeyError):
                d = {'code': "invalid json" }
            except socket.timeout:
                d = {'code': "timeout"}
            except (URLError, HTTPError) as error:
                d = {'code': "500", 'content': error.__str__()}
            except Exception as ex:
                print(ex)
            finally:
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                message = json.dumps(d)
                self.wfile.write(message.encode())




server_address = ('127.0.0.1', PORT)

try:
    server = http.server.HTTPServer(server_address, MyHandler)
    print('Started http server')
    server.serve_forever()
except KeyboardInterrupt:
    print('^C received, shutting down server')
    server.socket.close()