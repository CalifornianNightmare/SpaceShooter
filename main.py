import pygame
import random
import math

# ГЛОБАЛЬНЫЕ ПАРАМЕТРЫ
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
LIVES = 3  # Жизни
INITIAL_SCORE = 0  # Начальные счёт
ASTEROID_SPAWN_RATE = 1.5  # Промежуток между появлением астероидов
FRICTION = 0.99  # Сопротивление среды
ACCELERATION = 0.1  # Ускорение корабля
FUEL_BLAST_SPEED = 9  # Скорость вылета топлива
FUEL_BLAST_DELAY = 2  # Раз в сколько кадров вылетает топливо
FUEL_BLAST_LIFETIME = 0.1  # Время через которое топливо уничтожается
ROCKET_RELOAD = 3  # Перезарядка выстрела ракет
ANIMATION_FRAMES_PER_SPRITE = 5  # Сколько кадров длится один спрайт анимации


# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# Спрайты
BACKGROUND_SHEET = pygame.image.load('sprites/SpaceShooterAssetPack_BackGrounds.png')
BACKGROUND_IU = pygame.image.load('sprites/SpaceShooterAssetPack_IU.png')
BACKGROUND_MISC = pygame.image.load('sprites/SpaceShooterAssetPack_Miscellaneous.png')
BACKGROUND_PROJECTILES = pygame.image.load('sprites/SpaceShooterAssetPack_Projectiles.png')
BACKGROUND_SHIPS = pygame.image.load('sprites/SpaceShooterAssetPack_Ships.png')

# КЛАССЫ
class Spaceship:
    def __init__(self):
        self.image = pygame.transform.scale(BACKGROUND_SHIPS.subsurface(pygame.Rect(32, 48, 16, 16)), (32, 32))
        self.thrust_image = pygame.transform.scale(BACKGROUND_SHIPS.subsurface(pygame.Rect(32, 64, 19, 16)), (38, 32))
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.angle = 0
        self.velocity = pygame.math.Vector2(0, 0)
        self.thrusting = False

    def rotate(self, direction):
        self.angle += direction

    def accelerate(self):
        self.thrusting = True
        thrust_vector = pygame.math.Vector2(math.cos(math.radians(self.angle)), -math.sin(math.radians(self.angle)))
        self.velocity -= thrust_vector * ACCELERATION

    def update(self):
        if not self.thrusting:
            self.velocity *= FRICTION
        else:
            self.thrusting = False

        self.rect.center += self.velocity
        self.rect.centerx %= SCREEN_WIDTH
        self.rect.centery %= SCREEN_HEIGHT

    def draw(self, screen):
        rotated_image = pygame.transform.rotate(self.thrust_image if self.thrusting else self.image, self.angle)
        screen.blit(rotated_image, rotated_image.get_rect(center=self.rect.center))

class Asteroid:
    def __init__(self):
        size = random.randint(26, 48)
        self.image = pygame.transform.scale(BACKGROUND_MISC.subsurface(pygame.Rect(8, 24, 8, 8)), (size, size))

        spawn_side = random.choice(['top', 'bottom', 'left', 'right'])
        if spawn_side == 'top':
            self.rect = self.image.get_rect(center=(random.randint(0, SCREEN_WIDTH), 0))
        elif spawn_side == 'bottom':
            self.rect = self.image.get_rect(center=(random.randint(0, SCREEN_WIDTH), SCREEN_HEIGHT))
        elif spawn_side == 'left':
            self.rect = self.image.get_rect(center=(0, random.randint(0, SCREEN_HEIGHT)))
        else:
            self.rect = self.image.get_rect(center=(SCREEN_WIDTH, random.randint(0, SCREEN_HEIGHT)))

        center_x, center_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        direction = pygame.math.Vector2(center_x - self.rect.centerx, center_y - self.rect.centery)
        direction_length = direction.length()

        if direction_length > 0:
            direction.normalize_ip()
            min_speed = 0.4
            max_speed = 1.9
            speed = random.uniform(min_speed, max_speed)
            self.velocity = direction * speed
        else:
            self.velocity = pygame.math.Vector2(random.uniform(-1, 1), random.uniform(-1, 1)).normalize() * 2  # Fallback
        self.angular_velocity = random.uniform(-1, 1)
        self.angle = 0

    def update(self):
        self.rect.center += self.velocity

        if (self.rect.centerx < -self.rect.width or self.rect.centerx > SCREEN_WIDTH + self.rect.width or
                self.rect.centery > SCREEN_HEIGHT + self.rect.height):
            return False

        self.angle += self.angular_velocity
        return True

    def draw(self, screen):
        rotated_image = pygame.transform.rotate(self.image, self.angle)
        screen.blit(rotated_image, self.rect)

class FuelBlast:
    def __init__(self, position, angle):
        self.image = pygame.transform.scale(BACKGROUND_PROJECTILES.subsurface(pygame.Rect(2, 17, 3, 5)), (9, 18))
        self.image = pygame.transform.rotate(self.image, angle + 90)
        self.rect = self.image.get_rect(center=position)
        self.velocity = pygame.math.Vector2(math.cos(math.radians(angle)), -math.sin(math.radians(angle))) * FUEL_BLAST_SPEED
        self.lifetime = FUEL_BLAST_LIFETIME * FPS

    def update(self):
        self.rect.center += self.velocity
        if (self.rect.centerx % SCREEN_WIDTH != self.rect.centerx) or (self.rect.centery % SCREEN_HEIGHT != self.rect.centery):
            self.lifetime = 0
        self.lifetime -= 1

    def is_alive(self):
        return self.lifetime > 0

    def draw(self, screen):
        screen.blit(self.image, self.rect)

# КЛАСС РАКЕТЫ
class Rocket:
    def __init__(self, position, angle):
        self.image = pygame.transform.scale(BACKGROUND_PROJECTILES.subsurface(pygame.Rect(42, 17, 4, 5)), (8, 20))
        self.image = pygame.transform.rotate(self.image, angle + 90)
        self.rect = self.image.get_rect(center=position)
        self.velocity = pygame.math.Vector2(math.cos(math.radians(angle)), -math.sin(math.radians(angle))) * 10
        self.lifetime = int(min(SCREEN_WIDTH, SCREEN_HEIGHT) / self.velocity.length() * FPS * 0.8)  # Жизнь ракеты ограничена 80% от экрана

    def update(self):
        self.rect.center -= self.velocity
        self.lifetime -= 1
        return self.lifetime > 0

    def draw(self, screen):
        screen.blit(self.image, self.rect)


class Animation:
    def __init__(self, spritesheet, start_rect, frame_count, position, duration, size_multiplier, looping=False):
        self.frames = [
            pygame.transform.scale(spritesheet.subsurface(pygame.Rect(start_rect.x + i * start_rect.width, start_rect.y, start_rect.width, start_rect.height)),
                                   (start_rect.width * size_multiplier, start_rect.height * size_multiplier))  # Увеличиваем размер
            for i in range(frame_count)
        ]
        self.position = position
        self.duration = duration
        self.frame_duration = duration // frame_count
        self.current_frame = 0
        self.looping = looping
        self.time_elapsed = 0
        self.finished = False

    def update(self):
        if self.finished:
            return
        self.time_elapsed += 1
        if self.time_elapsed >= self.frame_duration:
            self.time_elapsed = 0
            self.current_frame += 1
            if self.current_frame >= len(self.frames):
                if self.looping:
                    self.current_frame = 0
                else:
                    self.finished = True

    def draw(self, screen):
        if not self.finished:
            frame = self.frames[self.current_frame]
            rect = frame.get_rect(center=self.position)
            screen.blit(frame, rect)


# Функция для отображения жизней
def draw_lives(screen, lives):
    heart_image = pygame.transform.scale(BACKGROUND_MISC.subsurface(pygame.Rect(16, 0, 8, 8)), (28, 28))  # Замените на изображение сердца
    for i in range(lives):
        screen.blit(heart_image, (10 + i * 32, 10))

def draw_score(screen, score, font):
    score_surface = font.render(f'Score: {score}', True, WHITE)
    screen.blit(score_surface, (10, 38))

# ГЛАВНАЯ ФУНКЦИЯ
def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Asteroids")
    clock = pygame.time.Clock()

    # Загрузка шрифта
    font_path = 'font/ka1.ttf'
    font_size = 30
    font = pygame.font.Font(font_path, font_size)

    # ПЕРЕМЕННЫЕ ИГРЫ
    spaceship = Spaceship()
    asteroids = []
    fuel_blasts = []
    rockets = []
    animations = []
    lives = LIVES
    score = INITIAL_SCORE
    running = True
    spawn_timer = 0

    fuel_blast_delay_counter = 0
    rocket_reload_timer = ROCKET_RELOAD

    bg_scale = max(SCREEN_WIDTH / 256, SCREEN_HEIGHT / 128)
    background_image = pygame.transform.scale(BACKGROUND_SHEET.subsurface(pygame.Rect(0, 0, 256, 128)), (bg_scale * 256, bg_scale * 128))

    # ГЛАВНЫЙ ЦИКЛ
    while running:

        # Фон
        screen.fill(BLACK)
        screen.blit(background_image, (0, 0))

        # Выход
        for event in pygame.event.get():
            if event.type == pygame.QUIT:

                pygame.quit()


        # Нажатие клавиш
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            spaceship.rotate(5)
        if keys[pygame.K_RIGHT]:
            spaceship.rotate(-5)
        fuel_blast_delay_counter += 1
        if keys[pygame.K_UP]:
            spaceship.accelerate()
            if fuel_blast_delay_counter >= FUEL_BLAST_DELAY:
                fuel_blasts.append(FuelBlast(spaceship.rect.center, spaceship.angle))
                fuel_blast_delay_counter = 0
        rocket_reload_timer += 1 / FPS
        if keys[pygame.K_SPACE] and rocket_reload_timer >= ROCKET_RELOAD:
            spaceship.thrusting = True
            rockets.append(Rocket(spaceship.rect.center, spaceship.angle))
            rocket_reload_timer = 0

        # Анимация перезарядки
        if abs(rocket_reload_timer - ROCKET_RELOAD) < 0.001:

            animations.append(Animation(
                BACKGROUND_MISC,
                pygame.Rect(40, 48, 8, 8),
                4,
                spaceship.rect.center,
                ANIMATION_FRAMES_PER_SPRITE * 4,
                5,
                looping=False
            ))

        # Чекаем топливо на натуральную смерть
        fuel_blasts_to_remove = []
        for fuel_blast in fuel_blasts:
            fuel_blast.update()
            if not fuel_blast.is_alive():
                fuel_blasts_to_remove.append(fuel_blast)

        # Чекаем ракету на натуральную смерть
        rockets_to_remove = []
        for rocket in rockets:
            if not rocket.update():
                rockets_to_remove.append(rocket)

        # Астероиды спавн
        spawn_timer += 1 / FPS
        if spawn_timer > ASTEROID_SPAWN_RATE:
            asteroids.append(Asteroid())
            spawn_timer = 0

        # Чекаем различные столкновения с астероидами
        asteroids_to_remove = []
        for asteroid in asteroids:
            if not asteroid.update():
                # Астероиды за экраном
                asteroids_to_remove.append(asteroid)
            else:

                # Столкновение с кораблём
                if spaceship.rect.colliderect(asteroid.rect):
                    lives -= 1
                    asteroids_to_remove.append(asteroid)

                    animations.append(Animation(
                        BACKGROUND_MISC,
                        pygame.Rect(40, 32, 16, 16),  # Координаты первого кадра анимации потери здоровья
                        4,
                        spaceship.rect.center,
                        ANIMATION_FRAMES_PER_SPRITE * 4,
                        10,
                        looping=False
                    ))

                    if lives == 0:
                        running = False

                # Столкновение с топливом
                for fuel_blast in fuel_blasts:
                    if fuel_blast.rect.colliderect(asteroid.rect):
                        score += 1
                        fuel_blasts_to_remove.append(fuel_blast)
                        asteroids_to_remove.append(asteroid)

                # Столкновение с ракетой
                for rocket in rockets:
                    if rocket.rect.colliderect(asteroid.rect):
                        score += 1
                        rockets_to_remove.append(rocket)
                        asteroids_to_remove.append(asteroid)

        # Убеждаемся что не было два удаления в один кадр
        asteroids = [asteroid for asteroid in asteroids if asteroid not in asteroids_to_remove]
        fuel_blasts = [fuel_blast for fuel_blast in fuel_blasts if fuel_blast not in fuel_blasts_to_remove]
        rockets = [rocket for rocket in rockets if rocket not in rockets_to_remove]

        for asteroid in asteroids_to_remove:
            animations.append(Animation(
                BACKGROUND_MISC,
                pygame.Rect(72, 48, 8, 8),  # Координаты первого кадра взрыва
                4,
                asteroid.rect.center,
                ANIMATION_FRAMES_PER_SPRITE * 4,
                9,
                looping=False
            ))

        # Отрисовка объектов
        for asteroid in asteroids:
            asteroid.draw(screen)
        for fuel_blast in fuel_blasts:
            fuel_blast.draw(screen)
        for rocket in rockets:
            rocket.draw(screen)

        spaceship.draw(screen)
        spaceship.update()

        animations_to_remove = []
        for animation in animations:
            animation.update()
            if animation.finished:
                animations_to_remove.append(animation)
            else:
                animation.draw(screen)

        animations = [anim for anim in animations if anim not in animations_to_remove]

        # Отображение жизней и счёта
        draw_lives(screen, lives)
        draw_score(screen, score, font)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
