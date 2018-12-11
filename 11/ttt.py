import os
import asyncio
import sys
from aiohttp import web
import json
from board import Board

PORT = 15555

class Counter(object):
    def __init__(self, start=1):
        self.count = start

    def __call__(self):
        val = self.count
        self.count += 1
        return val

class Game:
    def __init__(self, ID, name):
        self.id = ID
        self.name = name
        self.board = Board()
        self.state = 'Empty'
    
    def status(self):
        d = {}
        if self.board.winner != None:
            d['winner'] = self.get_player(self.board.winner)
            self.state = 'Game finished'
        elif self.board.count_placed == 9:
            d['winner'] = 0
            self.state = 'Game finished'
        else:
            d['board'] = [[self.get_player(y) for y in x] for x in self.board.board] 
            d['next'] = self.get_player(self.board.turn)
        return d
        
    def play(self, player, x, y):
        if player not in (1, 2):
            raise ValueError('Player {player} is not part of game'.format(player=player))

        if x not in (0, 1, 2) or y not in (0, 1, 2):
            raise ValueError('Invalid coordinates')

        self.state = 'Running'
        self.board.place(self.get_peace(player), ((y * 3) + x))

    @staticmethod
    def get_player(peace):
        if peace == Board.PIECE_O:
            return 2
        elif peace == Board.PIECE_X:
            return 1
        else:
            return 0

    @staticmethod
    def get_peace(player):
        if player == 1:
            return Board.PIECE_X
        elif player == 2:
            return Board.PIECE_O
        else:
            return Board.PIECE_EMPTY      

class Handler:

    def __init__(self):
        self.games = {}
        self.counter = Counter()

    async def handle_start(self, request):
        name = request.rel_url.query['name'] if 'name' in request.rel_url.query else ''
        ID = self.counter()

        game_obj = Game(ID, name)
        self.games[ID] = game_obj

        d = {'id': ID}
        return web.json_response(d)  

    async def handle_status(self, request):
        try:
            ID = int(request.rel_url.query['game'])
        except:
            raise web.HTTPBadRequest()

        if ID not in self.games:
            return web.Response(
                body='Game <{id}> does not exist'.format(id=ID),
                status=404
                )

        d = self.games[ID].status()
        return web.json_response(d)    


    async def handle_play(self, request):
        try:
            ID = int(request.rel_url.query['game'])
            player = int(request.rel_url.query['player'])
            x = int(request.rel_url.query['x'])
            y = int(request.rel_url.query['y'])
        except:
            raise web.HTTPBadRequest()

        if ID not in self.games.keys():
            return web.Response(
                body='Game <{id}> does not exist'.format(id=ID),
                status=404
                )

        try:
            self.games[ID].play(player, x, y)
            d = {'status': 'ok'}
        except Exception as ex:
            d = {'status': 'bad', 'message': ex.__str__()}
        finally:
            return web.json_response(d) 

    async def handle_list(self, request):
        d = [{'id':game.id, 'name':game.name} for game in self.games.values() if game.state == 'Empty']
        return web.json_response(d)   

app = web.Application()
handler = Handler()
app.add_routes([web.get('/start', handler.handle_start),
                web.get('/status', handler.handle_status),
                web.get('/list', handler.handle_list),
                web.get('/play', handler.handle_play)])

web.run_app(app, port=PORT)