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
    pygame.quit()
    sys.exit()


def draw_text(sc, balls):
    text1 = font.render(f"Current score: {sc}", 1, (100, 255, 100))
    text2 = font.render(f"Next kill will summon: {balls}", 1, (100, 255, 100))
    screen.blit(text1, (t_x, t_y1))
    screen.blit(text2, (t_x, t_y2))


def start_screen(end=False):
    font_name = os.path.join('data', 'font.ttf')
    font = pygame.font.Font(font_name, 30)
    if not end:
        text = font.render("Press any key to continue -->", 1, (0, 0, 0))
        fon = pygame.transform.scale(load_image('fon.png'), (width, height))
        screen.blit(fon, (0, 0))
        screen.blit(text, (width // 2, height // 2))
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
        fon = pygame.transform.scale(load_image('gameover.jpg'), (width, height))
        screen.blit(fon, (0, 0))
        screen.blit(text, (width * 0.1, height // 2))
        screen.blit(text1, (width * 0.6, height // 2))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif flag_joy and event.type in [pygame.JOYAXISMOTION, pygame.JOYHATMOTION, pygame.JOYBUTTONDOWN,
                                             pygame.JOYBALLMOTION] and not end:
                return  # начинаем игру
            elif event.type == pygame.KEYDOWN and not flag_joy and not end:
                return
            elif end:
                if event.type == pygame.MOUSEBUTTONDOWN and not flag_joy:
                    return
                elif flag_joy and event.type == pygame.JOYBUTTONDOWN:
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
    image = load_image("cyberpunk_back.png")
    image = pygame.transform.scale(image, (width, height))
    image1 = load_image("industrial_back.jpg")
    image1 = pygame.transform.scale(image1, (width, height))
    image2 = load_image("forest_back.png")
    image2 = pygame.transform.scale(image2, (width, height))
    image = choice([image, image1, image2])

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
        global x, xw, y, flag_shield, flag_dead
        self.left = self.frames[:9]
        self.right = self.frames[18:27]
        self.counter += 1
        if pygame.sprite.spritecollideany(self, all_balls) and not flag_shield:
            flag_dead = True
            if self.counter % 2 == 0:
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
            shield_sound.play()
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
counter = 0
flag_dead = 0
end = 0

while running:
    if not flag_dead:
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

start_screen(end=True)
