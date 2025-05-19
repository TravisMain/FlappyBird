import pygame
import sys
import random
import os

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
pipe_move_speed = 3         # Speed at which pipes move left
pipe_spawn_interval = 1500  # Milliseconds between pipe spawns (e.g., 1200 for harder, 1800 for easier)
pipe_gap_size = 150         # Vertical gap between pipe pairs (e.g., 100 for harder, 200 for easier)

# High Score File
high_score_file = "highscore.txt"

# Function to load high score
def load_high_score():
    try:
        with open(high_score_file, 'r') as f:
            score_val = int(f.read())
            return score_val
    except (IOError, ValueError):
        return 0 # File not found or invalid content, default to 0

# Function to save high score
def save_high_score(score_to_save):
    try:
        with open(high_score_file, 'w') as f:
            f.write(str(score_to_save))
    except IOError:
        print(f"Error: Could not save high score to {high_score_file}")

# Load Sounds
try:
    sound_flap = pygame.mixer.Sound(resource_path('assets/audio/wing.ogg'))
    sound_point = pygame.mixer.Sound(resource_path('assets/audio/point.ogg'))
    sound_hit = pygame.mixer.Sound(resource_path('assets/audio/hit.ogg'))
    sound_die = pygame.mixer.Sound(resource_path('assets/audio/die.ogg'))
    sound_swoosh = pygame.mixer.Sound(resource_path('assets/audio/swoosh.ogg')) # Optional swoosh sound
except pygame.error as e:
    print(f"Error loading sound(s): {e}. Sound effects will be disabled.")
    # Create dummy sound objects if loading fails, so game doesn't crash
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

# Bird class
class Bird(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.frames = bird_frames
        self.frame_index = 0
        self.animation_speed = 0.15 # How fast the animation plays
        self.animation_timer = 0

        if self.frames:
            self.image = self.frames[self.frame_index]
        else: # Placeholder if no images loaded
            self.image = pygame.Surface([34, 24]) # Placeholder size
            self.image.fill((255, 255, 0)) # Yellow color for placeholder
            # Create a dummy frames list with the placeholder for consistency if needed elsewhere
            self.frames = [self.image, self.image, self.image]
        
        self.rect = self.image.get_rect(center=(50, screen_height // 2))
        self.velocity = 0
        self.gravity = 0.25 # Adjusted for a more flappy feel
        self.flap_strength = -6 # Adjusted for a more flappy feel

    def update(self):
        # Animate bird
        if self.frames and len(self.frames) > 1: # Only animate if multiple frames exist
            self.animation_timer += self.animation_speed
            if self.animation_timer >= 1:
                self.frame_index = (self.frame_index + 1) % len(self.frames)
                self.image = self.frames[self.frame_index]
                self.animation_timer = 0
        
        # Bird movement
        self.velocity += self.gravity
        self.rect.y += int(self.velocity) # Convert to int for pixel position

        # Keep bird on screen (optional, or handle as game over)
        if self.rect.top < 0:
            self.rect.top = 0
            self.velocity = 0
        # if self.rect.bottom > screen_height: # Game over if bird hits ground
        #     self.rect.bottom = screen_height
        #     self.velocity = 0


    def flap(self):
        if game_state == 'game_active': # Only allow flap if game is active
            self.velocity = self.flap_strength
            sound_flap.play()
            # sound_swoosh.play() # Optional: play swoosh on flap too

    def draw(self, surface):
        surface.blit(self.image, self.rect)

# Pipe class
class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, position, inverted=False):
        super().__init__()
        self.image = pipe_image
        self.pipe_type = position # Store the pipe type (1 for top, -1 for bottom)
        pipe_width = 52 # Default width if image not loaded
        pipe_height = 320 # Default height if image not loaded

        if self.image is None:
            self.image = pygame.Surface([pipe_width, pipe_height])
            self.image.fill((0, 255, 0)) # Green color for placeholder
        else:
            # If using an image, you might want to get its dimensions
            pipe_width = self.image.get_width()
            pipe_height = self.image.get_height()

        # Add a passed attribute for scoring
        self.passed = False

        self.rect = self.image.get_rect()

        # Position can be 1 (top pipe) or -1 (bottom pipe)
        if position == 1: # Top pipe
            if inverted:
                 self.image = pygame.transform.flip(self.image, False, True)
            self.rect.bottomleft = (x, y - pipe_gap_size // 2)
        elif position == -1: # Bottom pipe
            if not inverted: # Standard bottom pipe, no flip needed from typical sprite
                pass # image is already oriented correctly
            self.rect.topleft = (x, y + pipe_gap_size // 2)

    def update(self):
        self.rect.x -= pipe_move_speed # Move pipe to the left
        if self.rect.right < 0:
            self.kill() # Remove pipe when it goes off screen

# Game variables
score = 0
game_state = 'start_screen' # Initial state
font = pygame.font.Font(None, 36) # Default font, size 36
high_score = load_high_score() # Load high score at start

# Background scrolling variables
background_x = 0
background_scroll_speed = 1 # Slower than pipes for parallax effect

# Function to display score
def display_score(state):
    if state == 'game_active':
        score_surface = font.render(f'Score: {int(score)}', True, (255, 255, 255))
        score_rect = score_surface.get_rect(center=(screen_width // 2, 50))
        screen.blit(score_surface, score_rect)
    if state == 'game_over':
        # Display game_over_image if loaded
        if game_over_image:
            game_over_rect = game_over_image.get_rect(center=(screen_width // 2, screen_height // 2 - 60)) # Adjusted Y
            screen.blit(game_over_image, game_over_rect)
        else: # Fallback text if image not loaded
            game_over_text_surface = font.render('Game Over', True, (255, 0, 0))
            game_over_text_rect = game_over_text_surface.get_rect(center=(screen_width // 2, screen_height // 2 - 50))
            screen.blit(game_over_text_surface, game_over_text_rect)

        # Display scores below the game over image/text
        score_y_offset = screen_height // 2 + 0 # Adjusted Y
        if game_over_image:
            score_y_offset = game_over_rect.bottom + 30 # Position scores below the image
        
        score_surface = font.render(f'Score: {int(score)}', True, (255, 255, 255))
        score_rect = score_surface.get_rect(center=(screen_width // 2, score_y_offset))
        screen.blit(score_surface, score_rect)

        high_score_surface = font.render(f'High Score: {int(high_score)}', True, (255, 255, 255))
        high_score_rect = high_score_surface.get_rect(center=(screen_width // 2, score_y_offset + 40))
        screen.blit(high_score_surface, high_score_rect)

        restart_surface = font.render('Press R to Restart', True, (255, 255, 255))
        restart_rect = restart_surface.get_rect(center=(screen_width // 2, score_y_offset + 80))
        screen.blit(restart_surface, restart_rect)
    if state == 'start_screen':
        title_surface = font.render('Flappy Bird', True, (255, 255, 0)) # Yellow title
        title_rect = title_surface.get_rect(center=(screen_width // 2, screen_height // 3))
        screen.blit(title_surface, title_rect)

        start_surface = font.render('Press Space to Start', True, (255, 255, 255))
        start_rect = start_surface.get_rect(center=(screen_width // 2, screen_height // 2))
        screen.blit(start_surface, start_rect)

        high_score_display_surface = font.render(f'High Score: {int(high_score)}', True, (255, 255, 255))
        high_score_display_rect = high_score_display_surface.get_rect(center=(screen_width // 2, screen_height // 2 + 50))
        screen.blit(high_score_display_surface, high_score_display_rect)

# Function to reset the game
def reset_game():
    global score, game_state, high_score
    if score > high_score: 
        high_score = score
        save_high_score(high_score)
    score = 0
    bird.rect.center = (50, screen_height // 2)
    bird.velocity = 0
    pipes.empty()       # Clear existing pipes
    all_sprites.empty() # Clear all sprites
    all_sprites.add(bird) # Re-add bird
    game_state = 'game_active' # Set state to active
    create_pipe_pair() # Create initial pipes immediately for the new game
    # Restart background music if the mixer is available
    if 'pygame' in sys.modules and hasattr(pygame.mixer, 'music'):
        pygame.mixer.music.play(-1) # Play music, looping indefinitely


bird = Bird()
pipes = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()
all_sprites.add(bird)

# Timer for spawning pipes
PIPE_SPAWN_EVENT = pygame.USEREVENT
pygame.time.set_timer(PIPE_SPAWN_EVENT, pipe_spawn_interval) # Use variable for spawn interval
# pipe_gap = 150 # Gap between upper and lower pipe - Now using pipe_gap_size

# Function to create a new pair of pipes
def create_pipe_pair():
    # Random y position for the pipe gap center
    # Ensure pipe_gap_center is not too close to the top or bottom of the screen
    min_y = 100  # Minimum height for the gap center from the top
    max_y = screen_height - 100 - pipe_gap_size # Maximum height for the gap center from the top
    if min_y >= max_y: # Fallback if screen is too small
        pipe_gap_center_y = screen_height // 2
    else:
        pipe_gap_center_y = random.randint(min_y, max_y)

    top_pipe = Pipe(screen_width, pipe_gap_center_y, 1, inverted=True) # Inverted for top pipe
    bottom_pipe = Pipe(screen_width, pipe_gap_center_y, -1)
    pipes.add(top_pipe)
    pipes.add(bottom_pipe)
    all_sprites.add(top_pipe)
    all_sprites.add(bottom_pipe)

# Game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if game_state == 'game_active':
                    bird.flap()
                elif game_state == 'start_screen':
                    game_state = 'game_active' # Start the game
                    sound_swoosh.play() # Play swoosh when starting game
                    if 'pygame' in sys.modules and not pygame.mixer.music.get_busy(): # Check if music system available and not already playing
                        pygame.mixer.music.play(-1) # Start background music
                    score = 0 # Ensure score is 0 at start
                    bird.rect.center = (50, screen_height // 2)
                    bird.velocity = 0
                    pipes.empty() # Clear any pipes if they somehow existed
                    all_sprites.empty()
                    all_sprites.add(bird)
                    # Start pipe spawning by ensuring the first pair is created soon
                    create_pipe_pair() # Create initial pipes immediately

            if event.key == pygame.K_r and game_state == 'game_over':
                reset_game()
                sound_swoosh.play() # Play swoosh on restart
        if event.type == pygame.MOUSEBUTTONDOWN:
            if game_state == 'game_active':
                bird.flap()
            elif game_state == 'start_screen': # Also allow mouse click to start
               game_state = 'game_active'
               sound_swoosh.play()
               if 'pygame' in sys.modules and not pygame.mixer.music.get_busy(): # Check if music system available and not already playing
                   pygame.mixer.music.play(-1) # Start background music
               score = 0
               bird.rect.center = (50, screen_height // 2)
               bird.velocity = 0
               pipes.empty()
               all_sprites.empty()
               all_sprites.add(bird)
               create_pipe_pair()

        if event.type == PIPE_SPAWN_EVENT and game_state == 'game_active':
            create_pipe_pair()

    if game_state == 'game_active':
        # Game logic updates will go here
        all_sprites.update()

        # Collision detection
        if pygame.sprite.spritecollide(bird, pipes, False) or bird.rect.bottom >= screen_height or bird.rect.top <= 0:
            game_state = 'game_over'
            sound_hit.play()
            sound_die.play() # Play die sound on game over
            if 'pygame' in sys.modules: pygame.mixer.music.stop() # Stop background music abruptly
            if score > high_score: # Check and save high score immediately on game over
                high_score = score
                save_high_score(high_score)

        # Scoring
        for pipe in pipes:
            if not pipe.passed and pipe.rect.right < bird.rect.left:
                pipe.passed = True
                # Score 1 point if this is a bottom pipe (or any consistently chosen one from a pair)
                if pipe.pipe_type == -1: # Check if it's a bottom pipe
                    score += 1
                    sound_point.play()

        # Drawing code will go here
        # screen.fill((135, 206, 235))  # Light blue sky color - replaced by background image

        # Scroll and draw background
        if background_image:
            background_x -= background_scroll_speed
            if background_x <= -screen_width:
                background_x = 0
            screen.blit(background_image, (background_x, 0))
            screen.blit(background_image, (background_x + screen_width, 0))
        else:
            screen.fill((135, 206, 235)) # Fallback sky color

        all_sprites.draw(screen)
        display_score('game_active')

    elif game_state == 'game_over': # Game Over state
        screen.fill((0,0,0)) # Black screen for game over
        display_score('game_over')
    
    elif game_state == 'start_screen':
        # Draw background for start screen
        if background_image:
            background_x -= background_scroll_speed
            if background_x <= -screen_width:
                background_x = 0
            screen.blit(background_image, (background_x, 0))
            screen.blit(background_image, (background_x + screen_width, 0))
        else:
            screen.fill((135, 206, 235)) # Fallback sky color
        
        # Display message.png if loaded
        if message_image:
            message_rect = message_image.get_rect(center=(screen_width // 2, screen_height // 2 - 50))
            screen.blit(message_image, message_rect)
        else: # Fallback text if message_image not loaded
            start_surface = font.render('Press Space to Start', True, (255, 255, 255))
            start_rect = start_surface.get_rect(center=(screen_width // 2, screen_height // 2))
            screen.blit(start_surface, start_rect)

        # Bird can be displayed static on start screen
        bird.draw(screen) # Draw the bird in its initial position
        # display_score('start_screen') # Original call, might be redundant if message_image covers it

        # Display high score on start screen below the message image or text
        high_score_display_surface = font.render(f'High Score: {int(high_score)}', True, (255, 255, 255))
        # Adjust Y position based on whether message_image is present
        if message_image:
            high_score_y_offset = message_rect.bottom + 30
        else:
            high_score_y_offset = screen_height // 2 + 50
        high_score_display_rect = high_score_display_surface.get_rect(center=(screen_width // 2, high_score_y_offset))
        screen.blit(high_score_display_surface, high_score_display_rect)


    pygame.display.flip()  # Update the full display
    clock.tick(60)  # Limit to 60 FPS

pygame.quit()
sys.exit() 