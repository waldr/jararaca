import pygame
import random


# pygame orders coodinates as (x, y), (width, height)

class DISPLAY_PARAMS:
    width = 1280
    height = 720
    max_fps = 15
    bg_color = (127, 127, 127)


class Grid:
    shape = (30, 20)
    cell_size = 30  # pixels
    border_size = 0  # pixels
    cell_colors = [(0, 127, 30), (0, 65, 0)]

    total_pixel_size = (
        shape[0] * (cell_size + border_size + 1),
        shape[1] * (cell_size + border_size + 1),
    )

    offset = (
        (DISPLAY_PARAMS.width - total_pixel_size[0]) // 2,
        (DISPLAY_PARAMS.height - total_pixel_size[1]) // 2
    )

    def __init__(self):
        self.food_positions = []
        pass

    def draw(self):
        for x in range(Grid.shape[0]):
            for y in range(Grid.shape[1]):
                rect = pygame.Rect(
                    self.to_display_coords(x, y),
                    (Grid.cell_size, Grid.cell_size)
                )
                pygame.draw.rect(screen, Grid.cell_colors[(x + y) % 2], rect)

        for food_pos in self.food_positions:
            pygame.draw.circle(
                screen,
                (160, 0, 0),  # random.choice([(160, 0, 0), (160, 160, 0)]),
                self.to_display_coords(food_pos[0], food_pos[1], centralized=True),
                7
            )

    def to_display_coords(self, x, y, centralized: bool = False):
        cell_ref_point = (Grid.cell_size // 2, Grid.cell_size // 2) if centralized else (0, 0)
        return (
            Grid.offset[0] + x * Grid.cell_size + (x + 1) * (Grid.border_size) + cell_ref_point[0],
            Grid.offset[1] + y * Grid.cell_size + (y + 1) * (Grid.border_size) + cell_ref_point[1]
        )

    def maybe_spawn_food(self, occupied_positions):
        if len(self.food_positions) < 5 and random.random() > 0.95:
            pos = (
                random.randint(0, self.shape[0] - 1),
                random.randint(0, self.shape[1] - 1)
            )
            if pos not in occupied_positions and pos not in self.food_positions:
                self.food_positions.append(pos)


class Snake:
    def __init__(self, initial_position, grid: Grid):
        self.positions = [
            initial_position,
            (initial_position[0], initial_position[1] - 1),
            (initial_position[0], initial_position[1] - 2),
            (initial_position[0] - 1, initial_position[1] - 2)
        ]
        self.grid = grid
        self.surfaces = self.init_surfaces()
        self.movement_direction = (0, 1)

    def init_surfaces(self):
        head = pygame.image.load('graphics/head.png').convert_alpha()
        body_V = pygame.image.load('graphics/body_V.png').convert_alpha()
        body_SW = pygame.image.load('graphics/body_SW.png').convert_alpha()
        surfaces = dict(
            head=head,
            body_V=body_V,
            body_H=pygame.transform.rotate(body_V, 90),
            body_SW=body_SW,
            body_SE=pygame.transform.rotate(body_SW, 90),
            body_NE=pygame.transform.rotate(body_SW, 180),
            body_NW=pygame.transform.rotate(body_SW, 270),
        )
        surfaces = dict(
            (k, pygame.transform.scale(surface, (self.grid.cell_size, self.grid.cell_size)))
            for (k, surface) in surfaces.items()
        )
        return surfaces

    def draw(self):
        self.draw_head()
        self.draw_body()

    def get_body_orientations(self):
        diffs = [
            (self.positions[i][0] - self.positions[i - 1][0],
             self.positions[i][1] - self.positions[i - 1][1])
            for i in range(1, len(self.positions))
        ]
        orientations = []
        for i in range(len(diffs)):
            if diffs[i][1] == 0:
                if i >= len(diffs) - 1:
                    orientation = 'H'
                elif diffs[i][0] == 1 and diffs[i + 1][1] == -1:
                    orientation = 'SE'
                elif diffs[i][0] == 1 and diffs[i + 1][1] == 1:
                    orientation = 'NE'
                elif diffs[i][0] == -1 and diffs[i + 1][1] == -1:
                    orientation = 'SW'
                elif diffs[i][0] == -1 and diffs[i + 1][1] == 1:
                    orientation = 'NW'
                else:
                    orientation = 'H'
            else:  # diffs[i][0] == 0:
                if i >= len(diffs) - 1:
                    orientation = 'V'
                elif diffs[i][1] == 1 and diffs[i + 1][0] == -1:
                    orientation = 'SE'
                elif diffs[i][1] == 1 and diffs[i + 1][0] == 1:
                    orientation = 'SW'
                elif diffs[i][1] == -1 and diffs[i + 1][0] == -1:
                    orientation = 'NE'
                elif diffs[i][1] == -1 and diffs[i + 1][0] == 1:
                    orientation = 'NW'
                else:
                    orientation = 'V'
            orientations.append(orientation)
        # print(diffs)
        # print(orientations)
        return orientations

    def draw_head(self):
        head = self.surfaces['head']
        rotation_angle = {
            (0, 1): 0,
            (1, 0): 90,
            (0, -1): 180,
            (-1, 0): 270
        }.get(self.movement_direction)
        head = pygame.transform.rotate(head, rotation_angle)
        screen.blit(head, self.grid.to_display_coords(*self.positions[0]))

    def draw_body(self):
        if len(self.positions) < 2:
            return
        orientations = self.get_body_orientations()
        for pos, orientation in zip(self.positions[1:], orientations):
            screen.blit(self.surfaces[f'body_{orientation}'], self.grid.to_display_coords(*pos))

    def update_position(self):
        self.positions.pop(-1)
        self.positions.insert(
            0,
            (
                self.positions[0][0] + self.movement_direction[0],
                self.positions[0][1] + self.movement_direction[1]
            )
        )

    def maybe_grow(self):
        next_pos = (self.positions[0][0] + self.movement_direction[0],
                    self.positions[0][1] + self.movement_direction[1])
        grew = False
        if next_pos in self.grid.food_positions:
            self.positions.insert(0, next_pos)
            grew = True
            self.grid.food_positions.remove(next_pos)
        return grew

    def is_collided(self):
        for pos in self.positions:
            for i in [0, 1]:
                if pos[i] >= self.grid.shape[i] or pos[i] < 0:
                    return True
        if len(self.positions) > 1:
            for pos in self.positions[1:]:
                if pos == self.positions[0]:
                    return True
        return False


class Scoreboard:
    def __init__(self, position):
        self.font = pygame.font.Font(pygame.font.get_default_font(), 24)
        self.position = position
        self.score = 0

    def get_score(self):
        return self.score

    def increment_score(self):
        self.score += 1

    def draw(self):
        text_surface = self.font.render(f'SCORE: {self.score}', False, (160, 0, 0))
        screen.blit(text_surface, self.position)


def get_new_movement_direction(pressed_keys):
    if pressed_keys[pygame.K_UP]:
        return (0, -1)
    elif pressed_keys[pygame.K_DOWN]:
        return (0, 1)
    elif pressed_keys[pygame.K_LEFT]:
        return (-1, 0)
    elif pressed_keys[pygame.K_RIGHT]:
        return (1, 0)
    else:
        return None


def game_loop(movement_direction):
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (
                event.type == pygame.KEYDOWN and pygame.key.get_pressed()[pygame.K_q]):
            pygame.quit()
            exit()
        new_direction = None
        if event.type == pygame.KEYDOWN:
            new_direction = get_new_movement_direction(pygame.key.get_pressed())
        if new_direction is not None:
            snake.movement_direction = new_direction
    grew = snake.maybe_grow()
    if grew:
        scoreboard.increment_score()
    snake.update_position()
    is_collided = snake.is_collided()
    if is_collided:
        print(f'DEAD! Final score: {scoreboard.get_score()}')
        pygame.quit()
        exit()
    screen.fill(DISPLAY_PARAMS.bg_color)
    grid.draw()
    snake.draw()
    scoreboard.draw()
    grid.maybe_spawn_food(snake.positions)
    pygame.display.update()
    clock.tick(DISPLAY_PARAMS.max_fps)
    return movement_direction


pygame.init()
screen = pygame.display.set_mode(
    (DISPLAY_PARAMS.width, DISPLAY_PARAMS.height))
pygame.display.set_caption('Jararaca')
clock = pygame.time.Clock()
grid = Grid()
snake = Snake((grid.shape[0] // 2, grid.shape[1] // 2), grid=grid)
scoreboard = Scoreboard((grid.offset[0], grid.offset[1] - 30))

movement_direction = (0, 1)
while True:
    movement_direction = game_loop(movement_direction)
