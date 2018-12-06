import aiohttp
import json

class Client():
    def __init__(self, host, port):
        self.host = host
        self.port = port

    async def __aenter__(self):
        self.client = aiohttp.ClientSession()
        return self

    async def __aexit__(self, type, value, traceback):
        await self.client.close()

    async def get_json(self, url):
        async with self.client.get(url) as response:
            assert response.status == 200
            return await response.read()

    async def run_command(self, cmd, **kwargs):
        url = 'http://{host}:{port}/'.format(host=self.host, port=self.port)
        args_str = '&'.join(['{}={}'.format(k, v) for k,v in kwargs.items()])
        query = '?' + args_str if len(args_str) > 0 else ''
        data = await self.get_json(url + cmd + query)

        return json.loads(data.decode('utf-8'))

    async def get_status(self, gameid):
        data = await self.run_command('status', game=gameid)
        return data

    async def get_games(self):
        data = await self.run_command('list')
        return data


    async def create_game(self):
        data = await self.run_command('start', name='a')
        return int(data['id'])

    async def play(self, gameid, player, x, y):
        data = await self.run_command('play', game=gameid, player=player, x=x, y=y)
        return data