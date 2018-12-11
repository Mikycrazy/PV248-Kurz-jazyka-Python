from HTTPClient import Client
import json
import asyncio
import sys

HOST = 'localhost'
PORT = 15555

PIECE_X = 'X'
PIECE_O = 'O'
PIECE_EMPTY = '_'

def get_peace(player):
    if player == 1:
        return PIECE_X
    elif player == 2:
        return PIECE_O
    else:
        return PIECE_EMPTY   

async def main():

    gameid = None
    player = None

    async with Client(HOST, PORT) as client:
        games = await client.get_games()
        if len(games) == 0:
            print('No games')
        else:
            for record in games:
                print('{}: {}'.format(record['id'], record['name']))

        while True:
            input_str = input()
            if 'new' in input_str:
                parts = input_str.split()
                name = ' '.join(parts[1:]) if len(parts) > 1 else ''
                gameid = await client.create_game(name)
                player = 1
                break
            else:
                try:
                    x = int(input_str)
                    if x not in [x['id'] for x in games]:
                        raise Exception()
                except:
                    print('Invalid game \'{}\''.format(input_str))
                    continue

                gameid = x
                player = 2
                break


        waiting = False
        while True:  
            status = await client.get_status(gameid)    
            if 'board' in status:     
                if status['next'] == player:
                    waiting = False
                    for row in status['board']:
                        print(''.join([get_peace(x) for x in row]))
                    while True:
                        text = input('your turn ({piece}):'.format(piece = get_peace(player)))
                        parts = text.strip().split()
                        try:
                            x = int(parts[0])
                            y = int(parts[1])
                        except:
                            print("Invalid input")
                            continue
                        
                        resp = await client.play(gameid, player, x, y)
                        if resp['status'] == 'ok':
                            break
                        else:
                            print(resp['message'])  
                else:
                    if not waiting:
                        print('waiting for the other player') 
                        waiting = True  
            else:
                if status['winner'] == player:
                    print('YOU WIN')
                elif status['winner'] == 0:
                    print('DRAW')
                else:
                    print('YOU LOSE')
                break
            await asyncio.sleep(1)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())