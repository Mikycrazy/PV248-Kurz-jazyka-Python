import os
import asyncio
import sys
from aiohttp import web
from aiohttp import streamer

DIR = '10/static'

async def get_date():
    code = 'import datetime; print(datetime.datetime.now())'

    # Create the subprocess; redirect the standard output
    # into a pipe.
    proc = await asyncio.create_subprocess_exec(
        sys.executable, '-c', code,
        stdout=asyncio.subprocess.PIPE)

    # Read one line of output.
    data = await proc.stdout.readline()
    line = data.decode('ascii').rstrip()

    # Wait for the subprocess exit.
    await proc.wait()
    return line


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

async def handle(request):
    file_name = request.match_info.get('fileName')
    _, file_extension = os.path.splitext(file_name)
    if file_extension == '.cgi':
        result = await get_date()
        return web.Response(text=result)

    headers = {
        "Content-disposition": "attachment; filename={file_name}".format(file_name=file_name)
    }

    file_path = os.path.join(DIR, file_name)
    if not os.path.exists(file_path):
        return web.Response(
            body='File <{file_name}> does not exist'.format(file_name=file_name),
            status=404
        )
    
    return web.Response(
        body=file_sender(file_path=file_path),
        headers=headers
    )

if sys.platform == 'win32':
    loop = asyncio.ProactorEventLoop()
    asyncio.set_event_loop(loop)

app = web.Application()
app.add_routes([web.get('/', handle),
                web.get('/{fileName}', handle)])

web.run_app(app, port=15555)