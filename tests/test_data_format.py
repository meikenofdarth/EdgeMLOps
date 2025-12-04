# tests/test_data_format.py
import unittest
import sys
import os

# This is a bit of magic to make sure the test can find the main project files
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from devices.publisher import generate_sensor_data

class TestDataFormat(unittest.TestCase):
    def test_payload_structure_and_types(self):
        """Test if the generated payload has the correct structure and data types."""
        payload, _ = generate_sensor_data(150.0)
        
        # Check that all required keys are present
        self.assertIn("timestamp", payload)
        self.assertIn("temp_c", payload)
        self.assertIn("humidity", payload)
        self.assertIn("voc_ppb", payload)
        
        # Check that the data types are correct
        self.assertIsInstance(payload["voc_ppb"], int)
        self.assertIsInstance(payload["temp_c"], float)
        self.assertIsInstance(payload["humidity"], float)