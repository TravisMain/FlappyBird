import json
import os

class BirdManager:
    def __init__(self):
        self.progress_file = 'bird_progress.json'
        # Initialize unlocked_birds with 'blue' unlocked by default
        self.unlocked_birds = {'blue': True, 'red': False, 'yellow': False}
        self.achievements = {
            'red': {'name': 'Speed Demon', 'requirement': 50, 'description': 'Moves faster horizontally.'},
            'yellow': {'name': 'Heavy Lifter', 'requirement': 30, 'description': 'Stronger flap, falls faster.'},
            'blue': {'name': 'Graceful Glider', 'requirement': 40, 'description': 'Falls more gently.'}
        }
        self.high_scores = {
            'red': 0,
            'yellow': 0,
            'blue': 0,
            'default': 0  # Keep a default score, though bird types are specific
        }
        self.load_progress()

    def load_progress(self):
        # Default state for unlocked_birds, ensuring all achievement birds are present
        default_unlocked_birds = {bird: False for bird in self.achievements.keys()}
        default_unlocked_birds['blue'] = True # Blue is unlocked by default

        try:
            if os.path.exists(self.progress_file):
                with open(self.progress_file, 'r') as f:
                    data = json.load(f)
                    # Load unlocked_birds if present
                    # Start with a copy of the default unlocked birds state.
                    # This ensures all known birds are present and 'blue' defaults to True.
                    self.unlocked_birds = default_unlocked_birds.copy()
                    
                    loaded_saved_unlocked_birds = data.get('unlocked_birds')
                    if loaded_saved_unlocked_birds is not None:
                        # If there's saved data for unlocked_birds, update self.unlocked_birds.
                        # This will override defaults for birds found in the save file.
                        for bird_type, is_unlocked in loaded_saved_unlocked_birds.items():
                            if bird_type in self.unlocked_birds: # Only process known bird types
                                self.unlocked_birds[bird_type] = is_unlocked
                    
                    self.high_scores = data.get('high_scores', self.high_scores)
            else:
                # File doesn't exist, so initialize with a copy of the default state.
                print(f"Progress file '{self.progress_file}' not found. Using default progress.")
                self.unlocked_birds = default_unlocked_birds.copy()
                # high_scores are already initialized in __init__ and potentially updated by data.get if file existed but was empty
                # If file truly doesn't exist, self.high_scores retains its __init__ state, which is the desired default.

        except FileNotFoundError: # Explicitly handle if os.path.exists was bypassed or failed (though unlikely with current check)
            print(f"Progress file '{self.progress_file}' not found. Initializing with default progress.")
            self.unlocked_birds = default_unlocked_birds.copy()
            self.high_scores = {bird: 0 for bird in self.achievements.keys()}
            self.high_scores['default'] = 0
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON from '{self.progress_file}': {e}. Initializing with default progress.")
            self.unlocked_birds = default_unlocked_birds.copy()
            self.high_scores = {bird: 0 for bird in self.achievements.keys()}
            self.high_scores['default'] = 0
        except IOError as e:
            print(f"IOError loading progress from '{self.progress_file}': {e}. Initializing with default progress.")
            self.unlocked_birds = default_unlocked_birds.copy()
            self.high_scores = {bird: 0 for bird in self.achievements.keys()}
            self.high_scores['default'] = 0
        except Exception as e: # Catch any other unexpected errors
            print(f"An unexpected error occurred while loading progress: {e}. Initializing with default progress.")
            self.unlocked_birds = default_unlocked_birds.copy()
            self.high_scores = {bird: 0 for bird in self.achievements.keys()}
            self.high_scores['default'] = 0


    def save_progress(self):
        try:
            with open(self.progress_file, 'w') as f: # Use self.progress_file
                json.dump({
                    'unlocked_birds': self.unlocked_birds,
                    'high_scores': self.high_scores
                }, f)
        except IOError as e:
            print(f"IOError: Could not save progress to '{self.progress_file}': {e}")
        except Exception as e: # Catch any other unexpected errors during save
            print(f"An unexpected error occurred while saving progress: {e}")

    def update_score(self, bird_type, score):
        # Ensure high_scores dictionary has the bird_type key
        if bird_type not in self.high_scores:
            self.high_scores[bird_type] = 0
            
        if score > self.high_scores[bird_type]:
            self.high_scores[bird_type] = score
            self.check_achievements(bird_type, score) # save_progress is called in check_achievements

    def check_achievements(self, bird_type, score):
        if bird_type in self.achievements:
            # Unlock the bird if the score meets the requirement and it's not already unlocked
            if not self.unlocked_birds.get(bird_type, False) and score >= self.achievements[bird_type]['requirement']:
                self.unlocked_birds[bird_type] = True
                self.save_progress() # Save progress when an achievement is unlocked

    def is_bird_unlocked(self, bird_type):
        # Returns true if bird_type is in unlocked_birds and its value is True
        return self.unlocked_birds.get(bird_type, False)

    def get_available_birds(self):
        # Returns a list of all bird types defined in achievements
        return list(self.achievements.keys())

    def get_bird_achievement_info(self, bird_type):
        if bird_type in self.achievements:
            return self.achievements[bird_type]
        return None 