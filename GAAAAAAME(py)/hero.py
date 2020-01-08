class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.image = player_image
        self.rect = self.image.get_rect().move(tile_width * pos_x + 15, tile_height * pos_y + 5)

    def update(self, a=False):
        if a:
            if a == "up":
                self.rect.y -= 10
            elif a == "down":
                self.rect.y += 10
            elif a == "right":
                self.rect.x += 10
            else:
                self.rect.x -= 10