import pygame, sys, os
import asyncio
from HTTPClient import Client

HOST = 'localhost'
PORT = 15555

SIZE = 560
BOARD_PADDING = 40
FIELD_SIZE = (SIZE - (2 * BOARD_PADDING)) // 3

clock = pygame.time.Clock()
gameDisplay = pygame.display.set_mode((SIZE, SIZE))
white = (255, 255, 255)
black = (0,0,0)
green = (0, 255, 128)
red = (255, 64, 64)

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

    def display_text(self, text, place):
        font = pygame.font.SysFont("Arial", 100, True) 
        text_ = font.render(text, True, black)
        rect = text_.get_rect()
        rect.center = place
        gameDisplay.blit(text_, rect) 

    def display_turn(self):
        font = pygame.font.SysFont("Arial", 30) 
        text_ = font.render(("Player Turn : " + self.get_peace(self.turn)), True, black)
        rect = text_.get_rect()
        rect.center = (100, 20)
        gameDisplay.blit(text_, rect)   

    def change_turn(self):
        if self.turn == 1:
            self.turn = 2
        else:
            self.turn = 1    

    def display_status(self):
        for x in range(3):
            for y in range(3):
                if self.board[x][y] != 0:
                    self.display_text(self.get_peace(self.board[x][y]), self.display[x][y])

    async def mouse_event(self):
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()

        if click[0] == 1:
            y = (mouse[0] - BOARD_PADDING) // FIELD_SIZE
            x = (mouse[1] - BOARD_PADDING) // FIELD_SIZE
            print((self.turn, self.player))
            if self.turn == self.player:
                self.change_turn()
                await self.client.play(self.gameid, self.player, x, y)


    async def update_status(self):
        status = await self.client.get_status(self.gameid)  

        if 'board' in status:
            self.board = status['board']
        
        if 'next' in status:
            self.turn = status['next']

        if 'winner' in status:
            self.gameOver(status['winner'])

    def gameOver(self, winner):
        self.over = True
        font = pygame.font.SysFont("Arial", 40, True) 
        text = "You win" if winner == self.player else "You lose"
        text_ = font.render(text, True, red)
        rect = text_.get_rect()
        rect.center = (SIZE // 2, SIZE // 2)
        gameDisplay.fill(white)    
        gameDisplay.blit(text_, rect)
        pygame.display.update()

async def main(): 
    player = 1
    gameid = 3

    if len(sys.argv) < 3:
        exit("Too less arguments calling script")

    gameid = int(sys.argv[1])
    player = int(sys.argv[2])

    pygame.init()
    pygame.display.set_caption("TicTacTeo")
    async with Client(HOST, PORT) as client:
        game = Game(client, gameid, player)
        while True:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    sys.exit()
                    pygame.quit()
                    exit()
            
            if not game.over:
                gameDisplay.fill(white)
                game.draw_board()
                await game.update_status()
                game.display_turn()
                game.display_status()
                await game.mouse_event()
                pygame.display.update()
            clock.tick(40)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())