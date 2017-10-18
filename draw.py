import pygame                   
import time
import random
import threading
import sys
import base64
import math


class _ADict(dict):
    def __init__(self, *args, **kwargs):
        super(_ADict, self).__init__(*args, **kwargs)
        self.__dict__ = self

def ADict(data):
    if isinstance(data, dict):
        data = _ADict(data)
        for k in data:
            data[k] = ADict(data[k])
    if isinstance(data, list):
        for i in range(len(data)):
            data[i] = ADict(data[i])
    return data


_MARGIN = 20


class Board:
    def __init__(self, rows, cols, x0, y0, x1, y1):
        self.rows = rows
        self.cols = cols

        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1

        self.data = [["" for i in range(cols)] for j in range(rows)]
        self._data = [["" for i in range(cols)] for j in range(rows)]
        self._label = [["" for i in range(cols)] for j in range(rows)]
        self._size = [["" for i in range(cols)] for j in range(rows)]

        self.bg_color = [[(0, 0, 0) for i in range(cols)] for j in range(rows)]
        self.text_color = [[(255, 255, 255) for i in range(cols)] for j in range(rows)]

        self.color = (255, 255, 255)

        self.clicked = []

    def clear_cache(self):
        self._data = [["" for i in range(self.cols)] for j in range(self.rows)]

    def clear(self):
        self.data = [["" for i in range(self.cols)] for j in range(self.rows)]
        self.bg_color = [[(0, 0, 0) for i in range(self.cols)] for j in range(self.rows)]
        

class Draw:
    def init(self, w, h, real_w=None, real_h=None, border=True):
        pygame.font.init()

        self.w = w
        self.h = h

        if not real_w: real_w = w
        if not real_h: real_h = h

        if border:
            real_w = real_w + 2 * _MARGIN
            real_h = real_h + 2 * _MARGIN

        self.real_w = real_w
        self.real_h = real_h

        self.screen = pygame.display.set_mode((real_w, real_h), pygame.RESIZABLE)
        pygame.display.set_caption("ultimate-draw by enot110")

        icon = pygame.image.load('pusheen.png')
        pygame.display.set_icon(icon)

        self.obj = {}
        self.board = {}

        self.clock = pygame.time.Clock()
        self._cached_fps = {}
        
        self.draw()

    def draw(self):
        self.clock.tick()

        scale = min((self.real_w - 2 * _MARGIN) / self.w, (self.real_h - 2 * _MARGIN) / self.h)

        make_xy = lambda x, y: (
            self.real_w / 2 - self.w / 2 * scale + x * scale,
            self.real_h / 2 - self.h / 2 * scale + y * scale
        )

        self.screen.fill((0, 0, 0))

        for o in list(self.obj.values()):
            o = ADict(o)
            if 'color' not in o:
                o.color = (255, 255, 255)
            
            if o.type == 'rect':
                (x0, y0) = make_xy(o.x0, o.y0)
                (x1, y1) = make_xy(o.x1, o.y1)
                pygame.draw.rect(self.screen, o.color, (x0, y0, x1 - x0, y1 - y0), 1)
            if o.type == 'circle':
                (x, y) = make_xy(o.x, o.y)
                r = o.r * scale
                pygame.draw.circle(self.screen, o.color, (int(x), int(y)), int(r), 1)

        for b in list(self.board.values()):
            (x0, y0) = make_xy(b.x0, b.y0)
            (x1, y1) = make_xy(b.x1, b.y1)

            for i in range(b.rows):
                for j in range(b.cols):
                    if b.bg_color[i][j] != (0, 0, 0) or b.data[i][j]:
                        X0 = int(math.floor(x0 + (x1 - x0) * j / b.cols))
                        Y0 = int(math.floor(y0 + (y1 - y0) * i / b.rows))
                        X1 = int(math.ceil(x0 + (x1 - x0) * (j + 1) / b.cols))
                        Y1 = int(math.ceil(y0 + (y1 - y0) * (i + 1) / b.rows))
    
                        if b.bg_color[i][j]:
                            pygame.draw.rect(self.screen, b.bg_color[i][j], (X0, Y0, X1 - X0, Y1 - Y0)) 

                        if b.data[i][j]:

                            if b.data[i][j] == b._data[i][j]:
                                size = b._size[i][j]
                                label = b._label[i][j]
                            else:
                                START = 100
                                font = pygame.font.SysFont("monospace", START)
                                size = font.size(b.data[i][j])
                                alpha = min((X1 - X0) / size[0], (Y1 - Y0) / size[1])
                                true_size = int(START * alpha)
                                while true_size > 0:
                                    font = pygame.font.SysFont("monospace", true_size)
                                    size = font.size(b.data[i][j])
                                    if size[0] <= X1 - X0 - 2 and size[1] <= Y1 - Y0 - 2:
                                        break
                                    true_size -= 1
                             
                                label = font.render(b.data[i][j], 1, b.text_color[i][j])

                                b._size[i][j] = size
                                b._label[i][j] = label
                                b._data[i][j] = b.data[i][j]

                            self.screen.blit(label, ((X0 + X1 - size[0]) / 2, (Y0 + Y1 - size[1]) / 2))
        
            for i in range(b.rows + 1):
                y_mid = y0 + (y1 - y0) * i / b.rows
                pygame.draw.line(self.screen, b.color, (x0, y_mid), (x1, y_mid))
            for i in range(b.cols + 1):
                x_mid = x0 + (x1 - x0) * i / b.cols
                pygame.draw.line(self.screen, b.color, (x_mid, y0), (x_mid, y1))

        rect = (
            self.real_w / 2 - self.w / 2 * scale - _MARGIN / 2,
            self.real_h / 2 - self.h / 2 * scale - _MARGIN / 2,
            self.w * scale + _MARGIN,
            self.h * scale + _MARGIN,
        )
        pygame.draw.rect(self.screen, (255, 255, 255), rect, 1)
        
        font = pygame.font.SysFont("monospace", 16)
        
        fps = int(self.clock.get_fps())
        if fps not in self._cached_fps:
            fps_text = ' fps: %d ' % fps
            size = font.size(fps_text)
            label = font.render(fps_text, 0, (255, 255, 255), (0, 0, 0))
            (x, y) = make_xy(self.w, 0)
            self._cached_fps[fps] = ((x, y), size, label)
        else:
            ((x, y), size, label) = self._cached_fps[fps]

        self.screen.blit(label, (x - _MARGIN - size[0], y - _MARGIN))  
        
        pygame.display.flip()

    
    def run(self):
        self.running = 1
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = 0
                if event.type == pygame.VIDEORESIZE:
                    self.real_w = event.w
                    self.real_h = event.h
                    self.screen = pygame.display.set_mode((self.real_w, self.real_h), pygame.RESIZABLE)
                    for b in list(self.board.values()):
                        b.clear_cache() 

                if event.type == pygame.MOUSEBUTTONDOWN:
                    scale = min((self.real_w - 2 * _MARGIN) / self.w, (self.real_h - 2 * _MARGIN) / self.h)

                    unmake_xy = lambda x, y: (
                        (x - (self.real_w / 2 - self.w / 2 * scale)) / scale,
                        (y - (self.real_h / 2 - self.h / 2 * scale)) / scale
                    )
                    
                    x, y = event.pos
                    x, y = unmake_xy(x, y)

                    for b in list(self.board.values()):
                        if b.x0 <= x <= b.x1 and b.y0 <= y <= b.y1:
                            r = (y - b.y0) * b.rows / (b.y1 - b.y0)
                            c = (x - b.x0) * b.cols / (b.x1 - b.x0)
                            r = max(0, min(b.rows - 1, int(r)))
                            c = max(0, min(b.cols - 1, int(c)))
                            b.clicked.append((r, c))

            self.draw()


draw = Draw()

def run_draw(func, *args, **kwargs):
    draw.init(*args, **kwargs)
    thread = threading.Thread(target=func)
    thread.daemon = True
    thread.start()
    draw.run()


if __name__ == "__main__":
    def main():
        b = Board(7, 7, 0, 0, 1, 1)
        draw.board[0] = b
        
        while True:
            if b.clicked:
                (r, c) = b.clicked.pop()
                b.bg_color[r][c] = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
                x = 0
                if b.data[r][c]: x = int(b.data[r][c])
                b.data[r][c] = str((x + 1) * 3)
        
    
    run_draw(main, 1.6, 1, real_w=800, real_h=500)
