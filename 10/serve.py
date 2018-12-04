import os
import asyncio
import sys
from aiohttp import web
from aiohttp import streamer
from concurrent.futures import ThreadPoolExecutor

import re

regex = r"\/(.+?)(\..+?)(\/.*)?$"
DIR = '10/static'
PORT = 15555

e = ThreadPoolExecutor()
async def read_file(file_path):
     loop = asyncio.get_event_loop()
     with open(file_path) as f:
        return (await loop.run_in_executor(e, f.read))


def get_file_name(path):
    m = re.search(regex, path)
    if m:
        file_name = m.group(1)
        file_extension = m.group(2)
        path_info = m.group(3) if m.group(3) else ""

    return file_name, file_extension, path_info

async def run_cgi(file_path, ipt=None):
    proc = await asyncio.create_subprocess_exec(
        file_path,
        stdout=asyncio.subprocess.PIPE,
        stdin=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT)

    if ipt:
        proc.stdin.write(ipt)
        await proc.stdin.drain()

    stdout, _ = await proc.communicate()
    return stdout.decode()

def make_cgi_env(request, file_path, path_info):
        """Set CGI environment variables"""

        env = {}
        env['SERVER_SOFTWARE'] = "09"
        env['SERVER_NAME'] = "aiohttp"
        env['GATEWAY_INTERFACE'] = 'CGI/1.1'
        env['DOCUMENT_ROOT'] = DIR
        env['SERVER_PROTOCOL'] = "HTTP/1.1"
        env['SERVER_PORT'] = str(PORT)

        env['REQUEST_METHOD'] = request.method
        env['REQUEST_URI'] = str(request.raw_path)
        env['PATH_TRANSLATED'] = DIR + path_info
        env['REMOTE_HOST'] = request.host
        env['SCRIPT_NAME'] = file_path
        env['PATH_INFO'] = path_info
        env['QUERY_STRING'] = request.query_string
        env['CONTENT_LENGTH'] = str(request.content_length)
        env['CONTENT_TYPE'] = str(request.content_type)
        for k in request.headers:
            env['HTTP_%s' %k.upper()] = request.headers[k]
        os.environ.update(env)

async def post_handle(request):
    file_name, file_extension, path_info = get_file_name(request.path)
    file_path = os.path.join(DIR, (file_name + file_extension))
    if not os.path.exists(file_path):
        return web.Response(
            body='File <{file_name}> does not exist'.format(file_name=file_name),
            status=404
        )


    data = await request.read()
    
    if file_extension == '.cgi':
        make_cgi_env(request, file_path, path_info)
        result = await run_cgi(file_path, data)
        return web.Response(text=result)

    


async def get_handle(request):

    file_name, file_extension, path_info = get_file_name(request.path)
    file_path = os.path.join(DIR, (file_name + file_extension))
    if not os.path.exists(file_path):
        return web.Response(
            body='File <{file_name}> does not exist'.format(file_name=file_name),
            status=404
        )

    if file_extension == '.cgi':
        make_cgi_env(request, file_path, path_info)
        result = await run_cgi(file_path)
        return web.Response(text=result)
    
    return web.Response(
        body=file_sender(file_path=file_path),
        headers={ "Content-disposition": "attachment; filename={file_name}".format(file_name=file_name) }
    )



@streamer
async def file_sender(writer, file_path=None):
    """
    This function will read large file chunk by chunk and send it through HTTP
    without reading them into memory
    """
    with open(file_path, 'rb') as f:
        chunk = f.read(2 ** 16)
        while chunk:
            await writer.write(chunk)
            chunk = f.read(2 ** 16) 

if sys.platform == 'win32':
    loop = asyncio.ProactorEventLoop()
    asyncio.set_event_loop(loop)

app = web.Application()
app.add_routes([web.get('/{tail:.*}', get_handle),
                web.post('/{tail:.*}', post_handle)])

web.run_app(app, port=15555)