import pygame
from pygame.locals import *
from pygame import mixer
import pickle
from os import path

pygame.mixer.pre_init(44100, -16, 2, 512)
mixer.init()
pygame.init()

clock = pygame.time.Clock()
fps = 120


screen_width = 500
screen_height = 500

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('CORONA SURVIVE')

#Fonte
font_score = pygame.font.SysFont('Arial', 30)

#Cor da Fonte
red = (255, 25, 25)


#Variaveis do Jogo
tile_size = 25
game_over = 0
main_menu = True
level = 1
max_levels = 6
score = 0

#Imagem Background
city_image = pygame.image.load('imagens/abandonedcity.jpg')
city_image = pygame.transform.scale(city_image,(500, 500))
restart_img = pygame.image.load('imagens/restart.png')
play_img = pygame.image.load('imagens/play.png')
quit_img = pygame.image.load('imagens/quit.png')

#sons
back_fx = pygame.mixer.Sound('sons/background_sound.wav')
back_fx.set_volume(0.5)
pygame.mixer.music.load('sons/background_sound.wav')
pygame.mixer.music.play(-1, 0.0, 5000)
mask_fx = pygame.mixer.Sound('sons/mask_sound.wav')
mask_fx.set_volume(0.5)
jump_fx = pygame.mixer.Sound('sons/jump_sound.wav')
jump_fx.set_volume(0.5)
game_over_fx = pygame.mixer.Sound('sons/game over_sound.wav')
game_over_fx.set_volume(0.5)

#Cor do Texto do Counter
def draw_text(text, font, text_color, x, y):
    img = font.render(text, True, text_color)
    screen.blit(img, (x, y))



def reset_level(level):
    player.reset(100, screen_height - 130)
    virus_group.empty()
    spike_group.empty()
    mask_group.empty()
    exit_group.empty()

    if path.exists(f'level{level}_data'):
        pickle_in = open(f'level{level}_data', 'rb')
        world_data = pickle.load(pickle_in)
    world = World(world_data)

    return world

class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.clicked = False

    def draw(self):

        action = False

        pos = pygame.mouse.get_pos()

        if self.rect.collidepoint(pos):
             if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                 self.clicked = True
                 action = True

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False


        screen.blit(self.image, self.rect)

        return action


class Player():
    def __init__(self, x, y):
        self.reset(x, y)


    def update(self, game_over):
        kx = 0
        ky = 0
        tempo_passos = 20
        if game_over == 0:
            #controles
            key = pygame.key.get_pressed()
            if key[pygame.K_SPACE] and self.jumped == False and self.in_air == False:
                jump_fx.play()
                self.vel_y = -15
                self.jumped = True
            if key[pygame.K_SPACE] == False:
                self.jumped = False
            if key[pygame.K_LEFT]:
                kx -= 1
                self.counter += 1
                self.direction = -1
            if key[pygame.K_RIGHT]:
                kx += 1
                self.counter += 1
                self.direction = 1
            if key[pygame.K_LEFT] == False and key[pygame.K_RIGHT] == False:
                self. counter = 0
                self.index = 0
                if self.direction == 1:
                    self.image = self.images_right[self.index]
                if self.direction == -1:
                    self.image = self.images_left[self.index]


            #animação
            if self.counter > tempo_passos:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images_right):
                    self.index = 0
                if self.direction == 1:
                    self.image = self.images_right[self.index]
                if self.direction == -1:
                    self.image = self.images_left[self.index]



            #gravidade

            self.vel_y += 1
            if self.vel_y > 5:
                self.vel_y = 3
            ky += self.vel_y

            #colisão em objetos

            self.in_air = True


            for tile in world.tile_list:
                if tile[1].colliderect(self.rect.x + kx, self.rect.y , self.width, self.height):
                    kx = 0
                if tile[1].colliderect(self.rect.x, self.rect.y + ky, self.width, self.height):
                    if self.vel_y < 0:
                        ky = tile[1].bottom - self.rect.top
                        self.vel_y = 0
                    elif self.vel_y >= 0:
                        ky = tile[1].top - self.rect.bottom
                        self.vel_y = 0
                        self.in_air = False


            #colisão nos monstros
            if pygame.sprite.spritecollide(self, virus_group, False):
                game_over = -1
                game_over_fx.play()

            if pygame.sprite.spritecollide(self, spike_group, False):
                game_over = -1
                game_over_fx.play()

            if pygame.sprite.spritecollide(self, exit_group, False):
                game_over = 1


            #coordenadas

            self.rect.x += kx
            self.rect.y += ky


        elif game_over == -1:
            self.image =self.dead_image
            if self.rect.y > 50:
                self.rect.y -= 5


        screen.blit(self.image, self.rect)


        return game_over


    def reset(self, x, y):
        self.images_right = []
        self.images_left = []
        self.index = 0
        self.counter = 0
        for num in range(1, 9):
            img_right = pygame.image.load(f'imagens/Margery{num}.png')
            img_right = pygame.transform.scale(img_right, (30, 40))
            img_left = pygame.transform.flip(img_right, True, False)
            self.images_right.append(img_right)
            self.images_left.append(img_left)
        self.dead_image = pygame.image.load('imagens/ghost.png')
        self.image = self.images_right[self.index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.vel_y = 0
        self.jumped = False
        self.direction = 0
        self.in_air = True

class World():
    def __init__(self, data):
        self.tile_list = []
        #imagens do jogo
        box_alt = pygame.image.load('imagens/boxAlt.png')
        box_item = pygame.image.load('imagens/boxItem.png')
        row_count = 0
        for row in data:
            col_count = 0
            for tile in row:
                if tile == 1:
                    img = pygame.transform.scale(box_alt, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 2:
                    img = pygame.transform.scale(box_item, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 3:
                    virus = Monster(col_count * tile_size, row_count * tile_size + -5)
                    virus_group.add(virus)
                if tile == 6:
                    spike = Spikes(col_count * tile_size, row_count * tile_size + (tile_size // 2))
                    spike_group.add(spike)
                if tile == 7:
                    mask = Mask(col_count * tile_size + (tile_size // 2), row_count * tile_size + (tile_size // 2))
                    mask_group.add(mask)
                if tile == 8:
                    exit = Exit(col_count * tile_size, row_count * tile_size - (tile_size // 2))
                    exit_group.add(exit)
                col_count += 1
            row_count += 1

    def draw(self):
        for tile in self.tile_list:
            screen.blit(tile[0], tile[1])



class Monster(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('imagens/monsters.png')
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_direction = 1
        self.move_counter = 0

    def update(self):
        self.rect.x += self.move_direction
        self.move_counter += -1
        if abs(self.move_counter) > 30:
            self.move_direction *= -1
            self.move_counter *= -1


class Spikes(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('imagens/spikes.png')
        self.image = pygame.transform.scale(img, (tile_size, tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Mask(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('imagens/mask.png')
        self.image = pygame.transform.scale(img, (tile_size, tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)



class Exit(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('imagens/exit.png')
        self.image = pygame.transform.scale(img, (tile_size, int(tile_size * 1.5)))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y



player = Player(100, screen_height - 130)

virus_group = pygame.sprite.Group()
spike_group = pygame.sprite.Group()
mask_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()


if path.exists(f'level{level}_data'):
    pickle_in = open(f'level{level}_data', 'rb')
    world_data = pickle.load(pickle_in)
world = World(world_data)


restart_button = Button(screen_width // 2 - 100, screen_height // 2 + 25, restart_img)

play_button = Button(screen_width // 2 - 250, screen_height // 2, play_img)

quit_button = Button(screen_width // 2 + 25, screen_height // 2, quit_img)


run = True
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
    clock.tick(fps)

    screen.blit(city_image,(0,0))

    if main_menu == True:
        if quit_button.draw():
            run = False
        if play_button.draw():
            main_menu = False
    else:
        world.draw()

        if game_over == 0:
            virus_group.update()
            # adicionando pontos com as masks
            if pygame.sprite.spritecollide(player, mask_group, True):
                score += 1
                mask_fx.play()
            draw_text('M:' + str(score), font_score, red, tile_size - 1, 20)

        virus_group.draw(screen)
        spike_group.draw(screen)
        mask_group.draw(screen)
        exit_group.draw(screen)

        game_over = player.update(game_over)

        # Se o personagem morrer
        if game_over == -1:
            if restart_button.draw():
                world_data = []
                world = reset_level(level)
                player.reset(100, screen_height - 130)
                game_over = 0
                score = 0


        #Se o personagem passar de fase
        if game_over == 1:
            level += 1
            if level <= max_levels:
                world_data = []
                world = reset_level(level)
                game_over = 0
            else:
                if restart_button.draw():
                    level = 1
                    world_data = []
                    world = reset_level(level)
                    game_over = 0
                    score = 0


    pygame.display.update()

pygame.quit()



