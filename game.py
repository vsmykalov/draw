import random
from draw import *


N = 7

class Game:
    def __init__(self):
        # 0 -- empty
        # 1 -- first player
        # 2 -- second player
        # -1 -- dead
        self.board = [[0 for i in range(N)] for j in range(N)]
        self.turn = 1

    def inv(self):
        g = Game()
        for i in range(N):
            for j in range(N):
                g.board[i][j] = self.board[N - 1 - i][N - 1 - j]
                if g.board[i][j] > 0:
                    g.board[i][j] = 3 - g.board[i][j]
        g.turn = 3 - self.turn
        return g

    def is_move_valid(self, x, y):
        if self.board[x][y] in [-1, self.turn]: return False
        if self.turn == 1 and x == 0 and y == 0: return True
        if self.turn == 2 and x == N - 1 and y == N - 1: return True
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                xx = x + dx
                yy = y + dy
                if 0 <= xx < N and 0 <= yy < N and self.board[xx][yy] == self.turn:
                    return True
        return False

    def make_move(self, x, y):
        assert self.is_move_valid(x, y)
        if self.board[x][y] == 0:
            self.board[x][y] = self.turn
        else:
            self.board[x][y] = -1
        self.turn = 3 - self.turn


class Strategy:
    def make_move(self, g):
        pass



class RandomStrategy(Strategy):
    def __init__(self):
        self.name = "random"

    def make_move(self, g):
        valid_moves = []
        for x in range(N):
            for y in range(N):
                if g.is_move_valid(x, y):
                    valid_moves.append((x, y))
        if not valid_moves:
            return None
        return random.choice(valid_moves)


class HackedRandomStrategy(Strategy):
    def __init__(self):
        self.name = "hacked random"

    def make_move(self, g):
        valid_moves = []
        for x in range(N):
            for y in range(N):
                if g.board[x][y] != 0 and g.is_move_valid(x, y):
                    valid_moves.append((x, y))
        if valid_moves:
            return random.choice(valid_moves)
        for x in range(N):
            for y in range(N):
                if g.board[x][y] == 0 and g.is_move_valid(x, y):
                    valid_moves.append((x, y))
        if not valid_moves:
            return None
        return random.choice(valid_moves)

class HackedGreedyStrategy(Strategy):
    def __init__(self):
        self.name = "hacked greedy"

    def make_move(self, g):
        if random.randint(0, 1) == 0:
            for x in range(N):
                for y in range(N):
                    if g.board[x][y] != 0 and g.is_move_valid(x, y):
                        return (x, y)
            for x in range(N):
                for y in range(N):
                    if g.board[x][y] == 0 and g.is_move_valid(x, y):
                        return (x, y)
        else:
            for y in range(N):
                for x in range(N):
                    if g.board[x][y] != 0 and g.is_move_valid(x, y):
                        return (x, y)
            for y in range(N):
                for x in range(N):
                    if g.board[x][y] == 0 and g.is_move_valid(x, y):
                        return (x, y)
        return None

class HumanStrategy(Strategy):
    def __init__(self):
        self.name = "human"

    def make_move(self, g):
        self.board = draw.board[0]
        self.board.clicked = []

        while True:
            while not self.board.clicked:
                pass
        
            (x, y) = self.board.clicked.pop()

            if g.is_move_valid(x, y):
                return (x, y)




def play_game(player1, player2):
    g = Game()

    while True:
        if g.turn == 1:
            move = player1.make_move(g)
            if not move: return 2
            g.make_move(*move)

        if g.turn == 2:
            move = player2.make_move(g)
            if not move: return 1
            g.make_move(*move)


def show_game(player1, player2):

    def main():
        g = Game()
        draw.board[0] = Board(N, N, 0, 0, 1, 1)
        draw.board[1] = Board(1, 1, 1.1, 0, 1.6, 0.05)
        draw.board[0].clear()
        draw.board[1].clear()
    
        name1 = 'p1 (%s)' % player1.name
        name2 = 'p2 (%s)' % player2.name
    
        while True:
            if g.turn == 1:
                draw.board[1].data[0][0] = '%s move' % name1
                move = player1.make_move(g)
                if not move:
                    draw.board[1].data[0][0] = '%s WON' % name2
                    return 2
                g.make_move(*move)
    
            elif g.turn == 2:
                draw.board[1].data[0][0] = '%s move' % name2
                move = player2.make_move(g)
                if not move:
                    draw.board[1].data[0][0] = '%s WON' % name1
                    return 1
                g.make_move(*move)
    
            time.sleep(0.25)
            for i in range(N):
                for j in range(N):
                    if g.board[i][j] == 0:
                        draw.board[0].data[i][j] = ""
                    if g.board[i][j] == 1:
                        draw.board[0].text_color[i][j] = (255, 0, 0)
                        draw.board[0].data[i][j] = "X"
                    if g.board[i][j] == 2:
                        draw.board[0].text_color[i][j] = (0, 128, 255)
                        draw.board[0].data[i][j] = "O"
                    if g.board[i][j] == -1:
                        draw.board[0].text_color[i][j] = (255, 255, 255)
                        draw.board[0].data[i][j] = "dead"
                        draw.board[0].bg_color[i][j] = (96, 96, 96)
    run_draw(main, 1.6, 1, 800, 500)

def show_stats(player1, player2, games=1000):
    wins = {1:0, 2:0}

    for i in range(games):
        who_won = play_game(player1, player2)
        #print("game %d --> %d won" % (i, who_won))
        wins[who_won] += 1. / games

    print("total: ", wins)
    