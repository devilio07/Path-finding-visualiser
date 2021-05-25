from types import LambdaType
import pygame
import math
from queue import PriorityQueue

# Canvas size width = 720p
WIDTH = 600

Window = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("Path finding visualizer")

#Defining colour tuples to be used in grid to highlight.
RED = (255,0,0)
BLUE = (204,229,255)
GREEN = (0,255,0)
YELLOW = (255,255,0)
WHITE = (255,255,255)
BLACK = (0,0,0)
ORANGE = (255,165,0)
GREY = (128,128,128)
PURPLE = (128,0,128)
OLIVE = (128,128,0)

class Node:
    def __init__(self, row, col, width, total_rows):
        self.row =row
        self.col=col
        self.x=row*width
        self.y=col*width
        self.color=BLUE
        self.neighbour =[]
        self.width = width
        self.total_rows = total_rows

    def get_pos(self):
        return self.row, self.col

    def is_closed(self):
        return self.color == YELLOW

    def is_open(self):
        return self.color == GREEN

    def is_barrier(self):
        return self.color == BLACK

    def is_start(self):
        return self.color == ORANGE

    def is_end(self):
        return self.color == RED

    def reset(self):
        self.color = BLUE

    def make_closed(self):
        self.color=YELLOW

    def make_open(self):
        self.color=GREEN

    def make_barrier(self):
        self.color=BLACK

    def make_start(self):
        self.color=ORANGE

    def make_end(self):
        self.color=RED

    def make_path(self):
        self.color=PURPLE

    def draw(self, win):
        pygame.draw.rect(Window, self.color,(self.x,self.y, self.width,self.width))

    def update_neighbours(self, grid):
        self.neighbour = []
        # Lower neighbour
        if self.row < (self.total_rows-1) and not grid[self.row + 1][self.col].is_barrier():
            self.neighbour.append(grid[self.row + 1][self.col])
        # Upper neighbour
        if self.row > 0 and not grid[self.row - 1][self.col].is_barrier():
            self.neighbour.append(grid[self.row - 1][self.col])
        # Left neighbour
        if self.col > 0  and not grid[self.row][self.col - 1].is_barrier():
            self.neighbour.append(grid[self.row][self.col-1])
        # Right neighbour
        if self.col < (self.total_rows-1) and not grid[self.row][self.col + 1].is_barrier():
            self.neighbour.append(grid[self.row][self.col + 1])

    def __lt__(self, other):
        return False

def make_grid(rows, width):
    grid=[]
    gap = width//rows
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            node = Node(i, j, gap, rows)
            grid[i].append(node)
    return grid

def draw_grid(win, rows, width):
    gap = width//rows
    for i in range(rows):
        pygame.draw.line(win, GREY, (0, i*gap),(width, i*gap))
        for j in range(rows):
            pygame.draw.line(win, GREY, (j*gap,0),(j*gap, width))

def draw(win, grid, rows, width):
    win.fill(WHITE)

    for row in grid:
        for node in row:
            node.draw(win)

    draw_grid(win, rows, width)
    pygame.display.update()

def get_click_pos(pos, rows, width):
    gap=width//rows
    y,x = pos

    row = y//gap
    col = x//gap

    return row, col

def H_score(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1-x2) + abs(y1-y2)

def draw_path(parent, current, draw):
    while current in parent:
        current = parent[current]
        current.make_path()
        draw()


def algorithm(draw, grid, start, end):
    print("[INFO] Analysing the grid.....")
    count=0
    open_set = PriorityQueue()
    open_set.put((0, count, start))
    parent = {}
    G_score={node : float("inf") for row in grid for node in row}
    G_score[start]=0
    F_score={node : float("inf") for row in grid for node in row}
    F_score[start] = H_score(start.get_pos(), end.get_pos())

    open_hashset={start}

    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        current = open_set.get()[2]
        open_hashset.remove(current)

        if current==end:
            draw_path(parent, end, draw)
            start.make_start()
            end.make_end()
            return True

        for neighbour in current.neighbour:
            temp_g_score = G_score[current] + 1

            if temp_g_score < G_score[neighbour]:
                parent[neighbour]=current
                G_score[neighbour]= temp_g_score
                F_score[neighbour]=temp_g_score + H_score(neighbour.get_pos(), end.get_pos())
                if neighbour not in open_hashset:
                    count += 1
                    open_set.put((F_score[neighbour], count, neighbour))
                    open_hashset.add(neighbour)
                    neighbour.make_open()

        draw()

        if current!=start:
            current.make_closed()

    return False

def main(win, width):
    ROWS = 30 
    grid = make_grid(ROWS, width)

    start = None
    end = None

    run = True
    started = False

    while run:
        draw(win, grid, ROWS, width)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if pygame.mouse.get_pressed()[0]:
                pos = pygame.mouse.get_pos()
                row, col = get_click_pos(pos, ROWS, width)
                node = grid[row][col]

                if not start and node!= end:
                    start = node
                    start.make_start()
                if not end and node!=start:
                    end = node
                    end.make_end()

                elif node != end and node != start:
                    node.make_barrier()

            elif pygame.mouse.get_pressed()[2]:
                pos = pygame.mouse.get_pos()
                row, col = get_click_pos(pos, ROWS, width)
                node = grid[row][col]
                node.reset()
                if node == start:
                    start = None
                elif node == end:
                    end = None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and start and end:
                    for row in grid:
                        for node in row:
                            node.update_neighbours(grid)

                    # Algorithm will execute everytime space key is pressed.
                    # continue from here tomorrow/ later.
                    algorithm(lambda : draw(win, grid, ROWS, width), grid, start, end)

                if event.key == pygame.K_c:
                    start=None
                    end = None
                    grid = make_grid(ROWS, width)
 

    pygame.quit()

main(Window, WIDTH)