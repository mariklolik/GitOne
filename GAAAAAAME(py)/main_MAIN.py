import pygame
import os
import sys
from random import randint
from random import choice

pygame.init()
pygame.joystick.init()
flag_joy = 1
try:
    joy = pygame.joystick.Joystick(0)
    joy.init()
    print("Enabled joystick: {0}".format(joy.get_name()))
except pygame.error:
    flag_joy = 0
    print("no joystick")

FPS = 50
size = width, height = 800, 600
screen = pygame.display.set_mode(size)
running = True
clock = pygame.time.Clock()
screen.fill((255, 255, 255))


def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
    intro_text = ["Press any key to continue -->"]
    font_name = os.path.join('data', 'font.ttf')
    fon = pygame.transform.scale(load_image('fon.png'), (width, height))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(font_name, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('black'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, (0.1 * width, height - 100))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif flag_joy and event.type in [pygame.JOYAXISMOTION, pygame.JOYHATMOTION, pygame.JOYBUTTONDOWN, pygame.JOYBALLMOTION]:
                return  # начинаем игру
            elif event.type == pygame.KEYDOWN and not flag_joy:
                return
        pygame.display.flip()
        clock.tick(FPS)


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    image = pygame.image.load(fullname).convert()
    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


horizontal_borders = pygame.sprite.Group()
vertical_borders = pygame.sprite.Group()
all_bullets = pygame.sprite.Group()  # выстрелы
all_back = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()  # герой
all_borders = pygame.sprite.Group()
all_balls = pygame.sprite.Group()

x, xw, y = 0, 0, 0


class Border(pygame.sprite.Sprite):

    def __init__(self, x1, y1, x2, y2):
        super().__init__(all_borders)
        if x1 == x2:
            self.add(vertical_borders)
            self.image = pygame.Surface([1, y2 - y1])
            self.rect = pygame.Rect(x1, y1, 1, y2 - y1)
        else:
            self.add(horizontal_borders)
            self.image = pygame.Surface([x2 - x1, 1])
            self.rect = pygame.Rect(x1, y1, x2 - x1, 1)


class Back(pygame.sprite.Sprite):
    image1 = load_image("industrial_back.jpg")
    image1 = pygame.transform.scale(image1, (width, height))
    image2 = load_image("forest_back.png")
    image2 = pygame.transform.scale(image2, (width, height))
    image = choice([image1, image2])

    def __init__(self, group):
        # НЕОБХОДИМО вызвать конструктор родительского класса Sprite. Это очень важно!!!
        super().__init__(group)
        self.image = Back.image
        self.rect = self.image.get_rect()
        self.rect.x = 0
        self.rect.y = 0


class Hero(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y):
        super().__init__(all_sprites)
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.image = pygame.transform.scale(self.image, (150, 150))
        self.counter = 0
        self.left = []
        self.right = []
        self.dead = []
        self.cut_sheet(load_image("dead_inside.png", -1), 6, 1, True)
        self.rect = self.rect.move(x, y)
        self.flag_end = 0
        self.flag_shield = False

    def cut_sheet(self, sheet, columns, rows, dead=False):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                if dead:
                    self.dead.append(sheet.subsurface(pygame.Rect(
                        frame_location, self.rect.size)))
                else:
                    self.frames.append(sheet.subsurface(pygame.Rect(
                        frame_location, self.rect.size)))

    def update(self, way=False):
        global x, xw, y, flag_shield
        self.left = self.frames[:9]
        self.right = self.frames[18:27]
        self.counter += 1
        if pygame.sprite.spritecollideany(self, all_balls) and not flag_shield:
            if self.counter % 8 == 0:
                self.cur_frame = (self.cur_frame + 1) % len(self.dead)
                self.image = pygame.transform.scale(self.dead[self.cur_frame], (150, 150))
                self.flag_end += 1
                if self.flag_end == 4:
                    self.kill()
        elif flag_shield:
            self.image = load_image("shield.png", -1)
            self.image = pygame.transform.scale(self.image, (150, 150))
            flag_shield = True
        elif way and not flag_shield:
            if way == "shoot":
                self.image = load_image("shoot.png", -1)
                self.image = pygame.transform.scale(self.image, (150, 150))
                x, xw, y = self.rect.x, self.rect.x + self.rect.w, self.rect.y
            elif not flag_shield:
                if not pygame.sprite.spritecollideany(self, vertical_borders):
                    if way > 0:
                        self.cur_frame = (self.cur_frame + 1) % len(self.right)
                        self.image = pygame.transform.scale(self.right[self.cur_frame], (150, 150))
                        self.rect.x += way * 10
                    elif way < 0:
                        self.cur_frame = (self.cur_frame + 1) % len(self.left)
                        self.image = pygame.transform.scale(self.left[self.cur_frame], (150, 150))
                        self.rect.x += way * 10
                    if self.counter % 30 == 0:
                        self.counter = 0
                else:
                    if self.rect.x + self.rect.w <= width:
                        self.rect.x += 1
                    elif self.rect.x - self.rect.w >= 0:
                        self.rect.x -= 1



class AnimatedBall(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y, lifes):
        super().__init__(all_balls)
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.image = pygame.transform.scale(self.image, (80, 80))
        self.rect = self.rect.move(x, y)
        self.counter = 0
        self.lifes = lifes
        self.vx = randint(-5, 10)
        self.vy = randint(-5, 10)

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self):
        global flag_shield, score
        if self.counter % 5 == 0:
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
            self.image = pygame.transform.scale(self.frames[self.cur_frame], (80, 80))

            self.counter = 0
        self.rect = self.rect.move(self.vx, self.vy)
        if pygame.sprite.spritecollideany(self, all_sprites) and flag_shield:
            self.rect.y -= 5
            self.rect.x += 5
            self.vy = -self.vy - 1
            self.vx = -self.vx - 1
        if pygame.sprite.spritecollideany(self, horizontal_borders):
            self.vy = -self.vy
        if pygame.sprite.spritecollideany(self, vertical_borders):
            self.vx = -self.vx
        if pygame.sprite.spritecollideany(self, all_bullets):
            self.lifes -= 1
            if self.lifes == 0:
                AnimatedBall(load_image("ball.png", -1), 3, 3, self.rect.x - 10, self.rect.y, 2)
                AnimatedBall(load_image("ball.png", -1), 3, 3, self.rect.x + 10, self.rect.y, 2)
                score += 100
                self.kill()
        self.counter += 1


class Bullet(pygame.sprite.Sprite):

    def __init__(self, x, y, type):
        super().__init__(all_bullets)
        if type == "r":
            image = load_image("ball3.png", -1)
        else:
            image = load_image("ball4.png", -1)
        image = pygame.transform.scale(image, (60, 60))
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.mode = 0
        self.type = type
        self.lifes = 3
        if self.type == "r":
            self.add = 2
            self.add1 = -2
        else:
            self.add = -2
            self.add1 = -2

    def update(self, ev=False):
        if self.lifes == 0:
            self.kill()

        self.rect = self.rect.move(self.add, self.add1)
        if pygame.sprite.spritecollideany(self, horizontal_borders):
            self.add1 = -self.add1
            self.lifes -= 1
        if pygame.sprite.spritecollideany(self, vertical_borders):
            self.add = -self.add
            self.lifes -= 1
        if pygame.sprite.spritecollideany(self, all_balls):
            self.kill()


Border(0, 0, width, 0)
Border(0, height, width, height)
Border(0, 0, 0, height)
Border(width, 0, width, height)
skeleton = Hero(load_image("spritesheet.png", -1), 9, 3, 0.5 * width, 0.76 * height)
Back(all_back)
flag_move = 0
flag_shoot = 0
flag_shield = 0
score = 0
way = 0
start_screen()
# Enemy(randint(0, width), randint(0, 0.3 * height))
AnimatedBall(load_image("ball.png", -1), 3, 3, 30, 30, 2)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if flag_joy:
            if event.type == pygame.JOYHATMOTION:
                if event.value in [(-1, 0), (1, 0)]:
                    flag_move = 1
                    way = event.value[0]
                elif event.value == (0, 0):
                    flag_move = 0

            if event.type == pygame.JOYAXISMOTION and not flag_shield:
                if event.axis == 2:
                    if event.value <= -0.97:
                        all_sprites.update("shoot")
                        flag_shoot = 1
                    if event.value >= 0.97:
                        all_sprites.update("shoot")
                        flag_shoot = 2

            if event.type == pygame.JOYBUTTONDOWN:
                if event.button == 0:
                    flag_shield = 1

            if event.type == pygame.JOYBUTTONUP:
                if event.button == 0:
                    flag_shield = 0
                if event.button == 2 and score - 300 >= 0:
                    score -= 300
                    for i in all_balls:
                        i.kill()
                    AnimatedBall(load_image("ball.png", -1), 3, 3, 30, 30, 2)
                    AnimatedBall(load_image("ball.png", -1), 3, 3, 40, 40, 2)
                    AnimatedBall(load_image("ball.png", -1), 3, 3, 50, 50, 2)
        else:
            if event.type == pygame.KEYDOWN:
                if event.key == 32:
                    flag_shield = 1

                if event.key == 97:
                    flag_move = not flag_move
                    way = -1

                if event.key == 100:
                    flag_move = 1
                    way = 1

                if event.key == 304 and score - 300 >= 0:
                    score -= 300
                    for i in all_balls:
                        i.kill()
                    AnimatedBall(load_image("ball.png", -1), 3, 3, 30, 30, 2)
                    AnimatedBall(load_image("ball.png", -1), 3, 3, 40, 40, 2)
                    AnimatedBall(load_image("ball.png", -1), 3, 3, 50, 50, 2)


            if event.type == pygame.KEYUP:
                if event.key == 97:
                    flag_move = 0
                    all_sprites.update("shield_up")

                if event.key == 100:
                    flag_move = 0

                if event.key == 32:
                    flag_shield = 0

            if event.type == pygame.MOUSEBUTTONDOWN and not flag_shield:

                if event.button == 3:
                    all_sprites.update("shoot")
                    flag_shoot = 1

                if event.button == 1:
                    all_sprites.update("shoot")
                    flag_shoot = 2

    if flag_move:
        all_sprites.update(way)
    if flag_shield:
        all_sprites.update()
    if flag_shoot == 1:
        Bullet(xw + 20, y, "r")
        flag_shoot = 0
    elif flag_shoot == 2:
        Bullet(x, y, "l")
        flag_shoot = 0
    all_back.draw(screen)  # не двигать
    print(score)
    all_balls.draw(screen)
    all_balls.update()

    all_sprites.update()
    all_sprites.draw(screen)
    all_bullets.draw(screen)
    all_bullets.update()
    pygame.display.flip()
    clock.tick(FPS)
