import pygame
import random

from main import main

# Инициализация pygame
pygame.init()

# Импорт спрайтов
BACKGROUND_SHEET = pygame.image.load('sprites/SpaceShooterAssetPack_BackGrounds.png')
BACKGROUND_IU = pygame.image.load('sprites/SpaceShooterAssetPack_IU.png')
BACKGROUND_MISC = pygame.image.load('sprites/SpaceShooterAssetPack_Miscellaneous.png')
BACKGROUND_PROJECTILES = pygame.image.load('sprites/SpaceShooterAssetPack_Projectiles.png')
BACKGROUND_SHIPS = pygame.image.load('sprites/SpaceShooterAssetPack_Ships.png')

# Настройки окна
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Главное меню")

# Загрузка ресурсов
bg_scale = max(SCREEN_WIDTH / 256, SCREEN_HEIGHT / 128)
background_image = pygame.transform.scale(BACKGROUND_SHEET.subsurface(pygame.Rect(0, 0, 256, 128)), (bg_scale * 256, bg_scale * 128))
asteroid_image = BACKGROUND_MISC.subsurface(pygame.Rect(8, 24, 8, 8))  # Укажите путь к изображению астероида

# Шрифт и текст
font_path = 'font/ka1.ttf'
font_size = 30
font = pygame.font.Font(font_path, font_size)
logo_text = font.render("Asteroid crusher", True, (255, 255, 255))
font_size = 60
font = pygame.font.Font(font_path, font_size)
start_text = font.render("Start!", True, (255, 255, 255))

# Цвета
WHITE = (255, 255, 255)

# Кнопка для запуска игры
button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 50, 300, 100)

# Цвета для кнопки
button_color = (0, 0, 0, 150)  # Полупрозрачный черный
glow_color = (0, 255, 255, 100)  # Неоновый голубой цвет с прозрачностью
text_color = (255, 255, 255)  # Белый цвет для текста
font = pygame.font.Font(None, 50)  # Шрифт для текста

# Спрайт астероида
class Asteroid(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        scale = random.randint(20, 100)
        self.image = pygame.transform.scale(asteroid_image, (scale, scale))
        self.image.set_alpha(random.randint(50, 200))
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, SCREEN_WIDTH + 200)
        self.rect.y = random.randint(-30, SCREEN_HEIGHT)

        self.x = float(self.rect.x)
        self.y = float(self.rect.y)

        self.speed = random.uniform(0.07, 0.4)

    def update(self):
        self.x -= self.speed
        self.rect.x = int(self.x)

        if self.rect.right < 0:
            self.x = float(random.randint(SCREEN_WIDTH, SCREEN_WIDTH + 200))
            self.y = float(random.randint(0, SCREEN_HEIGHT))
            self.speed = random.uniform(0.3, 1)
            scale = random.randint(20, 50)
            self.image = pygame.transform.scale(asteroid_image, (scale, scale))
            self.image.set_alpha(random.randint(50, 200))

# Группа спрайтов астероидов
asteroids = pygame.sprite.Group()
for _ in range(20):
    asteroids.add(Asteroid())

# Заглушка для функции игры
def start_game():
    main()


# Главное меню
running = True
while running:

    # Отрисовка фона
    screen.blit(background_image, (0, 0))

    # Отрисовка и обновление астероидов
    asteroids.update()
    asteroids.draw(screen)

    # Цвета
    button_color = (0, 255, 255)  # Неоновый цвет
    outline_color = (0, 200, 200)  # Цвет обводки

    # Отрисовка кнопки с обводкой
    pygame.draw.rect(screen, outline_color, button_rect.inflate(10, 10), border_radius=15)  # Обводка
    pygame.draw.rect(screen, button_color, button_rect, border_radius=15)

    # Отрисовка текста и кнопки
    pygame.draw.rect(screen, (0, 0, 0, 100), button_rect, border_radius=15)
    screen.blit(logo_text, (SCREEN_WIDTH // 2 - logo_text.get_width() // 2, SCREEN_HEIGHT // 2 - 100))
    screen.blit(start_text, (SCREEN_WIDTH // 2 - start_text.get_width() // 2, SCREEN_HEIGHT // 2 - 40))

    # Обновление экрана
    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and button_rect.collidepoint(event.pos):
            start_game()
            running = False

# Завершение
pygame.quit()
