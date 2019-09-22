# gaming_assembly.py
# uses pyparticles to create displayed game

import itertools
import pickle
import random
import time

import pygame

import pyparticles

# declare size of window and track to use
(width, height) = (1200, 450)
track = 'track.bmp'
# given track, place checkpoints
checkpoints = [(400, 150), (500, 70), (600, 60), (640, 140), (605, 210), (680, 300), (720, 380), (580, 390), (450, 350),
               (320, 320), (250, 235), (110, 325), (60, 200), (125, 75), (290, 90)]

# set up run parameters
duration = 60
n_generations = 40
generation_size = 300
n_to_keep = 10

# for ease, define colours here
RED = (255, 0, 0)
WHITE = (255, 255, 255)
GREY = (230, 230, 230)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)

# Train to create save file of best racers, Race to race them on a starting grid
Train = True
Race = False


def update_screen(env, screen):
    font = pygame.font.Font(None, 32)
    header = font.render('LEADERBOARD', True, RED, WHITE)
    header_rect = header.get_rect()
    header_rect.center = (800 + 200, 40)

    track_image = pygame.image.load(track)
    track_rect = track_image.get_rect()
    track_rect.left, track_rect.left = [0, 0]

    env.update()
    screen.fill(env.colour)
    screen.blit(track_image, track_rect)

    for pos in checkpoints:
        pygame.draw.circle(screen, RED, pos, 5, 5)

    # draw cars
    for car in env.particles:
        pygame.draw.circle(screen, car.colour, (int(car.x), int(car.y)), car.size, car.thickness)

        sorted_list = sorted(env.particles, key=lambda particle: particle.score)[::-1]

        # draw leaderboard
        screen.blit(header, header_rect)

        for i in range(0, 10):
            car = sorted_list[i]

            leader_x = 800 + 75
            leader_y = 80 + i * 35

            leader_id = font.render(str(i + 1), True, BLACK, WHITE)
            number_rect = leader_id.get_rect()
            number_rect.center = (leader_x - 10, leader_y)
            screen.blit(leader_id, number_rect)

            pygame.draw.circle(screen, car.colour, (leader_x + 20, leader_y), car.size, car.thickness)

            leader_name = font.render(str(car.name), True, BLACK, WHITE)
            name_rect = leader_name.get_rect()
            name_rect.midleft = (leader_x + 45, leader_y)
            screen.blit(leader_name, name_rect)

            leader_score = font.render(str(round(car.score, 3)), True, BLACK, WHITE)
            score_rect = leader_score.get_rect()
            score_rect.midleft = (leader_x + 100, leader_y)
            screen.blit(leader_score, score_rect)

            if car.w:
                display_w = font.render('W', True, BLACK, WHITE)
            else:
                display_w = font.render('W', True, GREY, WHITE)
            display_w_rect = display_w.get_rect()
            display_w_rect.center = (leader_x + 190, leader_y)
            screen.blit(display_w, display_w_rect)

            if car.a:
                display_a = font.render('A', True, BLACK, WHITE)
            else:
                display_a = font.render('A', True, GREY, WHITE)
            display_a_rect = display_a.get_rect()
            display_a_rect.center = (leader_x + 212, leader_y)
            screen.blit(display_a, display_a_rect)

            if car.s:
                display_s = font.render('S', True, BLACK, WHITE)
            else:
                display_s = font.render('S', True, GREY, WHITE)
            display_s_rect = display_s.get_rect()
            display_s_rect.center = (leader_x + 230, leader_y)
            screen.blit(display_s, display_s_rect)

            if car.d:
                display_d = font.render('D', True, BLACK, WHITE)
            else:
                display_d = font.render('D', True, GREY, WHITE)
            display_d_rect = display_d.get_rect()
            display_d_rect.center = (leader_x + 250, leader_y)
            screen.blit(display_d, display_d_rect)
    pygame.display.flip()


def train():
    # initiate display and display options
    screen = pygame.display.set_mode((width, height))

    # initialise environment
    env = pyparticles.Environment((width, height), image=track, checkpoints=checkpoints, colliding=False)

    # add initial particles
    for i in range(generation_size):
        env.addParticles(1, x=checkpoints[0][0], y=checkpoints[0][1], speed=0, size=5)

    pygame.init()

    n = 0
    while n < n_generations:
        print('##################')
        print('## GENERATION ' + str(n + 1) + ' ##')
        print('##################')

        pygame.display.set_caption('Generation ' + str(n + 1))

        # initiate run
        pygame.init()
        running = True
        start_time = time.time()
        current_time = time.time()

        while current_time - start_time < duration and running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            update_screen(env, screen)

            current_time = time.time()
            env.time_elapsed = int(round((current_time - start_time) * 1000))

        # breed new generation
        sorted_list = sorted(env.particles, key=lambda particle: particle.score)[::-1]
        env = pyparticles.Environment((width, height), image=track, checkpoints=checkpoints, colliding=False)

        for i in range(n_to_keep - 1):
            parent_pairs = list(itertools.combinations(range(i + 1), 2))

            for pair in parent_pairs:
                control_rods, bias, fov, colour = pyparticles.breed(sorted_list[pair[0]], sorted_list[pair[1]])
                env.addParticles(1, x=checkpoints[0][0], y=checkpoints[0][1], speed=0, size=5,
                                 control_rods=control_rods, bias=bias, fov=fov, colour=colour)

        while len(env.particles) < (generation_size - 5):
            parent1 = sorted_list[random.randint(0, generation_size - 1)]
            parent2 = sorted_list[random.randint(0, generation_size - 1)]
            control_rods, bias, fov, colour = pyparticles.breed(parent1, parent2)
            env.addParticles(1, x=checkpoints[0][0], y=checkpoints[0][1], speed=0, size=5, control_rods=control_rods,
                             bias=bias, fov=fov, colour=colour)

        while len(env.particles) < generation_size:
            env.addParticles(1, x=checkpoints[0][0], y=checkpoints[0][1], speed=0, size=5)

        # save these particles to file
        with open('final_drivers', 'wb') as output:
            driver_list = sorted_list[:10]
            pickle.dump(driver_list, output)

        n += 1


def race():
    # load in drivers
    with open('final_drivers', 'rb') as driver_file:
        driver_list = pickle.load(driver_file)

    # initiate race window
    pygame.display.set_caption('Race!')
    screen = pygame.display.set_mode((width, height))

    # create starting grid based on initial checkpoint
    spacing = 15
    starting_grid = [(checkpoints[0][0], checkpoints[0][1]),
                     (checkpoints[0][0] - spacing, checkpoints[0][1]),
                     (checkpoints[0][0], checkpoints[0][1] - spacing),
                     (checkpoints[0][0] - spacing, checkpoints[0][1] - spacing),
                     (checkpoints[0][0] - 2 * spacing, checkpoints[0][1]),
                     (checkpoints[0][0], checkpoints[0][1] - 2 * spacing),
                     (checkpoints[0][0] - 2 * spacing, checkpoints[0][1] - spacing),
                     (checkpoints[0][0] - 2 * spacing, checkpoints[0][1] - 2 * spacing),
                     (checkpoints[0][0] - spacing, checkpoints[0][1] - 2 * spacing),
                     (checkpoints[0][0] - 3 * spacing, checkpoints[0][1] - spacing)]

    env = pyparticles.Environment((width, height), image=track, checkpoints=checkpoints, colliding=False)

    # load in drivers
    i = 0
    for car in driver_list:
        fov = random.uniform(0, 90)
        env.addParticles(1, x=starting_grid[i][0], y=starting_grid[i][1], speed=0, size=5, control_rods=car.control_rods,
                         bias=car.bias, fov=car.fov)
        i += 1

    pygame.init()

    # begin run
    running = True
    start_time = time.time()
    current_time = time.time()
    while current_time - start_time < duration and running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # update cars + leaderboard
        update_screen(env, screen)

        current_time = time.time()
        env.time_elapsed = int(round((current_time - start_time) * 100000)) / 100


if __name__ == '__main__':
    if Train:
        train()
    elif Race:
        race()
