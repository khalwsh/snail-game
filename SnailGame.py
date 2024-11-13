import pygame
from sys import exit
from random import randint, choice

def initialize_game():
    pygame.init()
    screen = pygame.display.set_mode((800, 400))
    pygame.display.set_caption('Snail Game')
    clock = pygame.time.Clock()
    font = pygame.font.Font('assets/font/Pixeltype.ttf', 50)
    return screen, clock, font

def load_assets():
    # Player assets
    player_walk = [
        pygame.image.load('assets/graphics/player/player_walk_1.png').convert_alpha(),
        pygame.image.load('assets/graphics/player/player_walk_2.png').convert_alpha()
    ]
    player_jump = pygame.image.load('assets/graphics/player/jump.png').convert_alpha()
    player_stand = pygame.transform.rotozoom(pygame.image.load('assets/graphics/player/player_stand.png').convert_alpha(), 0, 2)

    # Obstacle assets
    snail_frames = [
        pygame.image.load('assets/graphics/snail/snail1.png').convert_alpha(),
        pygame.image.load('assets/graphics/snail/snail2.png').convert_alpha()
    ]
    fly_frames = [
        pygame.image.load('assets/graphics/fly/fly1.png').convert_alpha(),
        pygame.image.load('assets/graphics/fly/fly2.png').convert_alpha()
    ]

    # Background assets
    sky_surfaces = [
        pygame.image.load('assets/graphics/Sky.png').convert(),
        pygame.image.load('assets/graphics/Night_Sky.png').convert()
    ]
    ground_surfaces = [
        pygame.image.load('assets/graphics/ground.png').convert(),
        pygame.image.load('assets/graphics/night_ground.png').convert()
    ]

    # Audio
    jump_sound = pygame.mixer.Sound('assets/audio/jump.mp3')
    jump_sound.set_volume(0.5)
    bg_music = pygame.mixer.Sound('assets/audio/music.wav')
    bg_music.play(loops=-1)

    return {
        "player_walk": player_walk,
        "player_jump": player_jump,
        "player_stand": player_stand,
        "snail_frames": snail_frames,
        "fly_frames": fly_frames,
        "sky_surfaces": sky_surfaces,
        "ground_surfaces": ground_surfaces,
        "jump_sound": jump_sound,
        "bg_music": bg_music
    }

def handle_player_input(player, jump_sound):
    keys = pygame.key.get_pressed()
    if keys[pygame.K_SPACE] and player["rect"].bottom >= 300:
        player["gravity"] = -20
        jump_sound.play()

def update_player(player, player_assets):
    player["gravity"] += 1
    player["rect"].y += player["gravity"]
    if player["rect"].bottom >= 300:
        player["rect"].bottom = 300
    if player["rect"].bottom < 300:
        player["surf"] = player_assets["player_jump"]
    else:
        player["index"] += 0.1
        if player["index"] >= len(player_assets["player_walk"]):
            player["index"] = 0
        player["surf"] = player_assets["player_walk"][int(player["index"])]

def create_obstacle(obstacle_type, obstacle_assets):
    if obstacle_type == 'fly':
        frames = obstacle_assets["fly_frames"]
        y_pos = 210
    else:
        frames = obstacle_assets["snail_frames"]
        y_pos = 300
    return {"rect": frames[0].get_rect(midbottom=(randint(900, 1100), y_pos)), "frames": frames, "index": 0}

def update_obstacles(obstacles):
    for obstacle in obstacles:
        obstacle["rect"].x -= 6
        obstacle["index"] += 0.1
        if obstacle["index"] >= len(obstacle["frames"]):
            obstacle["index"] = 0
    obstacles = [ob for ob in obstacles if ob["rect"].x > -100]
    return obstacles

def display_score(screen, font, start_time):
    current_time = int(pygame.time.get_ticks() / 1000) - start_time
    score_surf = font.render(f'Score: {current_time}', False, (64, 64, 64))
    score_rect = score_surf.get_rect(center=(400, 50))
    screen.blit(score_surf, score_rect)
    return current_time

def check_collisions(player, obstacles):
    for obstacle in obstacles:
        if player["rect"].colliderect(obstacle["rect"]):
            return False
    return True
def player_setup(assets):
    player_walk = assets["player_walk"]
    return {
        "rect": player_walk[0].get_rect(midbottom=(80, 300)),
        "gravity": 0,
        "index": 0,
        "surf": player_walk[0]
    }

def main():
    screen, clock, font = initialize_game()
    assets = load_assets()

    # Initialize game states
    player = player_setup(assets)
    obstacles = []
    start_time = 0
    game_active = False
    score = 0  # Initialize score here

    # Background and ground settings for day and night
    sky_index, ground_index = 0, 0
    sky_surface = assets["sky_surfaces"][sky_index]
    ground_surface = assets["ground_surfaces"][ground_index]

    # Set a timer for switching between day and night every 10 seconds
    night_mode_timer = pygame.USEREVENT + 1
    pygame.time.set_timer(night_mode_timer, 10000)  # Switch every 10,000 ms (10 seconds)

    pygame.time.set_timer(pygame.USEREVENT, 1500)  # Obstacle spawn timer

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if game_active:
                if event.type == pygame.MOUSEBUTTONDOWN and player["rect"].collidepoint(event.pos) and player["rect"].bottom >= 300:
                    player["gravity"] = -20
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    player["gravity"] = -20
            else:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    game_active = True
                    start_time = int(pygame.time.get_ticks() / 1000)
                    score = 0  # Reset score at the start of a new game

            # Switch between day and night
            if event.type == night_mode_timer:
                sky_index = 1 - sky_index  # Toggle between 0 (day) and 1 (night)
                ground_index = 1 - ground_index  # Toggle ground
                sky_surface = assets["sky_surfaces"][sky_index]
                ground_surface = assets["ground_surfaces"][ground_index]

            if game_active and event.type == pygame.USEREVENT:
                obstacles.append(create_obstacle(choice(['fly', 'snail', 'snail', 'snail']), assets))

        if game_active:
            screen.blit(sky_surface, (0, 0))
            screen.blit(ground_surface, (0, 300))
            score = display_score(screen, font, start_time)  # Update the score during the game

            # Player
            handle_player_input(player, assets["jump_sound"])
            update_player(player, assets)
            screen.blit(player["surf"], player["rect"])

            # Obstacles
            obstacles = update_obstacles(obstacles)
            for obstacle in obstacles:
                screen.blit(obstacle["frames"][int(obstacle["index"])], obstacle["rect"])

            # Collision check
            game_active = check_collisions(player, obstacles)
        else:
            # Game Over screen
            screen.fill((94, 129, 162))
            screen.blit(assets["player_stand"], assets["player_stand"].get_rect(center=(400, 200)))
            score_message = font.render(f'Your score: {score}', False, (111, 196, 169))
            score_message_rect = score_message.get_rect(center=(400, 330))
            screen.blit(score_message, score_message_rect)

            # Reset day mode at the end of the game
            sky_index, ground_index = 0, 0
            sky_surface = assets["sky_surfaces"][sky_index]
            ground_surface = assets["ground_surfaces"][ground_index]

        pygame.display.update()
        clock.tick(60)

main()
