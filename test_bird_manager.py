import unittest
import os
import json
from bird_manager import BirdManager

class TestBirdManager(unittest.TestCase):

    def setUp(self):
        """Set up for test methods."""
        # Ensure a clean state for tests that might create the progress file
        self.progress_file = 'bird_progress.json'
        if os.path.exists(self.progress_file):
            os.remove(self.progress_file)
        self.bird_manager = BirdManager()

    def tearDown(self):
        """Tear down after test methods."""
        # Clean up the progress file if it was created by a test
        if os.path.exists(self.progress_file):
            os.remove(self.progress_file)

    def test_initialization_unlocked_birds(self):
        """Test initial state of unlocked_birds."""
        expected_unlocked = {'blue': True, 'red': False, 'yellow': False}
        self.assertEqual(self.bird_manager.unlocked_birds, expected_unlocked)

    def test_initialization_high_scores(self):
        """Test initial state of high_scores."""
        expected_scores = {'red': 0, 'yellow': 0, 'blue': 0, 'default': 0}
        self.assertEqual(self.bird_manager.high_scores, expected_scores)

    def test_initialization_achievements(self):
        """Test that achievements are populated."""
        self.assertTrue(self.bird_manager.achievements)
        self.assertIn('red', self.bird_manager.achievements)
        self.assertIn('yellow', self.bird_manager.achievements)
        self.assertIn('blue', self.bird_manager.achievements)
        self.assertEqual(self.bird_manager.achievements['blue']['name'], 'Graceful Glider')

    def test_get_available_birds(self):
        """Test get_available_birds method."""
        expected_birds = ['red', 'yellow', 'blue'] # Order matters if it's based on dict keys pre Python 3.7
        # Sorting to make the test order-independent for dict keys
        self.assertEqual(sorted(self.bird_manager.get_available_birds()), sorted(expected_birds))

    def test_get_bird_achievement_info_valid(self):
        """Test get_bird_achievement_info for a valid bird type."""
        info = self.bird_manager.get_bird_achievement_info('red')
        self.assertIsNotNone(info)
        self.assertEqual(info['name'], 'Speed Demon')

    def test_get_bird_achievement_info_invalid(self):
        """Test get_bird_achievement_info for an invalid bird type."""
        info = self.bird_manager.get_bird_achievement_info('green')
        self.assertIsNone(info)

    def test_is_bird_unlocked_initial(self):
        """Test is_bird_unlocked for initially locked and unlocked birds."""
        self.assertTrue(self.bird_manager.is_bird_unlocked('blue'))
        self.assertFalse(self.bird_manager.is_bird_unlocked('red'))
        self.assertFalse(self.bird_manager.is_bird_unlocked('yellow'))
        self.assertFalse(self.bird_manager.is_bird_unlocked('unknown_bird'))

    def test_load_progress_non_existent_file(self):
        """Test loading progress when the file does not exist."""
        # setUp already ensures the file doesn't exist initially
        # Re-instantiate to trigger load_progress in a controlled way for this test
        if os.path.exists(self.progress_file): # Should not exist, but defensive
            os.remove(self.progress_file)
        
        manager = BirdManager() # load_progress is called in __init__
        
        expected_unlocked = {'blue': True, 'red': False, 'yellow': False}
        expected_scores = {'red': 0, 'yellow': 0, 'blue': 0, 'default': 0}
        self.assertEqual(manager.unlocked_birds, expected_unlocked)
        self.assertEqual(manager.high_scores, expected_scores)

    def test_load_progress_valid_data(self):
        """Test loading progress from a valid JSON file."""
        valid_data = {
            'unlocked_birds': {'blue': True, 'red': True, 'yellow': False},
            'high_scores': {'blue': 10, 'red': 55, 'yellow': 5, 'default': 0}
        }
        with open(self.progress_file, 'w') as f:
            json.dump(valid_data, f)
        
        manager = BirdManager() # load_progress is called in __init__
        
        self.assertEqual(manager.unlocked_birds, valid_data['unlocked_birds'])
        self.assertEqual(manager.high_scores, valid_data['high_scores'])

    def test_load_progress_corrupted_json(self):
        """Test loading progress from a corrupted JSON file."""
        with open(self.progress_file, 'w') as f:
            f.write("{'unlocked_birds': {'blue': True, 'red': True") # Invalid JSON
        
        # Suppress print output during this test if desired, or check for it
        manager = BirdManager()
        
        # Should revert to defaults
        expected_unlocked = {'blue': True, 'red': False, 'yellow': False}
        expected_scores = {'red': 0, 'yellow': 0, 'blue': 0, 'default': 0}
        self.assertEqual(manager.unlocked_birds, expected_unlocked)
        self.assertEqual(manager.high_scores, expected_scores)

    def test_load_progress_missing_keys(self):
        """Test loading progress from JSON with missing keys."""
        # Case 1: missing 'unlocked_birds'
        data_missing_unlocked = {
            'high_scores': {'blue': 15, 'red': 2, 'yellow': 1, 'default': 0}
        }
        with open(self.progress_file, 'w') as f:
            json.dump(data_missing_unlocked, f)
        
        manager1 = BirdManager()
        expected_unlocked_default = {'blue': True, 'red': False, 'yellow': False}
        self.assertEqual(manager1.unlocked_birds, expected_unlocked_default, "Unlocked birds should default")
        self.assertEqual(manager1.high_scores, data_missing_unlocked['high_scores'], "High scores should load")

        # Clean up for next sub-test
        if os.path.exists(self.progress_file):
            os.remove(self.progress_file)

        # Case 2: missing 'high_scores'
        data_missing_scores = {
            'unlocked_birds': {'blue': True, 'red': True, 'yellow': False}
        }
        with open(self.progress_file, 'w') as f:
            json.dump(data_missing_scores, f)

        manager2 = BirdManager()
        expected_scores_default = {'red': 0, 'yellow': 0, 'blue': 0, 'default': 0}
        self.assertEqual(manager2.unlocked_birds, data_missing_scores['unlocked_birds'], "Unlocked birds should load")
        self.assertEqual(manager2.high_scores, expected_scores_default, "High scores should default")

    def test_save_progress(self):
        """Test saving progress correctly writes to file."""
        self.bird_manager.unlocked_birds['red'] = True
        self.bird_manager.high_scores['red'] = 70
        self.bird_manager.high_scores['blue'] = 20
        
        self.bird_manager.save_progress()
        
        self.assertTrue(os.path.exists(self.progress_file))
        with open(self.progress_file, 'r') as f:
            saved_data = json.load(f)
        
        self.assertEqual(saved_data['unlocked_birds'], self.bird_manager.unlocked_birds)
        self.assertEqual(saved_data['high_scores'], self.bird_manager.high_scores)

    def test_update_score_new_high_score_and_unlock(self):
        """Test update_score with a new high score that also unlocks a bird."""
        self.assertFalse(self.bird_manager.is_bird_unlocked('red')) # Initially locked
        self.bird_manager.update_score('red', 55) # Requirement for red is 50
        
        self.assertEqual(self.bird_manager.high_scores['red'], 55)
        self.assertTrue(self.bird_manager.is_bird_unlocked('red'))
        
        # Check if progress was saved (bird unlocked)
        manager_new_instance = BirdManager() # loads from file
        self.assertTrue(manager_new_instance.is_bird_unlocked('red'))
        self.assertEqual(manager_new_instance.high_scores['red'], 55)


    def test_update_score_lower_score(self):
        """Test update_score with a score lower than current high score."""
        self.bird_manager.high_scores['blue'] = 10
        self.bird_manager.update_score('blue', 5) # Current high score is 10
        
        self.assertEqual(self.bird_manager.high_scores['blue'], 10) # Should not change

    def test_update_score_no_unlock(self):
        """Test update_score that sets a new high score but doesn't unlock."""
        self.assertFalse(self.bird_manager.is_bird_unlocked('yellow')) # Initially locked
        self.bird_manager.update_score('yellow', 25) # Requirement for yellow is 30
        
        self.assertEqual(self.bird_manager.high_scores['yellow'], 25)
        self.assertFalse(self.bird_manager.is_bird_unlocked('yellow'))

    def test_check_achievements_unlocks_bird(self):
        """Test check_achievements directly (though usually called by update_score)."""
        self.assertFalse(self.bird_manager.is_bird_unlocked('yellow'))
        # Manually set score high enough and call check_achievements
        self.bird_manager.high_scores['yellow'] = 35 
        self.bird_manager.check_achievements('yellow', 35) # Requirement for yellow is 30
        
        self.assertTrue(self.bird_manager.is_bird_unlocked('yellow'))
        
        # Verify save
        manager_new_instance = BirdManager()
        self.assertTrue(manager_new_instance.is_bird_unlocked('yellow'))

    def test_check_achievements_already_unlocked(self):
        """Test check_achievements for an already unlocked bird."""
        # Unlock 'red' first
        self.bird_manager.update_score('red', 50)
        self.assertTrue(self.bird_manager.is_bird_unlocked('red'))
        
        # Call check_achievements again with a higher score
        self.bird_manager.high_scores['red'] = 60
        self.bird_manager.check_achievements('red', 60)
        
        # Should still be unlocked, no error, and progress should reflect the unlock
        self.assertTrue(self.bird_manager.is_bird_unlocked('red'))


if __name__ == '__main__':
    unittest.main()
