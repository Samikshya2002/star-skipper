import pygame
import time
import random
import math


pygame.font.init()


WIDTH, HEIGHT = 1000, 800


pygame.init()
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Star Skipper')


BG = pygame.transform.scale(pygame.image.load('img.jpg'), (WIDTH, HEIGHT))


PLAYER_HEIGHT = 60
PLAYER_WIDTH = 30
PLAYER_VEL = 5


STAR_RADIUS = 10
STAR_VEL = 3


player_img = pygame.transform.scale(pygame.image.load('person.png'), (PLAYER_WIDTH, PLAYER_HEIGHT))


FONT = pygame.font.SysFont('comicsans', 30)


class Player:
    def __init__(self, x, y, width, height, velocity):
        self.rect = pygame.Rect(x, y, width, height)
        self.velocity = velocity

    def move(self, keys):
        if keys[pygame.K_LEFT] and self.rect.x - self.velocity >= 0:
            self.rect.x -= self.velocity
        if keys[pygame.K_RIGHT] and self.rect.x + self.velocity + self.rect.width <= WIDTH:
            self.rect.x += self.velocity

    def draw(self):
        WIN.blit(player_img, (self.rect.x, self.rect.y))


class Star:
    def __init__(self, x, y, radius, velocity):
        self.points = self.generate_star_points(x, y, radius, 5)
        self.velocity = velocity

    @staticmethod
    def generate_star_points(x, y, radius, num_points):
        points = []
        angle = math.pi / num_points
        for i in range(num_points * 2):
            if i % 2 == 0:
                points.append([x + radius * math.cos(i * angle), y + radius * math.sin(i * angle)])
            else:
                points.append([x + radius / 2 * math.cos(i * angle), y + radius / 2 * math.sin(i * angle)])
        return points

    def move(self):
        for point in self.points:
            point[1] += self.velocity

    def is_off_screen(self):
        return self.points[-1][1] > HEIGHT

    def draw(self):
        pygame.draw.polygon(WIN, 'gray', self.points)


class Level:
    def __init__(self, num_stars, star_vel):
        self.num_stars = num_stars
        self.star_vel = star_vel

    def generate_stars(self):
        return [StarFactory.create_star(self.star_vel) for _ in range(self.num_stars)]


class StarFactory:
    @staticmethod
    def create_star(velocity):
        star_x = random.randint(0, WIDTH - 2 * STAR_RADIUS)
        star_y = random.randint(-HEIGHT, 0)
        return Star(star_x + STAR_RADIUS, star_y + STAR_RADIUS, STAR_RADIUS, velocity)


class UIManager:
    @staticmethod
    def draw_time(elapsed_time):
        time_text = FONT.render(f'Time: {round(elapsed_time)}s', 1, 'white')
        WIN.blit(time_text, (10, 10))

    @staticmethod
    def show_lost_screen():
        lost_text = FONT.render('You Lost!', 1, 'white')
        WIN.blit(lost_text, (WIDTH / 2 - lost_text.get_width() / 2, HEIGHT / 2 - lost_text.get_height() / 2))
        pygame.display.update()
        pygame.time.delay(4000)


class CollisionManager:
    @staticmethod
    def check_collision(player, stars):
        for star in stars:
            if player.rect.colliderect(pygame.Rect(star.points[0][0], star.points[0][1], STAR_RADIUS, STAR_RADIUS)):
                return True
        return False


class Timer:
    def __init__(self):
        self.start_time = time.time()

    def get_elapsed_time(self):
        return time.time() - self.start_time


class Game:
    def __init__(self):
        self.player = Player(200, HEIGHT - PLAYER_HEIGHT, PLAYER_WIDTH, PLAYER_HEIGHT, PLAYER_VEL)
        self.levels = [Level(5, 3), Level(8, 4), Level(12, 5)]
        self.current_level_index = 0
        self.stars = self.levels[self.current_level_index].generate_stars()
        self.clock = pygame.time.Clock()
        self.timer = Timer()
        self.star_add_increment = 2000
        self.star_count = 0
        self.running = True

    def update_level(self):
        if self.current_level_index < len(self.levels):
            level = self.levels[self.current_level_index]
            self.stars = level.generate_stars()

    def check_level_completion(self):
        if len(self.stars) == 0:
            self.current_level_index += 1
            if self.current_level_index < len(self.levels):
                self.update_level()
                print(f"Level {self.current_level_index} completed. Moving to level {self.current_level_index + 1}")
            else:
                print("Congratulations! You completed all levels.")
                self.running = False

    def run(self):
        while self.running:
            self.star_count += self.clock.tick(60)

            elapsed_time = self.timer.get_elapsed_time()
            if self.star_count > self.star_add_increment:
                level = self.levels[self.current_level_index]
                self.stars.extend([StarFactory.create_star(level.star_vel) for _ in range(5)])
                self.star_add_increment = max(200, self.star_add_increment - 50)
                self.star_count = 0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    break

            keys = pygame.key.get_pressed()
            self.player.move(keys)

            for star in self.stars[:]:
                star.move()
                if star.is_off_screen():
                    self.stars.remove(star)
                elif CollisionManager.check_collision(self.player, [star]):
                    UIManager.show_lost_screen()
                    self.running = False
                    break

            # Check if the level is completed
            self.check_level_completion()

            self.draw(elapsed_time)
        pygame.quit()

    def draw(self, elapsed_time):
        WIN.blit(BG, (0, 0))
        UIManager.draw_time(elapsed_time)
        self.player.draw()
        for star in self.stars:
            star.draw()
        pygame.display.update()


if __name__ == '__main__':
    game = Game()
    game.run()
