from random import randint
import pygame
from pygame.locals import *
import sys

HEIGHT = 20
WIDTH = 20

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
GREY = (34, 34, 34)
RED = (210, 0, 0)


FOOD = 0
UNDEF = int(1E3)
SNAKE = int(1E6)

LEFT = -1
RIGHT = 1
UP = -WIDTH
DOWN = WIDTH

DIRC_LIST = [LEFT, UP, RIGHT, DOWN]


# ამ ფუნქციით ვქმნით 'Snake'-ის ფანჯარას და ვუთითებთ თამაშის ძირითად კომპონენტებს.
def reset_all():
    global snake, board, snake_size, _snake, _board, _snake_size, food, score
    board = [0] * HEIGHT * WIDTH  # use one dimensional list to represent 2 dimensional board
    snake = [0] * (HEIGHT * WIDTH + 1)
    snake[0] = 1 * WIDTH + 1
    snake_size = score = 1

    _board = [0] * HEIGHT * WIDTH
    _snake = [0] * (HEIGHT * WIDTH + 1)
    _snake[0] = 1 * WIDTH + 1
    _snake_size = 1

    food = 7 * WIDTH + 8


# ამ ფუნქციით ვქმნით 'Snake'-ის სათამაშო დაფას
def init_board(__snake, __size, __board):
    for i in range(HEIGHT * WIDTH):
        if i == food:
            __board[i] = FOOD
        elif not (i in __snake[:__size]):
            __board[i] = UNDEF
        else:
            __board[i] = SNAKE


# ეს ფუნქცია განსაზღვრავს თამაშში გველის მოძრაობებს(მარცხნივ, მარჯვნივ, ზემოთ, ქვემოთ)
def can_move(pos, dirc):
    if dirc == UP and pos / WIDTH > 0:
        return True
    elif dirc == LEFT and pos % WIDTH > 0:
        return True
    elif dirc == DOWN and pos / WIDTH < HEIGHT - 1:
        return True
    elif dirc == RIGHT and pos % WIDTH < WIDTH - 1:
        return True
    return False


def find_food_path_bfs(__food, __snake, __board):
    found = False
    q = [__food]  # not using Queue() because it is slower
    explored = [0] * (WIDTH * HEIGHT)
    while q:
        pos = q.pop(0)
        if explored[pos] == 1:
            continue
        explored[pos] = 1
        for dirc in DIRC_LIST:
            if can_move(pos, dirc):
                if pos + dirc == __snake[0]:
                    found = True
                if __board[pos + dirc] < SNAKE:
                    if __board[pos + dirc] > __board[pos] + 1:
                        __board[pos + dirc] = __board[pos] + 1
                    if explored[pos + dirc] == 0:
                        q.append(pos + dirc)

    return found


def last_op():
    global snake_size, board, snake, food
    init_board(snake, snake_size, board)
    find_food_path_bfs(food, snake, board)
    mini = SNAKE
    mv = None
    for dirc in DIRC_LIST:
        if can_move(snake[0], dirc) and board[snake[0] + dirc] < mini:
            mini = board[snake[0] + dirc]
            mv = dirc
    return mv


def mv_body(__snake, __snake_size):
    for i in range(__snake_size, 0, -1):
        __snake[i] = __snake[i - 1]


# ეს ფუნქცია აგენერირებს გველის საჭმელს არეულად(random)
def gen_food():
    global food, snake_size
    a = False
    while not a:
        w = randint(1, WIDTH - 2)
        h = randint(1, HEIGHT - 2)
        food = h * WIDTH + w
        a = not (food in snake[:snake_size])


def r_move(__mv):
    global snake, board, snake_size, score
    mv_body(snake, snake_size)
    snake[0] += __mv

    if snake[0] == food:
        board[snake[0]] = SNAKE
        snake_size += 1
        score += 1
        if snake_size < HEIGHT * WIDTH:
            gen_food()
    else:
        board[snake[0]] = SNAKE
        board[snake[snake_size]] = UNDEF


def v_move():
    global snake, board, snake_size, _snake, _board, _snake_size, food
    _snake_size = snake_size
    _snake = snake[:]
    _board = board[:]
    init_board(_snake, _snake_size, _board)

    eaten = False
    while not eaten:
        find_food_path_bfs(food, _snake, _board)
        move = min_mv(_snake, _board)
        mv_body(_snake, _snake_size)
        _snake[0] += move
        if _snake[0] == food:
            _snake_size += 1
            init_board(_snake, _snake_size, _board)
            _board[food] = SNAKE
            eaten = True
        else:
            _board[_snake[0]] = SNAKE
            _board[_snake[_snake_size]] = UNDEF


def final_path():
    global snake, board
    v_move()
    if tail_available():
        return min_mv(snake, board)
    return follow_tail()


def tail_available():
    global _snake_size, _snake, _board, food
    _board[_snake[_snake_size - 1]] = FOOD
    _board[food] = SNAKE
    available = find_food_path_bfs(_snake[_snake_size - 1], _snake, _board)
    for dirc in DIRC_LIST:
        if can_move(_snake[0], dirc) and _snake[_snake_size - 1] == _snake[0] + dirc and _snake_size > 3:
            available = False
    return available


def min_mv(__snake, __board):
    mini = SNAKE
    mv = None
    for dirc in DIRC_LIST:
        if can_move(__snake[0], dirc) and __board[__snake[0] + dirc] < mini:
            mini = __board[__snake[0] + dirc]
            mv = dirc
    return mv


def follow_tail():
    global _board, _snake, food, _snake_size
    _snake_size = snake_size
    _snake = snake[:]
    init_board(_snake, _snake_size, _board)
    _board[_snake[_snake_size - 1]] = FOOD
    _board[food] = SNAKE
    find_food_path_bfs(_snake[_snake_size - 1], _snake, _board)
    _board[_snake[_snake_size - 1]] = SNAKE

    return max_mv(_snake, _board)


def max_mv(__snake, __board):
    maxi = -1
    mv = None
    for dirc in DIRC_LIST:
        if can_move(__snake[0], dirc) and UNDEF > __board[__snake[0] + dirc] > maxi:
            maxi = __board[__snake[0] + dirc]
            mv = dirc
    return mv


def run():
    reset_all()
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
        screen.fill(WHITE)
        pygame.draw.rect(screen, RED, (int(food / WIDTH) * 24, int(food % WIDTH) * 24, 24, 24))
        for i in range(HEIGHT * WIDTH):
            if board[i] == SNAKE:
                pygame.draw.rect(screen, GREY, (int(i / WIDTH) * 24, int(i % WIDTH) * 24, 24, 24))
        init_board(snake, snake_size, board)

        # ამ ფუნქციის ლოგიკა არის რომ იპოვოს დისტანცია გველიდან მის საკვებამდე
        #
        #
        # თუ გამოდის:
        #     ამოწმებს შეუძლია თუ არა გველს მიწვდეს მის კუდს
        #     თუ შეუძლია: მივიდეს საკვებამდე მინიმალური მოძრაობის რაოდენობით
        #     თუ არ შეუძლია: უნდა მიჰყვეს მისი კუდის მოძრაობას
        # თუ არ გამოდის:
        #     უნდა მიჰყვეს მისი კუდის მოძრაობას
        #
        # თუ გველს არ შეუძლია მიწვდეს საკვებს ან მის კუდს:
        #     უნდა გადაადგილდეს 1 ბლოკით არეულად(random) და შეამოწმოს ახლიდან

        best_move = final_path() if find_food_path_bfs(food, snake, board) else follow_tail()
        if best_move is None:
            best_move = last_op()
        if best_move is not None:
            r_move(best_move)
        else:
            break

        pygame.display.update()
        pygame.time.Clock().tick(20)


# ამ ფუნქციით ვქმნით თამაშის დაწების ეკრანს(ფანჯარას) რომელიც გამოდის პროგრამის გაშვებისას. ამ ფანჯარაზე გამოსახულია თამაშის
# სათაური და ჩართვის(Play) ღილაკი
def start_screen():
    start = True
    screen.fill(WHITE)
    pygame.font.init()
    menu = pygame.font.Font("./techkr/test2.ttf", 170).render('Snake', True, GREY)
    ai = pygame.font.Font("./techkr/test2.ttf", 40).render('ხელოვნური ინტელექტი', True, GREY)
    play = pygame.font.Font("./techkr/test2.ttf", 25).render('თამაში', True, WHITE)
    screen.blit(menu, (150, 10))
    screen.blit(ai, (15, 200))
    play_button = pygame.draw.rect(screen, GREY, (187, 300, 100, 50))
    screen.blit(play, (194, 310))

    while start:
        for event in pygame.event.get():
            if event.type == MOUSEBUTTONDOWN:
                if play_button.collidepoint(event.pos):
                    return
            if event.type == QUIT:
                start = False
        pygame.display.update()
    pygame.quit()
    sys.exit()


# ამ ფუნქციით ვქმნით თამაშის დასასრულის ფანჯარას. ამ ფანჯარაზე გამოსახულია 'თამაში დასრულებულია'(Game Over) და დაგროვებული
# ქულების რაოდენობა.
def gg_screen():
    gg = True
    screen.fill(WHITE)
    pygame.font.init()
    game_over = pygame.font.Font("./techkr/test.ttf", 40).render('თამაში დასრულდა', True, GREY)
    str_score = pygame.font.Font("./techkr/test.ttf", 50).render('ქულა: %s' % score, True, GREY)
    term = pygame.font.Font("./techkr/test.ttf", 25).render('გასვლა', True, WHITE)
    back = pygame.font.Font("./techkr/test.ttf", 19).render('დაბრუნება', True, WHITE)
    screen.blit(game_over, (60, 30))
    screen.blit(str_score, (55, 180))
    exit_button = pygame.draw.rect(screen, GREY, (90, 300, 100, 50))
    back_button = pygame.draw.rect(screen, GREY, (300, 300, 100, 50))
    screen.blit(term, (95, 310))
    screen.blit(back, (300, 315))

    while gg:
        for event in pygame.event.get():
            if event.type == MOUSEBUTTONDOWN:
                if back_button.collidepoint(event.pos):
                    return
                if exit_button.collidepoint(event.pos):
                    gg = False
            if event.type == QUIT:
                gg = False
        pygame.display.update()
    pygame.quit()
    sys.exit()


if _name_ == '_main_':
    pygame.init()
    pygame.display.set_caption("Snake Artificial Intelligence")
    screen = pygame.display.set_mode((480, 480))
    while True:
        start_screen()
        run()
gg_screen()
