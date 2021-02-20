import pygame
import random
from os import path
import sys

WIDTH = 800
HEIGHT = 600
FPS = 50
powerup_time = 6000

pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Galaga')
clock = pygame.time.Clock()
font_name = pygame.font.match_font('times')

# define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)


def text(s, txt, size, x, y):
 font = pygame.font.Font(font_name, size)
 text_surface = font.render(txt, True, WHITE)
 text_rect = text_surface.get_rect()
 text_rect.midtop = (x, y)
 s.blit(text_surface, text_rect)

def ship1():
  s = Ship()
  ships.add(s)
  all_sprites.add(s)


def newMob():
  m = Mob()
  mobs.add(m)
  all_sprites.add(m)


def shield_powerup(surf, x, y, pct):
  if pct < 0:
      pct = 0

  bar_length = 100
  bar_height = 10
  fill = (pct / 100) * bar_length
  outline_rect = pygame.Rect(x, y, bar_length, bar_height)
  fill_rect = pygame.Rect(x, y, fill, bar_height)
  pygame.draw.rect(surf, GREEN, fill_rect)
  pygame.draw.rect(surf, WHITE, outline_rect, 2)

  if 20 < pct < 50:
      pygame.draw.rect(surf, YELLOW, fill_rect)
  elif pct < 20:
      pygame.draw.rect(surf, RED, fill_rect)


def draw_lives(surf, x, y, lives, img):
  for i in range(lives):
      img_rect = img.get_rect()
      img_rect.x = x + 30 * i
      img_rect.y = y
      surf.blit(img, img_rect)


class Player(pygame.sprite.Sprite):
  def __init__(self):
      pygame.sprite.Sprite.__init__(self)
      self.image = pygame.transform.scale(player_img, (60, 46))
      self.image.set_colorkey(BLACK)
      self.rect = self.image.get_rect()
      self.radius = 20
      self.rect.centerx = WIDTH / 2
      self.rect.bottom = HEIGHT - 10
      self.speedx = 0
      self.shield = 100
      self.shoot_delay = 250
      self.last_shot = pygame.time.get_ticks()
      self.lives = 3
      self.hidden = False
      self.hide_timer = pygame.time.get_ticks()
      self.power = 1
      self.power_time = pygame.time.get_ticks()

  def update(self):
      # time out for powerups
      if self.power >= 2 and pygame.time.get_ticks() - self.power_time > powerup_time:
          self.power -= 1
          self.power_time = pygame.time.get_ticks()

      # unhide if hidden
      if self.hidden and pygame.time.get_ticks() - self.hide_timer > 1000:
          self.hidden = False
          self.rect.centerx = WIDTH / 2
          self.rect.bottom = HEIGHT - 10

      self.speedx = 0
      keystate = pygame.key.get_pressed()
      if keystate[pygame.K_LEFT]:
          self.speedx = -5
      if keystate[pygame.K_RIGHT]:
          self.speedx = 5
      if keystate[pygame.K_SPACE] and not self.hidden:
          self.shoot()
      self.rect.x += self.speedx
      if self.rect.right > WIDTH:
          self.rect.right = WIDTH
      if self.rect.left < 0:
          self.rect.left = 0

  def powerup(self):
      self.power += 1
      self.power_time = pygame.time.get_ticks()

  def shoot(self):
      now = pygame.time.get_ticks()
      if now - self.last_shot > self.shoot_delay:
          self.last_shot = now
          if self.power == 1:
              bullet = Bullet(self.rect.centerx, self.rect.top)
              all_sprites.add(bullet)
              bullets.add(bullet)
              shoot_sound.play()

          if self.power >= 2:
              bullet1 = Bullet(self.rect.left, self.rect.centery)
              bullet2 = Bullet(self.rect.right, self.rect.centery)
              all_sprites.add(bullet1)
              all_sprites.add(bullet2)
              bullets.add(bullet1)
              bullets.add(bullet2)
              shoot_sound.play()

  def hide(self):
      # hide the player temporary
      self.hidden = True
      self.hide_timer = pygame.time.get_ticks()
      self.rect.center = (WIDTH / 2, HEIGHT + 200)


class Mob(pygame.sprite.Sprite):
  def __init__(self):
      pygame.sprite.Sprite.__init__(self)
      self.image_orig = random.choice(meteor_images)
      self.image_orig.set_colorkey(BLACK)
      self.image = self.image_orig.copy()
      self.rect = self.image.get_rect()
      self.radius = int(self.rect.width * .85 / 2)
      self.rect.x = random.randrange(WIDTH - self.rect.width)
      self.rect.y = random.randrange(-150, -100)
      self.speedy = random.randrange(1, 8)
      self.speedx = random.randrange(-3, 3)
      self.rot = 0
      self.rot_speed = random.randrange(-8, 8)
      self.last_update = pygame.time.get_ticks()

  def rotate(self):
      now = pygame.time.get_ticks()
      if now - self.last_update > 50:
          self.last_update = now
          self.rot = (self.rot + self.rot_speed) % 360
          new_image = pygame.transform.rotate(self.image_orig, self.rot)
          old_center = self.rect.center
          self.image = new_image
          self.rect = self.image.get_rect()
          self.rect.center = old_center

  def update(self):
      self.rotate()
      self.rect.x += self.speedx
      self.rect.y += self.speedy
      if self.rect.top > HEIGHT + 10 or self.rect.left < -25 or self.rect.right > WIDTH + 20:
          self.rect.x = random.randrange(WIDTH - self.rect.width)
          self.rect.y = random.randrange(-100, -40)
          self.speedy = random.randrange(1, 8)


class Ship(pygame.sprite.Sprite):
  def __init__(self):
      pygame.sprite.Sprite.__init__(self)
      self.image_orig = pygame.transform.scale(ship_img, (60, 50))
      self.image_orig.set_colorkey(BLACK)
      self.image = self.image_orig.copy()
      self.rect = self.image.get_rect()
      self.radius = int(self.rect.width * .85 / 2)
      self.rect.x = random.randrange(WIDTH - self.rect.width)
      self.rect.y = random.randrange(-150, -100)
      self.speedy = random.randrange(1, 8)
      self.speedx = random.randrange(-3, 3)
      self.last_update = pygame.time.get_ticks()

  def update(self):
      self.rect.x += self.speedx
      self.rect.y += self.speedy
      if self.rect.top > HEIGHT + 10 or self.rect.left < -25 or self.rect.right > WIDTH + 20:
          self.rect.x = random.randrange(WIDTH - self.rect.width)
          self.rect.y = random.randrange(-100, -40)
          self.speedy = random.randrange(1, 8)

  def shoot(self):
      now = pygame.time.get_ticks()
      if now - self.last_update > 50:
          self.last_update = now
          bullet = Bullet2(self.rect.centerx, self.rect.bottom)
          all_sprites.add(bullet)
          bullets.add(bullet)
          shoot_sound.play()


class Bullet2(pygame.sprite.Sprite):
  def __init__(self, x, y):
      pygame.sprite.Sprite.__init__(self)
      self.image = bullet_img
      self.image.set_colorkey(BLACK)
      self.rect = self.image.get_rect()
      self.rect.bottom = y
      self.rect.centerx = x
      self.speedy = -10

  def update(self):
      self.rect.y += self.speedy
      # kill if it moves off the top of the screen
      if self.rect.top < 0:
          self.kill()


class Bullet(pygame.sprite.Sprite):
  def __init__(self, x, y):
      pygame.sprite.Sprite.__init__(self)
      self.image = bullet_img
      self.image.set_colorkey(BLACK)
      self.rect = self.image.get_rect()
      self.rect.bottom = y
      self.rect.centerx = x
      self.speedy = -10

  def update(self):
      self.rect.y += self.speedy
      # kill if it moves off the top of the screen
      if self.rect.bottom < 0:
          self.kill()


class Pow(pygame.sprite.Sprite):
  def __init__(self, center):
      pygame.sprite.Sprite.__init__(self)
      self.type = random.choice(['shield', 'gun', 'extra life'])
      self.image = powerup_images[self.type]
      self.image.set_colorkey(BLACK)
      self.rect = self.image.get_rect()
      self.rect.center = center
      self.speedy = 5

  def update(self):
      self.rect.y += self.speedy
      # kill if it moves off the top of the screen
      if self.rect.top > HEIGHT:
          self.kill()


class Explosion(pygame.sprite.Sprite):
  def __init__(self, center, size):
      pygame.sprite.Sprite.__init__(self)
      self.size = size
      self.image = explosion_anim[self.size][0]
      self.rect = self.image.get_rect()
      self.rect.center = center
      self.frame = 0
      self.last_update = pygame.time.get_ticks()
      self.frame_rate = 70

  def update(self):
      now = pygame.time.get_ticks()
      if now - self.last_update > self.frame_rate:
          self.last_update = now
          self.frame += 1
          if self.frame == len(explosion_anim[self.size]):
              self.kill()
          else:
              center = self.rect.center
              self.image = explosion_anim[self.size][self.frame]
              self.rect = self.image.get_rect()
              self.rect.center = center


def show_go_screen():
  screen.blit(background, background_rect)
  text(screen, 'Galaga', 65, WIDTH / 2, HEIGHT / 4)
  text(screen, 'Use arrow keys to move and Space Bar to shoot.', 30, WIDTH / 2, HEIGHT / 2)
  text(screen, 'Press Space to Being your Adventure!', 24, WIDTH / 2, HEIGHT * 2.5 / 4)
  pygame.display.flip()
  waiting = True
  while waiting:
      clock.tick(FPS)
      for event in pygame.event.get():
          if event.type == pygame.QUIT:
              pygame.quit()
          if event.type == pygame.KEYUP:
              waiting = False

background = pygame.image.load('space_background.png')
background_rect = background.get_rect()
player_img = pygame.image.load('ship1.png')
player_mini_img = pygame.transform.scale(player_img, (25, 19))
player_mini_img.set_colorkey(BLACK)
bullet_img = pygame.image.load( 'laserRed16.png')
meteor_images = []
meteor_list = [ 'meteorBrown_med1.png',
             'meteorBrown_med1.png', 'meteorBrown_small1.png', 'meteorBrown_small2.png',]
for img in meteor_list:
  meteor_images.append(pygame.image.load( img))

ship_img = pygame.image.load('enemyBlue1.png')
ship_mini_img = pygame.transform.scale(ship_img, (60, 50))


explosion_anim = {}
explosion_anim['lg'] = []
explosion_anim['sm'] = []
explosion_anim['player'] = []
for i in range(11):
  filename = 'explosion{}.png'.format(i)
  img = pygame.image.load(filename)
  img.set_colorkey(BLACK)
  img_lg = pygame.transform.scale(img, (75, 75))
  explosion_anim['lg'].append(img_lg)
  img_sm = pygame.transform.scale(img, (32, 32))
  explosion_anim['sm'].append(img_sm)

for i in range(2):
  filename = 'playerShip1_damage{}.png'.format(i)
  img = pygame.image.load( filename)
  img.set_colorkey(BLACK)
  explosion_anim['player'].append(img)

powerup_images = {}
powerup_images['shield'] = pygame.image.load('protect.png')
powerup_images['shield'] = pygame.transform.scale(powerup_images['shield'], (75,75))

powerup_images['gun'] = pygame.image.load('lasergun.png')
powerup_images['gun'] = pygame.transform.scale(powerup_images['gun'], (75,75))
powerup_images['extra life'] = pygame.image.load('extralife.png')
powerup_images['extra life'] = pygame.transform.scale(powerup_images['extra life'], (50,50))

# load all game sounds
shoot_sound = pygame.mixer.Sound('Laser Shot.wav')
shield_sound = pygame.mixer.Sound('bell_01.ogg')
power_sound = pygame.mixer.Sound('bell_02.ogg')
life_sound = pygame.mixer.Sound('24.wav')

expl_sounds = []
for snd in ['explosion01.wav', 'explosion.wav']:
  expl_sounds.append(pygame.mixer.Sound(path.join(snd)))

player_die_sound = pygame.mixer.Sound('death.wav')


all_sprites = pygame.sprite.Group()
mobs = pygame.sprite.Group()
bullets = pygame.sprite.Group()
ships = pygame.sprite.Group()
powerups = pygame.sprite.Group()
player = Player()
all_sprites.add(player)

for i in range(8):
  newMob()
  ship1()
score = 0


# Game Loop
game_over = True
running = True

while running:
  if game_over:
      show_go_screen()
      game_over = False
      all_sprites = pygame.sprite.Group()
      mobs = pygame.sprite.Group()
      ships = pygame.sprite.Group()
      bullets = pygame.sprite.Group()
      powerups = pygame.sprite.Group()
      player = Player()
      all_sprites.add(player)
      for i in range(8):
          newMob()
          ship1()
      score = 0


  clock.tick(FPS)

  for event in pygame.event.get():

      if event.type == pygame.QUIT:
          running = False

  # Update
  all_sprites.update()

  # collision event for mobs and bullets
  hits = pygame.sprite.groupcollide(mobs, bullets, True, True)
  for hit in hits:
      score += 50 - hit.radius
      random.choice(expl_sounds).play()
      expl = Explosion(hit.rect.center, 'lg')
      all_sprites.add(expl)
      if random.random() > 0.95:
          pow = Pow(hit.rect.center)
          all_sprites.add(pow)
          powerups.add(pow)
      newMob()

  hits = pygame.sprite.groupcollide(ships, bullets, True, True)
  for hit in hits:
      score += 50 - hit.radius
      random.choice(expl_sounds).play()
      expl = Explosion(hit.rect.center, 'lg')
      all_sprites.add(expl)
      if random.random() > 0.95:
          pow = Pow(hit.rect.center)
          all_sprites.add(pow)
          powerups.add(pow)
      ship1()

  # collision event for player and mobs
  hits = pygame.sprite.spritecollide(player, mobs, True, pygame.sprite.collide_circle)
  for hit in hits:
      player.shield -= hit.radius * 2
      newMob()
      if player.shield <= 0:
          random.choice(expl_sounds).stop()
          player_die_sound.play()
          death_explosion = Explosion(player.rect.center, 'player')
          all_sprites.add(death_explosion)
          player.hide()
          player.lives -= 1
          player.shield = 100

  hits = pygame.sprite.spritecollide(player, ships, True, pygame.sprite.collide_circle)
  for hit in hits:
      player.shield -= hit.radius * 4
      ship1()
      if player.shield <= 0:
          random.choice(expl_sounds).stop()
          player_die_sound.play()
          death_explosion = Explosion(player.rect.center, 'player')
          all_sprites.add(death_explosion)
          player.hide()
          player.lives -= 1
          player.shield = 100

  hits = pygame.sprite.spritecollide(player, powerups, True)
  for hit in hits:
      if hit.type == 'shield':
          random.choice(expl_sounds).stop()
          player.shield += random.randrange(10, 30)
          shield_sound.play()
          if player.shield >= 100:
              player.shield = 100

      if hit.type == 'gun':
          random.choice(expl_sounds).stop()
          power_sound.play()
          player.powerup()

      if hit.type == 'extra life':
          random.choice(expl_sounds).stop()
          life_sound.play()
          player.lives += 1
          if player.lives >= 5:
              player.lives = 5

  # if player dies and explosion is finished
  if player.lives == 0 and not death_explosion.alive():
      player.shield = 0
      import pygame


      game_over = True

  screen.fill(BLACK)
  screen.blit(background, background_rect)
  all_sprites.draw(screen)
  text(screen, str(score), 24, WIDTH / 2, 10)
  shield_powerup(screen, 5, 5, player.shield)
  draw_lives(screen, WIDTH - 150, 5, player.lives, player_mini_img)


  pygame.display.flip()

pygame.quit()
sys.exit()
