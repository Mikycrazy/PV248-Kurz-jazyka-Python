import pygame, sys, os
import asyncio
from HTTPClient import Client

HOST = 'localhost'
PORT = 15555

SIZE = 560
BOARD_PADDING = 40
FIELD_SIZE = (SIZE - (2 * BOARD_PADDING)) // 3

pygame.init()
pygame.display.set_caption("TicTacTeo")
clock = pygame.time.Clock()
gameDisplay = pygame.display.set_mode((SIZE, SIZE))

white = (255, 255, 255)
black = (0,0,0)
gray = (200,200,200)
light_gray = (220,220,220)
green = (0, 255, 128)
red = (255, 64, 64)
bright_red = (255,0,0)
bright_green = (0,255,0)


class Menu():

    def __init__(self, client):
        pass

class Game():

    PIECE_X = 'X'
    PIECE_O = 'O'
    PIECE_EMPTY = ' '

    @staticmethod
    def get_peace(player):
        if player == 1:
            return Game.PIECE_X
        elif player == 2:
            return Game.PIECE_O
        else:
            return Game.PIECE_EMPTY   


    def __init__(self, client, gameid, player):
        self.gameid = gameid
        self.player = player
        self.turn = 0
        self.over = False
        self.client = client
        self.board = [[0]*3, [0]*3, [0]*3]
        self.display = [[ (BOARD_PADDING + (x * FIELD_SIZE) + (FIELD_SIZE // 2), BOARD_PADDING + (y * FIELD_SIZE) + (FIELD_SIZE // 2)) for x in range(3)] for y in range(3)]

    def draw_board(self):
        for x in range(BOARD_PADDING, SIZE, FIELD_SIZE):
            pygame.draw.line(gameDisplay, black, (x, BOARD_PADDING), (x, SIZE - BOARD_PADDING), 2)
            pygame.draw.line(gameDisplay, black, (BOARD_PADDING, x), (SIZE - BOARD_PADDING, x), 2)

    def display_turn(self):
        font = pygame.font.SysFont("Arial", 30) 
        text_ = font.render(("Player Turn : " + self.get_peace(self.turn)), True, black)
        rect = text_.get_rect()
        rect.midleft = (BOARD_PADDING, 20)
        gameDisplay.blit(text_, rect)   

    def display_player(self):
        font = pygame.font.SysFont("Arial", 30) 
        text_ = font.render(("Player: " + self.get_peace(self.player)), True, black)
        rect = text_.get_rect()
        rect.midright = (SIZE - BOARD_PADDING, 20)
        gameDisplay.blit(text_, rect)    

    def display_status(self):
        for x in range(3):
            for y in range(3):
                if self.board[x][y] != 0:
                    display_text(self.get_peace(self.board[x][y]), self.display[x][y], 60)

    async def mouse_event(self):
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()

        if click[0] == 1:
            y = (mouse[1] - BOARD_PADDING) // FIELD_SIZE
            x = (mouse[0] - BOARD_PADDING) // FIELD_SIZE
            print((x, y))
            if self.turn == self.player:
                res = await self.client.play(self.gameid, self.player, x, y)
                if res['status'] == 'bad':
                    print(res['message']) 


    async def update_status(self):
        status = await self.client.get_status(self.gameid)  

        if 'winner' in status:
            self.gameOver(status['winner'])
            return False

        if 'board' in status:
            self.board = status['board']
        
        if 'next' in status:
            self.turn = status['next']

        return True

    def gameOver(self, winner):
        gameDisplay.fill(white)    
        font = pygame.font.SysFont("Arial", 80, True) 
        text = "DRAW" if winner == 0 else "YOU WIN" if winner == self.player else "YOU LOSE"
        text_ = font.render(text, True, red)
        rect = text_.get_rect()
        rect.center = (SIZE // 2, SIZE // 2)
        gameDisplay.blit(text_, rect)
        pygame.display.update()

def text_objects(text, font):
    textSurface = font.render(text, True, black)
    return textSurface, textSurface.get_rect()

def display_text(text, place, size):
    font = pygame.font.SysFont("Arial", size, True) 
    text_ = font.render(text, True, black)
    rect = text_.get_rect()
    rect.center = place
    gameDisplay.blit(text_, rect) 

async def game_intro(client):
    gameid = None
    player = None
    intro = True
    while intro:
        games = await client.get_games()
        for event in pygame.event.get():
            #print(event)
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
                
        gameDisplay.fill(white)
        display_text("TicTacToe", ((SIZE/2),40), 80)
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        #print(mouse)

        if  BOARD_PADDING + SIZE - (2 * BOARD_PADDING) > mouse[0] > BOARD_PADDING and 120 + 80 > mouse[1] > 120:
            pygame.draw.rect(gameDisplay, bright_red, (BOARD_PADDING, 120, SIZE - (2 * BOARD_PADDING), 80))
            if click[0] == 1:      
                gameid = await client.create_game('game {}'.format(len(games) + 1))
                player = 1
                intro = False
        else:
            pygame.draw.rect(gameDisplay, gray, (BOARD_PADDING, 120, SIZE - (2 * BOARD_PADDING), 80))

        display_text("New game", ((SIZE/2), 160), 40)
        pygame.draw.line(gameDisplay, black, (BOARD_PADDING // 2, 210), (SIZE - (BOARD_PADDING // 2), 210), 2)


        list_start_y = 220
        list_item_size = 50
        for i, game in enumerate(games):
            if  BOARD_PADDING + SIZE - (2 * BOARD_PADDING) > mouse[0] > BOARD_PADDING and list_start_y + (i * (list_item_size + 5)) + list_item_size > mouse[1] > list_start_y + (i * (list_item_size + 5)):
                pygame.draw.rect(gameDisplay, gray, (BOARD_PADDING, list_start_y + (i * (list_item_size + 5)), SIZE - (2 * BOARD_PADDING), list_item_size))
                if click[0] == 1:
                    print(game)
                    gameid = game['id']
                    player = 2
                    intro = False
            else:
                pygame.draw.rect(gameDisplay, light_gray, (BOARD_PADDING, list_start_y + (i * (list_item_size + 5)), SIZE - (2 * BOARD_PADDING), list_item_size))
            display_text('{}: {}'.format(game['id'], game['name']), ((SIZE//2), list_start_y + (i * (list_item_size + 5)) + list_item_size // 2), 25)

        pygame.display.update()
        clock.tick(15)

    return (gameid, player)

async def main_game(client, gameid, player): 
        game = Game(client, gameid, player)
        while True:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    sys.exit()
                    pygame.quit()
                    exit()
            
            if await game.update_status():
                gameDisplay.fill(white)
                game.draw_board() 
                game.display_turn()
                game.display_player()
                game.display_status()
                await game.mouse_event()
                pygame.display.update()

            clock.tick(40)

async def main(): 
    async with Client(HOST, PORT) as client:
        gameid, player = await game_intro(client)
        await asyncio.sleep(0.5)
        await main_game(client, gameid, player)

if __name__ == "__main__":
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())