import pygame
import random
import sys

# Inicializa o Pygame
pygame.init()

# Configurações da tela
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space Invaders")

# Cores
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# FPS
clock = pygame.time.Clock()
FPS = 60

# Classe do Jogador
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((50, 30))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT - 10
        self.speed = 5

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < SCREEN_WIDTH:
            self.rect.x += self.speed

    def shoot(self):
        bullet = Bullet(self.rect.centerx, self.rect.top)
        all_sprites.add(bullet)
        bullets.add(bullet)

# Classe do Inimigo
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((40, 40))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = 1

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT:
            self.rect.x = random.randint(0, SCREEN_WIDTH - self.rect.width)
            self.rect.y = random.randint(-100, -40)

# Classe do Tiro
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((5, 10))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed = -10

    def update(self):
        self.rect.y += self.speed
        # Remove o tiro quando ele sai da tela
        if self.rect.bottom < 0:
            self.kill()

# Cria grupos de sprites
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
bullets = pygame.sprite.Group()

# Cria o jogador
player = Player()
all_sprites.add(player)

# Cria inimigos
for i in range(8):
    enemy = Enemy(random.randint(0, SCREEN_WIDTH - 40), random.randint(-100, -40))
    all_sprites.add(enemy)
    enemies.add(enemy)

# Fonte para texto
font = pygame.font.SysFont(None, 36)

# Pontuação
score = 0

# Loop principal do jogo
running = True
while running:
    clock.tick(FPS)
    
    # Processa eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.shoot()
    
    # Atualiza sprites
    all_sprites.update()
    
    # Verifica colisão entre tiros e inimigos
    hits = pygame.sprite.groupcollide(bullets, enemies, True, True)
    for hit in hits:
        score += 10
        enemy = Enemy(random.randint(0, SCREEN_WIDTH - 40), random.randint(-100, -40))
        all_sprites.add(enemy)
        enemies.add(enemy)
    
    # Verifica colisão entre jogador e inimigos
    hits = pygame.sprite.spritecollide(player, enemies, False)
    if hits:
        running = False
    
    # Desenha tudo
    screen.fill(BLACK)
    all_sprites.draw(screen)
    
    # Desenha pontuação
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))
    
    # Atualiza a tela
    pygame.display.flip()

# Encerra o Pygame
pygame.quit()
sys.exit()