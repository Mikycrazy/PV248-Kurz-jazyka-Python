class Board:
    PIECE_X = 'X'
    PIECE_O = 'O'
    PIECE_EMPTY = '_'

    def __init__(self):
        self.board = [[self.PIECE_EMPTY]*3, [self.PIECE_EMPTY]*3, [self.PIECE_EMPTY]*3]
        self.winner = None
        self.turn = self.PIECE_X
        self.count_placed = 0

    def __getitem__(self, index):
        return self.board[index // 3][index % 3]
    
    def __setitem__(self, index, value):
        self.board[index // 3][index % 3] = value

    def place(self, symbol, index):
        if self.winner:
            raise RuntimeError('Player "{}" has already won the game.'.format(self.winner))
        
        if symbol != self.PIECE_X and symbol != self.PIECE_O:
            raise ValueError('Symbol must either be PIECE_O or PIECE_X')
        
        if symbol != self.turn:
            raise RuntimeError("It's not {}'s turn.".format(symbol))
        
        if self[index] != self.PIECE_EMPTY:
            raise RuntimeError('Spot {} already has a piece by the opposite player.'.format(index))
        
        self[index] = symbol
        self.turn = self.PIECE_X if self.turn == self.PIECE_O else self.PIECE_O
        self.count_placed += 1

        if self._check_for_win():
            pass

    def _check_for_win(self):
        """Check if a player has won."""
        for player in [self.PIECE_X, self.PIECE_O]:
            # 1. Check all rows
            for row in self.board:
                if all(map(lambda piece: piece == player, row)):
                    self.winner = player
                    return True
        
            # 2. Check all columns
            for column in zip(*self.board):
                if all(map(lambda piece: piece == player, column)):
                    self.winner = player
                    return True
        
            # 3. Check the two diagonals
            diagonals = [
                [self[0], self[4], self[8]],
                [self[2], self[4], self[6]],
            ]
            for diagonal in diagonals:
                if all(map(lambda piece: piece == player, diagonal)):
                    self.winner = player
                    return True
    
        return False

    def __str__(self):
        return '\n'.join(' '.join(row) for row in self.board)    
    