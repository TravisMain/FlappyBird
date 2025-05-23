import pygame
import sys
import random
import os
from bird_manager import BirdManager

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Initialize Pygame
pygame.init()
pygame.mixer.init() # Initialize the mixer for sounds

# Screen dimensions
screen_width = 288
screen_height = 512
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Flappy Bird')

# Game clock
clock = pygame.time.Clock()

# Game Difficulty Settings
pipe_move_speed = 2         # Reduced from 3 to 2 for better pacing
pipe_spawn_interval = 1800  # Increased from 1500 to 1800 for more spacing
pipe_gap_size = 150         # Keep the same gap size

# High Score File
high_score_file = "highscore.txt"

# Initialize bird manager
bird_manager = BirdManager()

# Game state
game_state = 'start_screen'  # 'start_screen', 'bird_select', 'game_active', 'game_over'
selected_bird_type = 'blue'
score = 0
high_score = 0
coin_count = 0 # Initialize coin count
pipes_passed_count = 0 # Track pipes passed for difficulty

# UI Settings
UI_PADDING = 20
UI_SPACING = 30

# Font setup
font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 24)

# Background scroll speed (keep global as it's a constant)
background_scroll_speed = 0.5

# Timer for spawning pipes (defined globally)
PIPE_SPAWN_EVENT = pygame.USEREVENT # Define PIPE_SPAWN_EVENT globally

# Function to load high score
def load_high_score():
    try:
        with open(high_score_file, 'r') as f:
            score_val = int(f.read())
            return score_val
    except (IOError, ValueError):
        return 0

# Function to save high score
def save_high_score(score_val):
    try:
        with open(high_score_file, 'w') as f:
            f.write(str(score_val))
    except IOError:
        print("Error saving high score")

# Load high score
high_score = load_high_score()

# Load Sounds
try:
    sound_flap = pygame.mixer.Sound(resource_path('assets/audio/wing.ogg'))
    sound_point = pygame.mixer.Sound(resource_path('assets/audio/point.ogg'))
    sound_hit = pygame.mixer.Sound(resource_path('assets/audio/hit.ogg'))
    sound_die = pygame.mixer.Sound(resource_path('assets/audio/die.ogg'))
    sound_swoosh = pygame.mixer.Sound(resource_path('assets/audio/swoosh.ogg'))
except pygame.error as e:
    print(f"Error loading sound(s): {e}. Sound effects will be disabled.")
    class DummySound:
        def play(self):
            pass
    sound_flap = DummySound()
    sound_point = DummySound()
    sound_hit = DummySound()
    sound_die = DummySound()
    sound_swoosh = DummySound()

# Load Background Music
try:
    pygame.mixer.music.load(resource_path('assets/audio/background.mp3'))
    pygame.mixer.music.set_volume(0.5) # Adjust volume as needed (0.0 to 1.0)
except pygame.error as e:
    print(f"Error loading background music: {e}. Background music will not play.")

# Load images (assuming they are in an 'assets' folder)
# For now, we'll use placeholder colors if images are not found
try:
    bird_image_mid = pygame.image.load(resource_path('assets/sprites/yellowbird-midflap.png')).convert_alpha()
    bird_image_up = pygame.image.load(resource_path('assets/sprites/yellowbird-upflap.png')).convert_alpha()
    bird_image_down = pygame.image.load(resource_path('assets/sprites/yellowbird-downflap.png')).convert_alpha()
    bird_frames = [bird_image_down, bird_image_mid, bird_image_up]
except pygame.error as e:
    print(f"Error loading bird animation frames: {e}. Trying single bird.png or placeholder.")
    try:
        bird_image = pygame.image.load(resource_path('assets/sprites/yellowbird-midflap.png')).convert_alpha()
        bird_frames = [bird_image, bird_image, bird_image]
    except pygame.error as e2:
        print(f"Error loading bird.png: {e2}. Using a placeholder rectangle.")
        bird_frames = None

try:
    pipe_image = pygame.image.load(resource_path('assets/sprites/pipe-green.png')).convert_alpha()
except pygame.error as e:
    print(f"Error loading pipe image: {e}. Using a placeholder.")
    pipe_image = None

try:
    background_image = pygame.image.load(resource_path('assets/sprites/background-day.png')).convert()
    background_image = pygame.transform.scale(background_image, (screen_width, screen_height))
except pygame.error as e:
    print(f"Error loading background image: {e}. Using default sky color.")
    background_image = None

try:
    message_image = pygame.image.load(resource_path('assets/sprites/message.png')).convert_alpha()
except pygame.error as e:
    print(f"Error loading message.png: {e}. Start screen message image will not be shown.")
    message_image = None

try:
    game_over_image = pygame.image.load(resource_path('assets/sprites/gameover.png')).convert_alpha()
except pygame.error as e:
    print(f"Error loading gameover.png: {e}. Game over image will not be shown.")
    game_over_image = None

# Load coin image (sprite sheet)
try:
    # Assuming coin animation frames are 20x20 pixels and laid out horizontally (updated)
    coin_sprite_sheet = pygame.image.load(resource_path('assets/sprites/Coin_One.png')).convert_alpha()
    coin_frame_width = 20 # Assumed frame width (changed back to 20)
    coin_frame_height = 20 # Assumed frame height (changed back to 20)
    # Calculate the number of frames based on sprite sheet width
    num_coin_frames = coin_sprite_sheet.get_rect().width // coin_frame_width
    # Extract frames
    coin_frames = []
    for i in range(num_coin_frames):
        frame = coin_sprite_sheet.subsurface((i * coin_frame_width, 0, coin_frame_width, coin_frame_height))
        coin_frames.append(frame)

except pygame.error as e:
    print(f"Error loading coin sprite sheet: {e}. Using a placeholder.")
    coin_sprite_sheet = None
    coin_frames = None # Use None to indicate no animation frames loaded
    coin_frame_width = 20 # Match placeholder size
    coin_frame_height = 20 # Match placeholder size

except FileNotFoundError:
    print("Coin_One.png not found. Using a placeholder.")
    coin_sprite_sheet = None
    coin_frames = None
    coin_frame_width = 20 # Match placeholder size
    coin_frame_height = 20 # Match placeholder size

# Load power-up countdown sprites
try:
    countdown_1 = pygame.image.load(resource_path('assets/sprites/1.png')).convert_alpha()
    countdown_2 = pygame.image.load(resource_path('assets/sprites/2.png')).convert_alpha()
    countdown_3 = pygame.image.load(resource_path('assets/sprites/3.png')).convert_alpha()
    countdown_sprites = [countdown_3, countdown_2, countdown_1]  # Order matters for countdown
except pygame.error as e:
    print(f"Error loading countdown sprites: {e}. Countdown will not be shown.")
    countdown_sprites = None

# Load base image
try:
    base_image = pygame.image.load(resource_path('assets/sprites/base.png')).convert_alpha()
except pygame.error as e:
    print(f"Error loading base image: {e}. Using a placeholder.")
    base_image = None

# Bird class
class Bird(pygame.sprite.Sprite):
    def __init__(self, bird_type='default'):
        super().__init__()
        self.bird_type = bird_type
        self.frames = self._load_bird_frames()
        self.frame_index = 0
        self.animation_speed = 0.15
        self.animation_timer = 0

        if self.frames:
            self.image = self.frames[self.frame_index]
        else:
            self.image = pygame.Surface([34, 24])
            self.image.fill((255, 255, 0))
            self.frames = [self.image, self.image, self.image]
        
        self.rect = self.image.get_rect(center=(50, screen_height // 2))
        self.velocity = 0
        self.gravity = 0.25
        self.flap_strength = -6
        self.horizontal_speed = 0

        self._apply_bird_type_attributes()

    def _load_bird_frames(self):
        try:
            if self.bird_type == 'red':
                return [
                    pygame.image.load(resource_path('assets/sprites/redbird-downflap.png')).convert_alpha(),
                    pygame.image.load(resource_path('assets/sprites/redbird-midflap.png')).convert_alpha(),
                    pygame.image.load(resource_path('assets/sprites/redbird-upflap.png')).convert_alpha()
                ]
            elif self.bird_type == 'yellow':
                return [
                    pygame.image.load(resource_path('assets/sprites/yellowbird-downflap.png')).convert_alpha(),
                    pygame.image.load(resource_path('assets/sprites/yellowbird-midflap.png')).convert_alpha(),
                    pygame.image.load(resource_path('assets/sprites/yellowbird-upflap.png')).convert_alpha()
                ]
            elif self.bird_type == 'blue':
                return [
                    pygame.image.load(resource_path('assets/sprites/bluebird-downflap.png')).convert_alpha(),
                    pygame.image.load(resource_path('assets/sprites/bluebird-midflap.png')).convert_alpha(),
                    pygame.image.load(resource_path('assets/sprites/bluebird-upflap.png')).convert_alpha()
                ]
            else:  # default bird (will be removed later)
                 return [
                    pygame.image.load(resource_path('assets/sprites/bluebird-downflap.png')).convert_alpha(),
                    pygame.image.load(resource_path('assets/sprites/bluebird-midflap.png')).convert_alpha(),
                    pygame.image.load(resource_path('assets/sprites/bluebird-upflap.png')).convert_alpha()
                ]
        except pygame.error as e:
            print(f"Error loading bird frames: {e}")
            return None

    def _apply_bird_type_attributes(self):
        if self.bird_type == 'red':
            self.horizontal_speed = 0.8
            self.gravity = 0.25
            self.flap_strength = -6
        elif self.bird_type == 'yellow':
            self.horizontal_speed = 0
            self.gravity = 0.35
            self.flap_strength = -8
        elif self.bird_type == 'blue':
            self.horizontal_speed = 0
            self.gravity = 0.25
            self.flap_strength = -6

    def update(self):
        if self.frames and len(self.frames) > 1:
            self.animation_timer += self.animation_speed
            if self.animation_timer >= 1:
                self.frame_index = (self.frame_index + 1) % len(self.frames)
                self.image = self.frames[self.frame_index]
                self.animation_timer = 0
        
        self.velocity += self.gravity
        self.rect.y += int(self.velocity)
        
        if self.rect.x < 50:
            self.rect.x += 1
        elif self.horizontal_speed != 0:
            self.rect.x += int(self.horizontal_speed)

        if self.rect.top < 0:
            self.rect.top = 0
            self.velocity = 0

    def flap(self, game_instance):
        if game_instance.game_state == 'game_active':
            self.velocity = self.flap_strength
            sound_flap.play()

    def draw(self, surface):
        surface.blit(self.image, self.rect)

# Pipe class
class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, position, current_horizontal_speed, is_horizontal_mover=False, horizontal_speed=0, horizontal_range=0, inverted=False):
        super().__init__()
        self.image = pipe_image
        self.pipe_type = position
        pipe_width = 52
        pipe_height = 320

        if self.image is None:
            self.image = pygame.Surface([pipe_width, pipe_height])
            self.image.fill((0, 255, 0))
        else:
            pipe_width = self.image.get_width()
            pipe_height = self.image.get_height()

        self.passed = False
        self.rect = self.image.get_rect()

        # Store initial position for horizontal range calculation
        self.initial_x = x
        self.is_horizontal_mover = is_horizontal_mover
        self.horizontal_speed = horizontal_speed
        self.horizontal_range = horizontal_range
        self.moving_forward = random.choice([True, False]) # Start moving forward or backward randomly

        if position == 1:
            if inverted:
                 self.image = pygame.transform.flip(self.image, False, True)
            self.rect.bottomleft = (x, y - pipe_gap_size // 2)
        elif position == -1:
            if not inverted:
                pass
            self.rect.topleft = (x, y + pipe_gap_size // 2)

        # Store the current horizontal speed (used for reference, not updated here)
        self.current_horizontal_speed = current_horizontal_speed

    def update(self, current_horizontal_speed):
        # Update base horizontal position
        self.rect.x -= current_horizontal_speed

        # Update additional horizontal movement if it's a horizontal mover
        if self.is_horizontal_mover and self.horizontal_range > 0:
            if self.moving_forward:
                self.rect.x += self.horizontal_speed
                # Check if reached forward limit of range
                if self.rect.x >= self.initial_x + self.horizontal_range:
                    self.moving_forward = False
            else:
                self.rect.x -= self.horizontal_speed
                # Check if reached backward limit of range
                if self.rect.x <= self.initial_x - self.horizontal_range:
                    self.moving_forward = True

        if self.rect.right < 0:
            self.kill()

# Coin class
class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        
        self.frames = coin_frames
        self.frame_index = 0
        self.animation_speed = 0.2
        self.animation_timer = 0

        if self.frames:
            self.image = self.frames[self.frame_index]
            self.rect = self.image.get_rect(center=(x, y))
        else:
            self.image = pygame.Surface([coin_frame_width, coin_frame_height])
            self.image.fill((255, 223, 0))
            self.rect = self.image.get_rect(center=(x, y))

    def update(self, current_horizontal_speed):
        # Animate coin
        if self.frames and len(self.frames) > 1:
            self.animation_timer += self.animation_speed
            if self.animation_timer >= 1:
                self.frame_index = (self.frame_index + 1) % len(self.frames)
                self.image = self.frames[self.frame_index]
                self.animation_timer = 0

        # Move coin to the left using current_horizontal_speed
        self.rect.x -= current_horizontal_speed
        if self.rect.right < 0:
            self.kill()

# --- Game Class Refactor with Difficulty Modifier, Vertical Pipes, and PowerUps ---
class Game:
    def __init__(self):
        # Game state variables
        self.game_state = 'start_screen'
        self.selected_bird_type = 'blue'
        self.score = 0
        self.high_score = self.load_high_score()
        self.coin_count = 0
        self.pipes_passed_count = 0
        self.pipe_move_speed = 2.0
        self.pipe_spawn_interval = 1800
        self.difficulty_stage = 0
        self.base_horizontal_pipe_speed = 1.0
        self.horizontal_pipe_speed_increase = 0.2
        self.base_pipe_horizontal_range = 30
        self.pipe_horizontal_range_increase = 5

        # Game objects and groups
        self.bird_manager = BirdManager()
        self.bird = Bird(self.selected_bird_type)
        self.pipes = pygame.sprite.Group()
        self.coins = pygame.sprite.Group()
        self.all_sprites = pygame.sprite.Group()
        self.all_sprites.add(self.bird)

        # Base position
        self.base_x = 0
        self.base_y = screen_height - 112  # Adjust this value based on your base image height

        # Background scroll
        self.background_x = 0

    def load_high_score(self):
        try:
            with open(high_score_file, 'r') as f:
                score_val = int(f.read())
                return score_val
        except (IOError, ValueError):
            return 0

    def save_high_score(self):
        try:
            with open(high_score_file, 'w') as f:
                f.write(str(int(self.high_score)))
        except IOError:
            print("Error saving high score")

    def display_score(self):
        if self.game_state == 'game_active':
            score_surface = font.render(str(int(self.score)), True, (255, 255, 255))
            score_rect = score_surface.get_rect(center=(screen_width // 2, UI_PADDING + 20))
            screen.blit(score_surface, score_rect)
            
            coin_surface = small_font.render(f'Coins: {self.coin_count}', True, (255, 255, 0))
            coin_rect = coin_surface.get_rect(topleft=(UI_PADDING, UI_PADDING))
            screen.blit(coin_surface, coin_rect)
        
        elif self.game_state == 'game_over':
            if game_over_image:
                game_over_rect = game_over_image.get_rect(center=(screen_width // 2, screen_height // 2 - 80))
                screen.blit(game_over_image, game_over_rect)

            score_surface = font.render(f'Score: {int(self.score)}', True, (255, 255, 255))
            score_rect = score_surface.get_rect(center=(screen_width // 2, screen_height // 2))
            screen.blit(score_surface, score_rect)

            high_score_surface = font.render(f'High Score: {int(self.high_score)}', True, (255, 255, 255))
            high_score_rect = high_score_surface.get_rect(center=(screen_width // 2, screen_height // 2 + UI_SPACING))
            screen.blit(high_score_surface, high_score_rect)

            restart_surface = font.render('Press R to Restart', True, (255, 255, 255))
            restart_rect = restart_surface.get_rect(center=(screen_width // 2, screen_height // 2 + UI_SPACING * 2))
            screen.blit(restart_surface, restart_rect)

            back_to_select_surface = font.render('Press B for Bird Select', True, (255, 255, 255))
            back_to_select_rect = back_to_select_surface.get_rect(center=(screen_width // 2, screen_height // 2 + UI_SPACING * 3))
            screen.blit(back_to_select_surface, back_to_select_rect)
        
        elif self.game_state == 'start_screen':
            if message_image:
                message_rect = message_image.get_rect(center=(screen_width // 2, screen_height // 2 - 50))
                screen.blit(message_image, message_rect)
            else:
                start_surface = font.render('Press Space to Start', True, (255, 255, 255))
                start_rect = start_surface.get_rect(center=(screen_width // 2, screen_height // 2))
                screen.blit(start_surface, start_rect)

            high_score_display_surface = font.render(f'High Score: {int(self.high_score)}', True, (255, 255, 255))
            high_score_display_rect = high_score_display_surface.get_rect(center=(screen_width // 2, screen_height // 2 + UI_SPACING))
            screen.blit(high_score_display_surface, high_score_display_rect)
        
        elif self.game_state == 'bird_select':
            overlay = pygame.Surface((screen_width, screen_height))
            overlay.fill((0, 0, 0))
            overlay.set_alpha(128)
            screen.blit(overlay, (0, 0))

            title_surface = font.render('Select Bird', True, (255, 255, 0))
            title_rect = title_surface.get_rect(center=(screen_width // 2, UI_PADDING + 20))
            screen.blit(title_surface, title_rect)

            y_offset = UI_PADDING + 80
            available_birds = self.bird_manager.get_available_birds()
            for i, bird_type in enumerate(available_birds):
                box_height = 60
                box_rect = pygame.Rect(UI_PADDING, y_offset + i * (box_height + 10) - (box_height // 2), screen_width - UI_PADDING * 2, box_height)
                if bird_type == self.selected_bird_type:
                    pygame.draw.rect(screen, (255, 255, 0), box_rect, 2)
                else:
                    pygame.draw.rect(screen, (255, 255, 255), box_rect, 1)

                text_y_name = y_offset + i * (box_height + 10) - 10
                text_y_desc = y_offset + i * (box_height + 10) + 10

                if self.bird_manager.is_bird_unlocked(bird_type):
                    bird_text = f"{bird_type.capitalize()} Bird"
                    if bird_type == self.selected_bird_type:
                        bird_text += " ✓"
                    bird_surface = small_font.render(bird_text, True, (255, 255, 255))
                    bird_rect = bird_surface.get_rect(center=(screen_width // 2, text_y_name))
                    screen.blit(bird_surface, bird_rect)

                    achievement_info = self.bird_manager.get_bird_achievement_info(bird_type)
                    if achievement_info and 'description' in achievement_info:
                        desc_surface = small_font.render(achievement_info['description'], True, (180, 180, 180))
                        desc_rect = desc_surface.get_rect(center=(screen_width // 2, text_y_desc))
                        screen.blit(desc_surface, desc_rect)
                else:
                    achievement = self.bird_manager.get_bird_achievement_info(bird_type)
                    if achievement:
                        lock_text = f"Locked: {achievement['description']}"
                        lock_surface = small_font.render(lock_text, True, (128, 128, 128))
                        lock_rect = lock_surface.get_rect(center=(screen_width // 2, text_y_name))
                        screen.blit(lock_surface, lock_rect)

            preview_bird = Bird(self.selected_bird_type)
            preview_bird.rect.center = (screen_width // 2, screen_height - 100)
            preview_bird.draw(screen)

            nav_surface = small_font.render('↑↓ to select, Space to choose', True, (200, 200, 200))
            nav_rect = nav_surface.get_rect(center=(screen_width // 2, screen_height - UI_PADDING - 30))
            screen.blit(nav_surface, nav_rect)

            select_surface = small_font.render('Click to Play', True, (255, 255, 255))
            select_rect = select_surface.get_rect(center=(screen_width // 2, screen_height - UI_PADDING))
            screen.blit(select_surface, select_rect)

    def reset_game(self):
        if self.score > self.high_score:
            self.high_score = self.score
            self.save_high_score()
            self.bird_manager.update_score(self.selected_bird_type, self.score)
        
        self.score = 0
        self.coin_count = 0
        self.pipes_passed_count = 0
        self.pipe_move_speed = 2.0
        self.pipe_spawn_interval = 1800
        self.difficulty_stage = 0
        self.bird = Bird(self.selected_bird_type)
        self.bird.rect.center = (50, screen_height // 2)
        self.bird.velocity = 0
        self.pipes.empty()
        self.coins.empty()
        self.all_sprites.empty()
        self.all_sprites.add(self.bird)
        self.game_state = 'game_active'
        self.create_pipe_pair()
        
        if 'pygame' in sys.modules and hasattr(pygame.mixer, 'music'):
            pygame.mixer.music.play(-1)

    def create_pipe_pair(self):
        min_y = 100
        max_y = screen_height - 100 - pipe_gap_size
        if min_y >= max_y:
            pipe_gap_center_y = screen_height // 2
        else:
            pipe_gap_center_y = random.randint(min_y, max_y)

        if pipe_image:
            current_pipe_width = pipe_image.get_width()
        else:
            current_pipe_width = 52

        # Check for overlap with existing pipes
        new_pipe_x = screen_width
        for pipe in self.pipes:
            # If there's a pipe within 100 pixels of the new pipe's position, adjust the new pipe's position
            if abs(pipe.rect.x - new_pipe_x) < 100:
                new_pipe_x = pipe.rect.x + 100

        # Determine horizontal movement parameters based on difficulty stage
        is_horizontal_mover = False
        horizontal_speed = 0
        horizontal_range = 0

        # Introduce horizontal movement after the first difficulty increase (20 pipes passed)
        if self.difficulty_stage > 0:
            # Calculate movement probability, capped at 20%
            movement_probability = min(0.2 * self.difficulty_stage, 0.2)  # Cap at 20%
            
            # Increase chance of horizontal movers and their parameters with difficulty
            if random.random() < movement_probability:
                is_horizontal_mover = True
                horizontal_speed = self.base_horizontal_pipe_speed + self.difficulty_stage * self.horizontal_pipe_speed_increase
                horizontal_range = self.base_pipe_horizontal_range + self.difficulty_stage * self.pipe_horizontal_range_increase
                # Cap the horizontal range to prevent the gap from closing too much
                max_horizontal_range = 60 # Define a maximum allowed horizontal range
                horizontal_range = min(horizontal_range, max_horizontal_range)
            
            # Decide which pipe(s) move horizontally
            if is_horizontal_mover:
                move_both = random.random() < 0.5 # 50% chance both move
                if move_both:
                    # Pass inverted=True for top pipe, False for bottom
                    top_pipe = Pipe(new_pipe_x, pipe_gap_center_y, 1, self.pipe_move_speed, is_horizontal_mover=True, horizontal_speed=horizontal_speed, horizontal_range=horizontal_range, inverted=True)
                    bottom_pipe = Pipe(new_pipe_x, pipe_gap_center_y, -1, self.pipe_move_speed, is_horizontal_mover=True, horizontal_speed=horizontal_speed, horizontal_range=horizontal_range, inverted=False)
                else:
                    # Randomly choose one pipe to be a horizontal mover
                    move_top = random.choice([True, False])
                    if move_top:
                        # Top pipe moves horizontally, bottom is static
                        top_pipe = Pipe(new_pipe_x, pipe_gap_center_y, 1, self.pipe_move_speed, is_horizontal_mover=True, horizontal_speed=horizontal_speed, horizontal_range=horizontal_range, inverted=True)
                        bottom_pipe = Pipe(new_pipe_x, pipe_gap_center_y, -1, self.pipe_move_speed, is_horizontal_mover=False, horizontal_speed=0, horizontal_range=0, inverted=False)
                    else:
                        # Bottom pipe moves horizontally, top is static
                        top_pipe = Pipe(new_pipe_x, pipe_gap_center_y, 1, self.pipe_move_speed, is_horizontal_mover=False, horizontal_speed=0, horizontal_range=0, inverted=True)
                        bottom_pipe = Pipe(new_pipe_x, pipe_gap_center_y, -1, self.pipe_move_speed, is_horizontal_mover=True, horizontal_speed=horizontal_speed, horizontal_range=horizontal_range, inverted=False)
            else:
                # No horizontal movement for this pair
                top_pipe = Pipe(new_pipe_x, pipe_gap_center_y, 1, self.pipe_move_speed, is_horizontal_mover=False, horizontal_speed=0, horizontal_range=0, inverted=True)
                bottom_pipe = Pipe(new_pipe_x, pipe_gap_center_y, -1, self.pipe_move_speed, is_horizontal_mover=False, horizontal_speed=0, horizontal_range=0, inverted=False)
        else:
            # No horizontal movement at the start of the game
            top_pipe = Pipe(new_pipe_x, pipe_gap_center_y, 1, self.pipe_move_speed, is_horizontal_mover=False, horizontal_speed=0, horizontal_range=0, inverted=True)
            bottom_pipe = Pipe(new_pipe_x, pipe_gap_center_y, -1, self.pipe_move_speed, is_horizontal_mover=False, horizontal_speed=0, horizontal_range=0, inverted=False)

        # Extend bottom pipe beyond screen
        if pipe_image:
            bottom_pipe.rect.height = screen_height * 2  # Make bottom pipe twice screen height
        else:
            bottom_pipe.rect.height = screen_height * 2

        self.pipes.add(top_pipe)
        self.pipes.add(bottom_pipe)
        self.all_sprites.add(top_pipe)
        self.all_sprites.add(bottom_pipe)

        # Add a coin randomly with a pipe pair
        if random.random() < 0.5:  # 50% chance to spawn a coin
            coin_x = new_pipe_x + current_pipe_width + 20
            # Random position between pipes or in the gap
            if random.random() < 0.5:  # 50% chance to be in the gap
                # Random height within the pipe gap, with some margin from the edges
                min_coin_y = pipe_gap_center_y - (pipe_gap_size // 2) + 30  # 30 pixels from top pipe
                max_coin_y = pipe_gap_center_y + (pipe_gap_size // 2) - 30  # 30 pixels from bottom pipe
                coin_y = random.randint(min_coin_y, max_coin_y)
            else:  # 50% chance to be between pipes
                # Random position between the pipes
                coin_y = random.randint(50, screen_height - 50)  # Keep away from screen edges
            coin = Coin(coin_x, coin_y)
            self.coins.add(coin)
            self.all_sprites.add(coin)

    def run(self):
        running = True
        pygame.time.set_timer(PIPE_SPAWN_EVENT, self.pipe_spawn_interval)

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        if self.game_state == 'start_screen':
                            self.game_state = 'bird_select'
                        elif self.game_state == 'bird_select':
                            # Start game from bird select
                            self.start_game() # Call a new method to start the game
                        elif self.game_state == 'game_active':
                            self.bird.flap(self)
                    elif event.key == pygame.K_r and self.game_state == 'game_over':
                        # Restart game from game over
                        self.start_game() # Call the start game method to reset and begin
                        sound_swoosh.play()
                    elif event.key == pygame.K_SPACE and self.game_state == 'game_over':
                        # Restart game from game over with space bar
                        self.start_game()
                        sound_swoosh.play()
                    elif event.key == pygame.K_b and self.game_state == 'game_over':
                        self.game_state = 'bird_select'
                        self.bird = Bird(self.selected_bird_type)
                        self.bird.rect.center = (screen_width // 2, screen_height // 2)
                        # Reset difficulty parameters when going back to bird select from game over
                        self.pipes_passed_count = 0
                        self.pipe_move_speed = 2.0
                        self.difficulty_stage = 0

                    elif self.game_state == 'bird_select':
                        available_birds = self.bird_manager.get_available_birds()
                        current_index = available_birds.index(self.selected_bird_type)
                        if event.key == pygame.K_UP:
                            self.selected_bird_type = available_birds[(current_index - 1) % len(available_birds)]
                        elif event.key == pygame.K_DOWN:
                            self.selected_bird_type = available_birds[(current_index + 1) % len(available_birds)]
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.game_state == 'game_active':
                        self.bird.flap(self)
                    elif self.game_state == 'start_screen':
                         self.game_state = 'bird_select'
                    elif self.game_state == 'bird_select':
                        mouse_pos = pygame.mouse.get_pos()
                        y_offset_start = UI_PADDING + 80
                        box_height = 60
                        available_birds = self.bird_manager.get_available_birds()
                        for i, bird_type in enumerate(available_birds):
                            box_y_start = y_offset_start + i * (box_height + 10) - (box_height // 2)
                            box_y_end = box_y_start + box_height
                            if self.bird_manager.is_bird_unlocked(bird_type):
                                if box_y_start <= mouse_pos[1] <= box_y_end:
                                    self.selected_bird_type = bird_type
                                    # Start game on click from bird select
                                    self.start_game() # Call the start game method
                                    sound_swoosh.play()
                                    break

                if event.type == PIPE_SPAWN_EVENT and self.game_state == 'game_active':
                    self.create_pipe_pair()

            if self.game_state == 'game_active':
                # Update base position
                self.base_x -= self.pipe_move_speed
                if self.base_x <= -screen_width:
                    self.base_x = 0

                # Update pipes and coins with the current pipe_move_speed
                self.pipes.update(self.pipe_move_speed)
                self.coins.update(self.pipe_move_speed)
                self.bird.update()

                collected_coins = pygame.sprite.spritecollide(self.bird, self.coins, True)
                self.coin_count += len(collected_coins)
                if len(collected_coins) > 0:
                    sound_point.play()

                if pygame.sprite.spritecollide(self.bird, self.pipes, False) or self.bird.rect.bottom >= screen_height or self.bird.rect.top <= 0:
                    self.game_state = 'game_over'
                    sound_hit.play()
                    sound_die.play()
                    if 'pygame' in sys.modules and hasattr(pygame.mixer, 'music'):
                        pygame.mixer.music.stop()
                    if self.score > self.high_score:
                        self.high_score = self.score
                        self.save_high_score()
                        self.bird_manager.update_score(self.selected_bird_type, self.score)

                for pipe in self.pipes:
                    if not pipe.passed and pipe.rect.right < self.bird.rect.left:
                        pipe.passed = True
                        if pipe.pipe_type == -1:
                            self.score += 1
                            self.pipes_passed_count += 1
                            if self.pipes_passed_count > 0 and self.pipes_passed_count % 20 == 0:
                                self.pipe_move_speed *= 1.05
                                self.difficulty_stage += 1
                                print(f"Difficulty Stage: {self.difficulty_stage}, Pipe Speed: {self.pipe_move_speed}")

            # Draw everything
            if background_image:
                self.background_x -= background_scroll_speed
                if self.background_x <= -screen_width:
                    self.background_x = 0
                screen.blit(background_image, (self.background_x, 0))
                screen.blit(background_image, (self.background_x + screen_width, 0))
            else:
                screen.fill((135, 206, 235))

            # Only draw game sprites when game is active
            if self.game_state == 'game_active':
                self.all_sprites.draw(screen)

            # Draw base
            if base_image:
                screen.blit(base_image, (self.base_x, self.base_y))
                screen.blit(base_image, (self.base_x + screen_width, self.base_y))

            self.display_score()
            pygame.display.flip()
            clock.tick(60)  # Single frame rate limit at the end of the loop

        pygame.quit()
        sys.exit()

    def start_game(self):
        self.game_state = 'game_active'
        if 'pygame' in sys.modules and hasattr(pygame.mixer, 'music') and not pygame.mixer.music.get_busy():
            pygame.mixer.music.play(-1)
        self.score = 0
        self.coin_count = 0
        self.pipes_passed_count = 0
        self.pipe_move_speed = 2.0
        self.difficulty_stage = 0

        self.pipes.empty()
        self.coins.empty()
        self.bird = Bird(self.selected_bird_type)
        self.bird.rect.center = (50, screen_height // 2)
        self.bird.velocity = 0
        self.all_sprites.empty()
        self.all_sprites.add(self.bird)
        self.create_pipe_pair()

# Run the game
if __name__ == '__main__':
    game = Game()
    game.run() 