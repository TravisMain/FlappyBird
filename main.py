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
# pipe_move_speed, pipe_spawn_interval are managed by Game instance or are constants.
# pipe_gap_size is an instance variable in Game class.

# High Score File
# high_score_file is an instance variable in Game class.

# Initialize bird manager
# bird_manager is an instance variable in Game class.

# Game state variables are managed by Game instance.

# UI Settings, Font setup, Background scroll speed, PIPE_SPAWN_EVENT
# All these are now instance variables in the Game class.


# Global high_score loading is removed; Game class handles this.

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
    num_coin_frames = coin_sprite_sheet.get_width() // coin_frame_width
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
            self.gravity = 0.15
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

    def flap(self, game_state):
        # Access game_state via the passed parameter
        if game_state == 'game_active':
            self.velocity = self.flap_strength
            sound_flap.play()

    def draw(self, surface):
        surface.blit(self.image, self.rect)

# Pipe class
class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, position, inverted=False, pipe_gap_size=150): # Added pipe_gap_size arg
        super().__init__()
        self.image = pipe_image # pipe_image is a global asset, acceptable
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

        if position == 1: # Top pipe
            if inverted: # Should always be true for top pipe as asset points down
                 self.image = pygame.transform.flip(self.image, False, True)
            self.rect.bottomleft = (x, y - pipe_gap_size // 2)
        elif position == -1: # Bottom pipe
            # Asset points down, so no flip needed for bottom pipe
            self.rect.topleft = (x, y + pipe_gap_size // 2)

    def update(self, current_speed):
        self.rect.x -= current_speed
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

    def update(self, current_speed):
        if self.frames and len(self.frames) > 1:
            self.animation_timer += self.animation_speed
            if self.animation_timer >= 1:
                self.frame_index = (self.frame_index + 1) % len(self.frames)
                self.image = self.frames[self.frame_index]
                self.animation_timer = 0

        self.rect.x -= current_speed
        if self.rect.right < 0:
            self.kill()

# Background scroll - This is managed by self.background_x in Game class
# background_x = 0

# The global display_score function is removed. Game.display_score() is used instead.
# The global load_high_score and save_high_score functions are also removed.

# --- Game Class Refactor with Difficulty Modifier ---
class Game:
    def __init__(self):
        # Initialize Pygame specifics that were global
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.PIPE_SPAWN_EVENT = pygame.USEREVENT 
        
        # UI and Game settings
        self.UI_PADDING = 20
        self.UI_SPACING = 30
        self.background_scroll_speed = 0.5
        self.pipe_gap_size = 150 # Added from global
        self.high_score_file = "highscore.txt" # Added from global

        # Game state variables
        self.game_state = 'start_screen'
        self.selected_bird_type = 'blue' 
        self.score = 0
        self.high_score = self._load_high_score_internal() 
        self.coin_count = 0
        self.pipes_passed_count = 0
        self.pipe_move_speed = 2.0 
        self.pipe_spawn_interval = 1800 

        # Game objects and groups
        self.bird_manager = BirdManager()
        self.bird = Bird(self.selected_bird_type) 
        self.pipes = pygame.sprite.Group()
        self.coins = pygame.sprite.Group()
        self.all_sprites = pygame.sprite.Group()
        self.all_sprites.add(self.bird)

        # Background scroll
        self.background_x = 0
        
        # Critical asset error flag and message
        self.critical_asset_error = False
        self.error_message_text = ""

        # Check for critical assets after loading attempts (example: pipe_image)
        # Note: pipe_image is loaded globally. We check its state here.
        if pipe_image is None:
            self.critical_asset_error = True
            self.error_message_text = "Error: Pipe image missing. Please reinstall."
            print("CRITICAL ERROR: Pipe image (pipe-green.png) failed to load.")


    def _load_high_score_internal(self): # Renamed from global load_high_score
        try:
            # Use self.high_score_file which is now an instance attribute
            with open(self.high_score_file, 'r') as f:
                score_val = int(f.read())
                return score_val
        except (IOError, ValueError):
            return 0

    def _save_high_score_internal(self): # Renamed from global save_high_score
        try:
            # Use self.high_score_file which is now an instance attribute
            with open(self.high_score_file, 'w') as f:
                f.write(str(int(self.high_score)))
        except IOError:
            print("Error saving high score")

    def display_score(self): # Uses self.font, self.small_font, self.UI_PADDING, self.UI_SPACING now
        if self.game_state == 'game_active':
            score_surface = self.font.render(str(int(self.score)), True, (255, 255, 255))
            score_rect = score_surface.get_rect(center=(screen_width // 2, self.UI_PADDING + 20))
            screen.blit(score_surface, score_rect)
            
            coin_surface = self.small_font.render(f'Coins: {self.coin_count}', True, (255, 255, 0))
            coin_rect = coin_surface.get_rect(topleft=(self.UI_PADDING, self.UI_PADDING))
            screen.blit(coin_surface, coin_rect)
        
        elif self.game_state == 'game_over':
            if game_over_image: # Global asset
                game_over_rect = game_over_image.get_rect(center=(screen_width // 2, screen_height // 2 - 80))
                screen.blit(game_over_image, game_over_rect)

            score_surface = self.font.render(f'Score: {int(self.score)}', True, (255, 255, 255))
            score_rect = score_surface.get_rect(center=(screen_width // 2, screen_height // 2))
            screen.blit(score_surface, score_rect)

            high_score_surface = self.font.render(f'High Score: {int(self.high_score)}', True, (255, 255, 255))
            high_score_rect = high_score_surface.get_rect(center=(screen_width // 2, screen_height // 2 + self.UI_SPACING))
            screen.blit(high_score_surface, high_score_rect)

            restart_surface = self.font.render('Press R to Restart', True, (255, 255, 255))
            restart_rect = restart_surface.get_rect(center=(screen_width // 2, screen_height // 2 + self.UI_SPACING * 2))
            screen.blit(restart_surface, restart_rect)

            back_to_select_surface = self.font.render('Press B for Bird Select', True, (255, 255, 255))
            back_to_select_rect = back_to_select_surface.get_rect(center=(screen_width // 2, screen_height // 2 + self.UI_SPACING * 3))
            screen.blit(back_to_select_surface, back_to_select_rect)
        
        elif self.game_state == 'start_screen':
            if message_image: # Global asset
                message_rect = message_image.get_rect(center=(screen_width // 2, screen_height // 2 - 50))
                screen.blit(message_image, message_rect)
            else:
                start_surface = self.font.render('Press Space to Start', True, (255, 255, 255))
                start_rect = start_surface.get_rect(center=(screen_width // 2, screen_height // 2))
                screen.blit(start_surface, start_rect)

            high_score_display_surface = self.font.render(f'High Score: {int(self.high_score)}', True, (255, 255, 255))
            high_score_display_rect = high_score_display_surface.get_rect(center=(screen_width // 2, screen_height // 2 + self.UI_SPACING))
            screen.blit(high_score_display_surface, high_score_display_rect)
        
        elif self.game_state == 'bird_select':
            overlay = pygame.Surface((screen_width, screen_height))
            overlay.fill((0, 0, 0))
            overlay.set_alpha(128) 
            screen.blit(overlay, (0,0))

            title_surface = self.font.render('Select Bird', True, (255, 255, 0)) 
            title_rect = title_surface.get_rect(center=(screen_width // 2, self.UI_PADDING + 20))
            screen.blit(title_surface, title_rect)

            y_offset = self.UI_PADDING + 80 
            available_birds = self.bird_manager.get_available_birds()
            for i, bird_type_iter in enumerate(available_birds):
                box_height = 60 
                box_rect = pygame.Rect(self.UI_PADDING, y_offset + i * (box_height + 10) - (box_height // 2) , screen_width - self.UI_PADDING*2, box_height)
                if bird_type_iter == self.selected_bird_type:
                    pygame.draw.rect(screen, (255,255,0), box_rect, 2) 
                else:
                    pygame.draw.rect(screen, (255,255,255), box_rect, 1) 
                
                text_y_name = y_offset + i * (box_height + 10) -10
                text_y_desc = y_offset + i * (box_height + 10) +10

                if self.bird_manager.is_bird_unlocked(bird_type_iter):
                    bird_text = f"{bird_type_iter.capitalize()} Bird"
                    if bird_type_iter == self.selected_bird_type:
                        bird_text += " ✓" 
                    bird_surface = self.small_font.render(bird_text, True, (255, 255, 255))
                    bird_rect = bird_surface.get_rect(center=(screen_width // 2, text_y_name))
                    screen.blit(bird_surface, bird_rect)

                    achievement_info = self.bird_manager.get_bird_achievement_info(bird_type_iter)
                    if achievement_info and 'description' in achievement_info:
                        desc_surface = self.small_font.render(achievement_info['description'], True, (180, 180, 180)) 
                        desc_rect = desc_surface.get_rect(center=(screen_width // 2, text_y_desc))
                        screen.blit(desc_surface, desc_rect)
                else: 
                    achievement = self.bird_manager.get_bird_achievement_info(bird_type_iter)
                    if achievement:
                        lock_text = f"Locked: {achievement['description']}"
                        lock_surface = self.small_font.render(lock_text, True, (128,128,128)) 
                        lock_rect = lock_surface.get_rect(center=(screen_width // 2, text_y_name))
                        screen.blit(lock_surface, lock_rect)

            preview_bird = Bird(self.selected_bird_type) 
            preview_bird.rect.center = (screen_width // 2, screen_height - 100)
            preview_bird.draw(screen) 

            nav_surface = self.small_font.render('↑↓ to select, Space to choose', True, (200, 200, 200))
            nav_rect = nav_surface.get_rect(center=(screen_width // 2, screen_height - self.UI_PADDING - 30))
            screen.blit(nav_surface, nav_rect)

            select_surface = self.small_font.render('Click to Play', True, (255, 255, 255))
            select_rect = select_surface.get_rect(center=(screen_width // 2, screen_height - self.UI_PADDING))
            screen.blit(select_surface, select_rect)

    def reset_game(self):
        if self.score > self.high_score:
            self.high_score = self.score
            self._save_high_score_internal() # Use internal method
            self.bird_manager.update_score(self.selected_bird_type, self.score)
        
        self.score = 0
        self.coin_count = 0
        self.pipes_passed_count = 0
        self.pipe_move_speed = 2.0 # Reset pipe speed
        self.pipe_spawn_interval = 1800 # Reset pipe_spawn_interval
        self.bird = Bird(self.selected_bird_type)
        self.bird.rect.center = (50, screen_height // 2)
        self.bird.velocity = 0
        self.pipes.empty()
        self.coins.empty()
        self.all_sprites.empty()
        self.all_sprites.add(self.bird)
        # self.game_state = 'game_active' # This will be set in _start_game_session
        # self.create_pipe_pair() # This will be called in _start_game_session
        
        # Start music if needed, will be handled in _start_game_session
        # if 'pygame' in sys.modules and hasattr(pygame.mixer, 'music'):
        #     pygame.mixer.music.play(-1)

    def _start_game_session(self):
        """Initializes and starts a new game session."""
        self.game_state = 'game_active'
        sound_swoosh.play()

        if 'pygame' in sys.modules and hasattr(pygame.mixer, 'music') and not pygame.mixer.music.get_busy():
            pygame.mixer.music.play(-1)

        self.score = 0
        self.coin_count = 0
        self.pipes_passed_count = 0
        self.pipe_move_speed = 2.0  # Initial pipe move speed
        self.pipe_spawn_interval = 1800 # Initial pipe spawn interval
        pygame.time.set_timer(self.PIPE_SPAWN_EVENT, self.pipe_spawn_interval) # Use self.PIPE_SPAWN_EVENT

        self.pipes.empty()
        self.coins.empty()
        
        self.bird = Bird(self.selected_bird_type)
        self.bird.rect.center = (50, screen_height // 2)
        self.bird.velocity = 0
        
        self.all_sprites.empty()
        self.all_sprites.add(self.bird)
        
        self.create_pipe_pair()

    def _draw_screen(self):
        """Handles all drawing operations for the current game state."""

        if self.critical_asset_error:
            screen.fill((50, 0, 0)) # Dark red screen for critical error
            error_surface = self.font.render(self.error_message_text, True, (255, 255, 255))
            error_rect = error_surface.get_rect(center=(screen_width // 2, screen_height // 2))
            screen.blit(error_surface, error_rect)
            # Additional instructions for the user could be added here
            instructions_surface = self.small_font.render("Please check console for details or reinstall.", True, (200, 200, 200))
            instructions_rect = instructions_surface.get_rect(center=(screen_width // 2, screen_height // 2 + 40))
            screen.blit(instructions_surface, instructions_rect)
            return # Skip other drawing if critical error

        # Draw background
        if background_image: # Global asset
            self.background_x -= self.background_scroll_speed
            if self.background_x <= -screen_width:
                self.background_x = 0
            screen.blit(background_image, (self.background_x, 0))
            screen.blit(background_image, (self.background_x + screen_width, 0))
        elif self.game_state == 'game_over': # Specific background for game_over if no image
            screen.fill((0, 0, 0)) # Black screen
        else:
            screen.fill((135, 206, 235)) # Default sky color for other states

        # Draw game-specific sprites based on state
        if self.game_state == 'game_active':
            self.all_sprites.draw(screen)
        elif self.game_state == 'start_screen':
            if hasattr(self, 'bird'): # Ensure bird exists (it's created in __init__)
                self.bird.draw(screen) # Draw the main bird
        # Note: 'bird_select' preview bird is handled within display_score.
        # 'game_over' doesn't typically draw active game sprites beyond what display_score might show.

        # Draw UI elements (scores, messages, etc.) on top
        self.display_score()

    def create_pipe_pair(self):
        # min_y and max_y define the vertical range for the center of the pipe gap.
        # The padding of 100 ensures the gap isn't too close to the screen edges.
        min_y = 100 
        max_y = screen_height - 100 - self.pipe_gap_size # Use self.pipe_gap_size

        # If the valid range for the gap center is invalid (e.g., due to extreme pipe_gap_size or small screen_height),
        # default to placing the gap in the middle of the screen.
        if min_y >= max_y:
            pipe_gap_center_y = screen_height // 2
        else:
            pipe_gap_center_y = random.randint(min_y, max_y)

        if pipe_image: # Global asset
            current_pipe_width = pipe_image.get_width()
        else:
            current_pipe_width = 52

        # Pass self.pipe_gap_size to the Pipe constructor
        top_pipe = Pipe(screen_width, pipe_gap_center_y, 1, inverted=True, pipe_gap_size=self.pipe_gap_size)
        bottom_pipe = Pipe(screen_width, pipe_gap_center_y, -1, pipe_gap_size=self.pipe_gap_size)
        self.pipes.add(top_pipe)
        self.pipes.add(bottom_pipe)
        self.all_sprites.add(top_pipe)
        self.all_sprites.add(bottom_pipe)

        if random.random() < 0.5:
            coin_x = screen_width + current_pipe_width + 20
            coin_y = pipe_gap_center_y
            coin = Coin(coin_x, coin_y)
            self.coins.add(coin)
            self.all_sprites.add(coin)

    def run(self):
        running = True
        # Use self.PIPE_SPAWN_EVENT and self.pipe_spawn_interval
        pygame.time.set_timer(self.PIPE_SPAWN_EVENT, self.pipe_spawn_interval)

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        if self.game_state == 'start_screen':
                            self.game_state = 'bird_select'
                        elif self.game_state == 'bird_select':
                            self._start_game_session() 
                        elif self.game_state == 'game_active':
                            self.bird.flap(self.game_state)
                    elif event.key == pygame.K_r and self.game_state == 'game_over':
                        self.reset_game()
                        # sound_swoosh is played in _start_game_session via reset_game
                    elif event.key == pygame.K_b and self.game_state == 'game_over':
                        self.game_state = 'bird_select'
                        self.bird = Bird(self.selected_bird_type)
                        self.bird.rect.center = (screen_width // 2, screen_height // 2)
                    elif self.game_state == 'bird_select':
                        available_birds = self.bird_manager.get_available_birds()
                        current_index = available_birds.index(self.selected_bird_type)
                        if event.key == pygame.K_UP:
                            self.selected_bird_type = available_birds[(current_index - 1) % len(available_birds)]
                        elif event.key == pygame.K_DOWN:
                            self.selected_bird_type = available_birds[(current_index + 1) % len(available_birds)]
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.game_state == 'game_active':
                        self.bird.flap(self.game_state)
                    elif self.game_state == 'start_screen':
                         self.game_state = 'bird_select'
                    elif self.game_state == 'bird_select':
                        mouse_pos = pygame.mouse.get_pos()
                        y_offset_start = self.UI_PADDING + 80 # Use self.UI_PADDING
                        box_height = 60
                        available_birds = self.bird_manager.get_available_birds()
                        for i, bird_type_iter in enumerate(available_birds):
                            box_y_start = y_offset_start + i * (box_height + 10) - (box_height // 2)
                            box_y_end = box_y_start + box_height
                            if self.UI_PADDING <= mouse_pos[0] <= screen_width - self.UI_PADDING and \
                               box_y_start <= mouse_pos[1] <= box_y_end: # Use self.UI_PADDING
                                if self.bird_manager.is_bird_unlocked(bird_type_iter):
                                    self.selected_bird_type = bird_type_iter
                                    self._start_game_session() 
                                    break

                if event.type == self.PIPE_SPAWN_EVENT and self.game_state == 'game_active': # Use self.PIPE_SPAWN_EVENT
                    self.create_pipe_pair()

            if self.game_state == 'game_active':
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
                        self._save_high_score_internal() # Use internal method
                        self.bird_manager.update_score(self.selected_bird_type, self.score)

                for pipe_obj in self.pipes: # Renamed pipe to pipe_obj
                    if not pipe_obj.passed and pipe_obj.rect.right < self.bird.rect.left:
                        pipe_obj.passed = True
                        if pipe_obj.pipe_type == -1:
                            self.score += 1
                            self.pipes_passed_count += 1
                            if self.pipes_passed_count > 0 and self.pipes_passed_count % 20 == 0:
                                self.pipe_move_speed *= 1.05 
                                # print(f"Pipe speed increased to: {self.pipe_move_speed}") # Debug print removed

                if background_image: # Global asset
                    self.background_x -= self.background_scroll_speed # Use self.background_scroll_speed
                    if self.background_x <= -screen_width:
                        self.background_x = 0
                    screen.blit(background_image, (self.background_x, 0))
                    screen.blit(background_image, (self.background_x + screen_width, 0))
                else:
                    screen.fill((135, 206, 235))

                # Drawing is now handled by _draw_screen
                pass

            elif self.game_state == 'game_over':
                # Drawing is now handled by _draw_screen
                pass
            
            elif self.game_state == 'start_screen':
                # Drawing is now handled by _draw_screen
                pass

            elif self.game_state == 'bird_select':
                # Drawing is now handled by _draw_screen
                pass
            
            # Centralized drawing call
            self._draw_screen() 
            pygame.display.flip()
            clock.tick(60)

        pygame.quit()
        sys.exit()

# Run the game
if __name__ == '__main__':
    game = Game()
    game.run() 