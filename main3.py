import os
import sys
import numpy as np
import pygame as pg
from pygame import time


def load_image(name):
    filename = os.path.join('data', name)
    try:
        image = pg.image.load(filename)
    except pg.error as error:
        raise SystemExit(error)
    return image


def load_level(filename):
    filename = os.path.join('data', filename)
    # Читаем уровень
    with open(filename, 'r') as mapfile:
        levelmap = np.array([list(i) for i in [line.strip() for line in mapfile]])
    return levelmap


def generate_level(level):
    # Создаём элементы игрового поля:
    data_lst = list()
    x, y = None, None
    row, col = level.shape
    for y in range(row):
        for x in range(col):
            if level[y, x] == '.':
                pass
            elif level[y, x] == '/':
                data_lst.append(Tile('dirt', x, y))
            elif level[y, x] == '?':
                data_lst.append(Tile('dirt_edge', x, y))
            elif level[y, x] == '!':
                data_lst.append(Tile('edge', x, y))
            elif level[y, x] == '2':
                data_lst.append(Tile('dirt_edge2', x, y))
            elif level[y, x] == '1':
                data_lst.append(Tile('edge1', x, y))
            elif level[y, x] == '#':
                data_lst.append(Tile('wall', x, y))
    return data_lst


# разрезание листа с картинками на отдельные кадры
def animasprite(sheet, cols, rows, x, y):
    frames = []
    rect = pg.Rect(0, 0, sheet.get_width() // cols, sheet.get_height() // rows)
    for j in range(rows):
        for i in range(cols):
            frame_location = (rect.w * i, rect.h * j)
            frames.append(sheet.subsurface(pg.Rect(frame_location, rect.size)))
    return frames


class Tile(pg.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__()
        self.image = run.tile_images[tile_type]
        self.rect = self.image.get_rect().move(run.tile_width * pos_x,
                                               run.tile_height * pos_y)
        self.abs_pos = (self.rect.x, self.rect.y)
        self.out()

    def out(self):
        return self.abs_pos[0], self.abs_pos[1], 70, 70


class Camera:
    def __init__(self, width, height):
        self.camera = pg.Rect(0, 0, width, height)
        self.width = width
        self.height = height

    def apply(self, entity):
        return entity.rect.move(self.camera.topleft)

    def update(self, target):
        x = -target.rect.x + int(run.width / 2.2)
        y = -target.rect.y + int(run.height / 2.2)
        # лимит
        x = min(0, x)  # лево
        y = min(0, y)  # верх
        self.camera = pg.Rect(x, y, self.width, self.height)


class Player(pg.sprite.Sprite):
    def __init__(self, game):
        pg.sprite.Sprite.__init__(self)
        self.game = game
        # спрайт игрока
        self.stand = load_image('stand.png')
        self.image = self.stand
        self.rect = pg.rect.Rect((0, 0), (60, 100))
        self.pos = vec(200, 700)
        # трение
        self.friction = -0.12
        # скорость передвижения игрока
        self.vel = vec(0, 0)
        # ускорение
        self.acc = vec(0, 0)
        # переменные для анимации, списки с кадрами
        self.walking = False
        self.walk_r_lst = animasprite(load_image('walk.png'), 4, 1, 0, 0)
        self.walk_l_lst = list()
        for frame in self.walk_r_lst:
            self.walk_l_lst.append(pg.transform.flip(frame, True, False))
        # счетчик кадров
        self.current_frame = 0
        self.last_update = 0
        # в какую сторону смотрит игрок
        self.look = 0

    def jump(self):
        # стоит ли игрок на поверхности
        self.rect.x += 1
        hits = pg.sprite.spritecollide(self, self.game.tiles_group, False)
        self.rect.x -= 1
        if hits:
            self.vel.y = -20

    def update(self):
        self.animate()
        self.acc = vec(0, 0.7)
        # считывание нажатий кнопок передвижения
        key = pg.key.get_pressed()
        if key[pg.K_LEFT] or key[pg.K_a]:
            self.acc.x = -0.65
            self.look = 1
        if key[pg.K_RIGHT] or key[pg.K_d]:
            self.acc.x = 0.65
            self.look = 0
        # ничего не получается :(
        # обновление координат игрока, применение трения
        self.acc.x += self.vel.x * self.friction
        # выравнивание скорости + инерция
        self.vel += self.acc
        if abs(self.vel.x) < 0.1:
            self.vel.x = 0
        self.pos += self.vel + 0.5 * self.acc
        self.rect.midbottom = self.pos

    def animate(self):
        current = pg.time.get_ticks()
        if self.vel.x != 0:
            self.walking = True
        else:
            self.walking = False
        # анимация ходьбы
        if self.walking:
            bottom = self.rect.bottom
            if current - self.last_update > 190:
                self.last_update = current
                self.current_frame = (self.current_frame + 1) % len(self.walk_r_lst)
                if self.vel.x > 0:
                    self.image = self.walk_r_lst[self.current_frame]
                else:
                    self.image = self.walk_l_lst[self.current_frame]
                self.rect = self.image.get_rect()
                self.rect.bottom = bottom
        if not self.walking:
            bottom = self.rect.bottom
            if self.look == 0:
                self.image = self.stand
            else:
                self.image = pg.transform.flip(self.stand, True, False)
            self.rect = self.image.get_rect()
            self.rect.bottom = bottom

def terminate():
    # Определяем отдельную функцию выхода из игры
    pg.quit()
    sys.exit()


# вектор
vec = pg.math.Vector2


def start_screen():
    # заставка
    start_screen_background = load_image('start-screen.jpg')
    run.screen.blit(start_screen_background, (0, 0))
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                terminate()
            elif event.type == pg.KEYDOWN or event.type == pg.MOUSEBUTTONDOWN:
                return  # Начинаем игру
        pg.display.flip()


class Game:
    def __init__(self):
        self.running = True
        pg.init()
        pg.display.set_caption('Roota`s adventure')
        size = self.width, self.height = 1200, 800
        self.clock = pg.time.Clock()
        self.screen = pg.display.set_mode(size)
        self.fps = 60

    def new(self):
        # Тайлы
        self.tile_images = {
            'wall': load_image('grass.png'),
            'dirt': load_image('dark_dirt.png'),
            'edge': load_image('grass2.png'),
            'edge1': load_image('grass2.png'),
            'dirt_edge': load_image('dark_dirt_edge_right.png'),
            'dirt_edge2': load_image('dark_dirt_edge_left.png'),
        }
        # размер тайлов:
        self.tile_width = self.tile_height = 70
        # Группы:
        self.tiles_group = pg.sprite.Group()
        self.all_sprites = pg.sprite.Group()
        self.mobs = pg.sprite.Group()
        # генерация уровня
        self.levelmap = load_level('level-01.map')
        data_lst = generate_level(self.levelmap)
        # помещение тайлов в группы
        for tile in data_lst:
            self.all_sprites.add(tile)
            self.tiles_group.add(tile)
        # камера
        self.camera = Camera(len(self.levelmap), len(self.levelmap[0]))
        # спавн игрока с референсом к классу Game
        self.player = Player(self)
        self.all_sprites.add(self.player)
        self.run()

    def run(self):
        self.running = True
        while self.running:
            self.playing = True
            while self.playing:
                self.clock.tick(self.fps)
                self.events()
                self.update()
                self.draw()

    def update(self):
        self.all_sprites.update()
        self.camera.update(self.player)
        # проверка коллюжена
        hits = pg.sprite.spritecollide(self.player, self.tiles_group, False)
        if hits:
            if self.player.vel.y >= 0:
                self.player.pos.y = hits[0].rect.y
                self.player.vel.y = 0

    def events(self):
        # цикл с событиями
        for event in pg.event.get():
            # закрытие окна
            if event.type == pg.QUIT:
                if self.playing:
                    self.playing = False
                self.running = False
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:
                    self.player.jump()
                    pass

    def draw(self):
        # прорисовка
        self.screen.fill((0, 0, 0))
        for sprite in self.all_sprites:
            self.screen.blit(sprite.image, self.camera.apply(sprite))
        pg.display.flip()

    def show_go_screen(self):
        pass


run = Game()
while run.running:
    run.new()
pg.quit()
