import pygame
import os
import sys
from random import randint
from random import choice

# инициализация
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

FPS = 60
size = width, height = 900, 600
screen = pygame.display.set_mode(size)
pygame.display.set_caption("KillBall")
running = True
clock = pygame.time.Clock()
screen.fill((255, 255, 255))

pygame.mixer.music.load(os.path.join('data', 'fight.ogg'))
pygame.mixer.music.set_volume(0.6)
pygame.mixer.music.play(-1)

shield_sound = pygame.mixer.Sound(os.path.join('data', 'magicshield.ogg'))
kill_balls_sound = pygame.mixer.Sound(os.path.join('data', 'heal.ogg'))

font_name = os.path.join('data', 'font.ttf')
font = pygame.font.Font(font_name, 20)
t_x = 0.2 * width
t_y1 = 0.2 * height
t_y2 = 0.3 * height


def terminate():
    # выход из начального окна

    pygame.quit()
    sys.exit()


def draw_text(sc, balls):
    # рисует текст с информацией о счете и количестве шаров, которое призовется после использоваиния способности

    text1 = font.render(f"Current score: {sc}", 1, (0, 255, 255))
    text2 = font.render(f"Next kill will summon: {balls}", 1, (0, 255, 255))
    screen.blit(text1, (t_x, t_y1))
    screen.blit(text2, (t_x, t_y2))


def start_screen(end=False):
    # При end=False риисует начальный экран, иначе - конечный

    if not end:
        fon = pygame.transform.scale(load_image('fon.png'), (width, height))
        screen.blit(fon, (0, 0))
    else:
        global score

        pygame.mixer.music.load(os.path.join('data', 'gameover.ogg'))
        pygame.mixer.music.play(-1)
        cur_score = open("score.txt", "r")
        current = cur_score.read()
        cur_score.close()
        if int(current) < score:
            current = score
        cur_score = open("score.txt", "w")
        cur_score.write(str(current))
        cur_score.close()
        text = font.render(f"Your score: {score}", 1, (100, 255, 100))
        text1 = font.render(f"Best score: {current}", 1, (100, 255, 100))
        if flag_joy:
            fon = pygame.transform.scale(load_image('gameover.jpg'), (width, height))
        else:
            fon = pygame.transform.scale(load_image('gameover11.jpg'), (width, height))
        screen.blit(fon, (0, 0))
        screen.blit(text, (width * 0.1, height * 0.9))
        screen.blit(text1, (width * 0.6, height * 0.9))
    cn = 0
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif flag_joy and event.type in [pygame.JOYAXISMOTION, pygame.JOYHATMOTION, pygame.JOYBUTTONDOWN,
                                             pygame.JOYBALLMOTION] and not end:
                if cn < 4:
                    cn += 1
                    fon = pygame.transform.scale(load_image('xbox.jpg'), (width, height))
                    screen.blit(fon, (0, 0))
                    pygame.display.flip()
                else:
                    return  # начинаем игру
            elif event.type in [pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN] and not flag_joy and not end:
                if cn < 1:
                    cn += 1
                    fon = pygame.transform.scale(load_image('pc_how.jpg'), (width, height))
                    screen.blit(fon, (0, 0))
                    pygame.display.flip()
                else:
                    return  # начинаем игру
            elif end:
                if event.type == pygame.KEYDOWN and not flag_joy:
                    if event.key == 102:
                        return
                elif flag_joy and event.type == pygame.JOYBUTTONDOWN:
                    if event.button == 7:
                        return
        pygame.display.flip()
        clock.tick(FPS)


def load_image(name, colorkey=None):
    # загружает изображения

    fullname = os.path.join('data', name)
    image = pygame.image.load(fullname).convert()
    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


# инициализация стен (горизонтальные и вертикальные ограничения)

horizontal_borders = pygame.sprite.Group()
vertical_borders = pygame.sprite.Group()

# инициализация групп спрайтов

all_bullets = pygame.sprite.Group()  # выстрелы
all_back = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()  # герой
all_borders = pygame.sprite.Group()
all_balls = pygame.sprite.Group()

# положение героя
x, xw, y = 0, 0, 0


class Border(pygame.sprite.Sprite):
    # стены

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
    # Задний план игры, выбирается случайно

    image = load_image("cyberpunk_back.png")
    image = pygame.transform.scale(image, (width, height))
    image1 = load_image("industrial_back.jpg")
    image1 = pygame.transform.scale(image1, (width, height))
    image2 = load_image("forest_back.png")
    image2 = pygame.transform.scale(image2, (width, height))
    image3 = load_image("hill_back.jpg")
    image3 = pygame.transform.scale(image3, (width, height))
    image = choice([image, image1, image2, image3])

    def __init__(self, group):
        # НЕОБХОДИМО вызвать конструктор родительского класса Sprite
        super().__init__(group)
        self.image = Back.image
        self.rect = self.image.get_rect()
        self.rect.x = 0
        self.rect.y = 0


class Hero(pygame.sprite.Sprite):
    # главный класс героя

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
        # герой анимирован, поэтому используется функция для разрезания sprite sheet

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
        global x, xw, y, flag_shield, flag_dead
        self.left = self.frames[:9]
        self.right = self.frames[18:27]
        self.counter += 1
        if pygame.sprite.spritecollideany(self, all_balls) and not flag_shield:
            # пересечение с вражеским шаром, щит не активирован, герой погибает

            flag_dead = True
            if self.counter % 2 == 0:
                # регулирует скорость анимации

                self.cur_frame = (self.cur_frame + 1) % len(self.dead)
                self.image = pygame.transform.scale(self.dead[self.cur_frame], (150, 150))
                self.flag_end += 1
                if self.flag_end == 4:
                    self.kill()
        elif flag_shield:
            # щит активирован

            self.image = load_image("shield.png", -1)
            self.image = pygame.transform.scale(self.image, (150, 150))
            flag_shield = True
        elif way and not flag_shield:
            # передана особенность движения

            if way == "shoot":
                # выстрел

                self.image = load_image("shoot.png", -1)
                self.image = pygame.transform.scale(self.image, (150, 150))
                x, xw, y = self.rect.x, self.rect.x + self.rect.w, self.rect.y
            elif not flag_shield:
                # щит не активирован

                if not pygame.sprite.spritecollideany(self, vertical_borders):
                    # не заходит за стены, щит не активирован

                    if way > 0:
                        # вправо

                        self.cur_frame = (self.cur_frame + 1) % len(self.right)
                        self.image = pygame.transform.scale(self.right[self.cur_frame], (150, 150))
                        self.rect.x += way * 10
                    elif way < 0:
                        # влево

                        self.cur_frame = (self.cur_frame + 1) % len(self.left)
                        self.image = pygame.transform.scale(self.left[self.cur_frame], (150, 150))
                        self.rect.x += way * 10
                    if self.counter % 30 == 0:
                        self.counter = 0
                else:
                    # отталкивание от стен

                    if self.rect.x + self.rect.w <= width:
                        self.rect.x += 1
                    elif self.rect.x - self.rect.w >= 0:
                        self.rect.x -= 1


class AnimatedBall(pygame.sprite.Sprite):
    # Вражеский шар

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
        self.vx = randint(-8, 8)
        self.vy = randint(-8, 8)

    def cut_sheet(self, sheet, columns, rows):
        # Разрез sprite sheet

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
            # Регуляция частоты обновления

            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
            self.image = pygame.transform.scale(self.frames[self.cur_frame], (80, 80))

            self.counter = 0
        self.rect = self.rect.move(self.vx, self.vy)
        if pygame.sprite.spritecollideany(self, all_sprites) and flag_shield:
            # Пересечние с героем, щит активирован

            shield_sound.play()
            self.rect.y -= 5
            self.rect.x += 5
            self.vy = -self.vy - 1
            self.vx = -self.vx - 1
        if pygame.sprite.spritecollideany(self, horizontal_borders):
            # Столкновение с горизонтальными стенами

            self.vy = -self.vy
        if pygame.sprite.spritecollideany(self, vertical_borders):
            # Столкновение с вертикальными стенами

            self.vx = -self.vx
        if pygame.sprite.spritecollideany(self, all_bullets):
            # Столкновение с пулями героя (шарами)

            self.lifes -= 1
            if self.lifes == 0:
                # При смерти появляется два новых шара

                AnimatedBall(load_image("ball.png", -1), 3, 3, self.rect.x - 10, self.rect.y, 2)
                AnimatedBall(load_image("ball.png", -1), 3, 3, self.rect.x + 10, self.rect.y, 2)
                score += 100
                self.kill()
        self.counter += 1


class Bullet(pygame.sprite.Sprite):
    # Снаряды главного героя (магические шарики)

    def __init__(self, x, y, type):
        super().__init__(all_bullets)
        # Существует два типа пуль: правые и левые. В зависимости от типа, меняется вид, движение и начальные координаты

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


# инициализация флагов и счетчиков

flag_move = 0
flag_shoot = 0
flag_shield = 0
score = 0
way = 0
counter = 0
flag_dead = 0
end = 0

# Инициализация начальных героев, врагов и окружения

Border(0, 0, width, 0)
Border(0, height, width, height)
Border(0, 0, 0, height)
Border(width, 0, width, height)
skeleton = Hero(load_image("spritesheet.png", -1), 9, 3, 0.5 * width, 0.76 * height)
Back(all_back)

start_screen()
AnimatedBall(load_image("ball.png", -1), 3, 3, 30, 30, 2)

while running:
    if not flag_dead:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if flag_joy:
                # Если подключен джойстик, меняется управление

                if event.type == pygame.JOYHATMOTION:
                    # Движение

                    if event.value in [(-1, 0), (1, 0)]:
                        flag_move = 1
                        way = event.value[0]
                    elif event.value == (0, 0):
                        # Остановка

                        flag_move = 0

                if event.type == pygame.JOYAXISMOTION and not flag_shield:
                    # Выстрел из левого или правого курка

                    if event.axis == 2:
                        if event.value <= -0.97:
                            all_sprites.update("shoot")
                            flag_shoot = 1
                        if event.value >= 0.97:
                            all_sprites.update("shoot")
                            flag_shoot = 2

                if event.type == pygame.JOYBUTTONDOWN:
                    # Поднять щит

                    if event.button == 0:
                        flag_shield = 1

                if event.type == pygame.JOYBUTTONUP:
                    if event.button == 0:
                        # Опустить щит

                        flag_shield = 0
                        for i in all_sprites:
                            i.image = load_image("shoot.png", -1)
                            i.image = pygame.transform.scale(i.image, (150, 150))
                    if event.button == 2 and score - 300 >= 0:
                        # Использовать способность

                        kill_balls_sound.play()
                        score -= 300
                        for i in all_balls:
                            i.kill()
                        counter += 1
                        for j in range(counter):
                            AnimatedBall(load_image("ball.png", -1), 3, 3, 30 + j, 30 + j, 2)
                        counter += 1
                        flag_counter_changed = 1
            else:
                # Управление на клавиатуре

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
                        kill_balls_sound.play()
                        score -= 300
                        for i in all_balls:
                            i.kill()
                        counter += 1
                        for j in range(counter):
                            AnimatedBall(load_image("ball.png", -1), 3, 3, 30 + j, 30 + j, 2)
                        counter += 1
                        flag_counter_changed = 1

                if event.type == pygame.KEYUP:
                    if event.key == 97:
                        flag_move = 0

                    if event.key == 100:
                        flag_move = 0

                    if event.key == 32:
                        flag_shield = 0
                        for i in all_sprites:
                            i.image = load_image("shoot.png", -1)
                            i.image = pygame.transform.scale(i.image, (150, 150))

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
        # Отрисовка спрайтов

        all_back.draw(screen)
        all_balls.draw(screen)
        all_balls.update()
        draw_text(score, counter)
        all_sprites.update()
        all_sprites.draw(screen)
        all_bullets.draw(screen)
        all_bullets.update()

        pygame.display.flip()
        clock.tick(FPS)
    elif flag_dead == 1:
        running = False

# Конец игры, вызов финального экрана

start_screen(True)
