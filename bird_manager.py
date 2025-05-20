import json
import os

class BirdManager:
    def __init__(self):
        self.progress_file = 'bird_progress.json'
        self.unlocked_birds = {'red', 'yellow', 'blue'}
        self.achievements = {
            'red': {'name': 'Speed Demon', 'requirement': 50, 'description': 'Moves faster horizontally.'},
            'yellow': {'name': 'Heavy Lifter', 'requirement': 30, 'description': 'Stronger flap, falls faster.'},
            'blue': {'name': 'Graceful Glider', 'requirement': 40, 'description': 'Falls more gently.'}
        }
        self.high_scores = {
            'red': 0,
            'yellow': 0,
            'blue': 0,
            'default': 0
        }
        self.load_progress()

    def load_progress(self):
        try:
            if os.path.exists('bird_progress.json'):
                with open('bird_progress.json', 'r') as f:
                    data = json.load(f)
                    self.unlocked_birds = data.get('unlocked_birds', {'default': True})
                    self.high_scores = data.get('high_scores', self.high_scores)
        except Exception as e:
            print(f"Error loading progress: {e}")

    def save_progress(self):
        try:
            with open('bird_progress.json', 'w') as f:
                json.dump({
                    'unlocked_birds': self.unlocked_birds,
                    'high_scores': self.high_scores
                }, f)
        except Exception as e:
            print(f"Error saving progress: {e}")

    def update_score(self, bird_type, score):
        if score > self.high_scores[bird_type]:
            self.high_scores[bird_type] = score
            self.check_achievements(bird_type, score)
            self.save_progress()

    def check_achievements(self, bird_type, score):
        if bird_type in self.achievements:
            if score >= self.achievements[bird_type]['requirement']:
                self.unlocked_birds[bird_type] = True
                self.save_progress()

    def is_bird_unlocked(self, bird_type):
        return bird_type in self.unlocked_birds

    def get_available_birds(self):
        return ['red', 'yellow', 'blue']

    def get_bird_achievement_info(self, bird_type):
        if bird_type in self.achievements:
            return self.achievements[bird_type]
        return None 