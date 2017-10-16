import pygame
import time
import random
import threading
import sys
import base64

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
        self.bg_color = [[(0, 0, 0) for i in range(cols)] for j in range(rows)]

        self.color = (255, 255, 255)


class Draw:
    def init(self, w, h, real_w=None, real_h=None, border=True):
        #border=False is not properly supported right now
        
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
        fps_text = ' fps: %.0f ' % self.clock.get_fps()
        size = font.size(fps_text)
        label = font.render(fps_text, 0, (255, 255, 255), (0, 0, 0))
        (x, y) = make_xy(self.w, 0)
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

            self.draw()


w, h = 2, 1
def main():
    b = Board(7, 7, 0, 0, 1, 1)
    draw.board[0] = b


    

        




draw = Draw()

if __name__ == "__main__":
    draw.init(w, h, real_w=1000, real_h=500)
    thread = threading.Thread(target=main)
    thread.daemon = True
    thread.start()
    draw.run()
