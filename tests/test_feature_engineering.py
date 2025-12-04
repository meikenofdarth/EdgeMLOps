# tests/test_feature_engineering.py
import unittest
import pandas as pd
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from cloud.train import create_lag_features

class TestFeatureEngineering(unittest.TestCase):
    def test_lag_feature_creation(self):
        """Test if lag features are created correctly and data is shaped as expected."""
        data = {'voc_ppb': [100, 110, 120, 130, 140, 150, 160]}
        df = pd.DataFrame(data)
        n_lags = 5
        
        df_lags = create_lag_features(df, 'voc_ppb', n_lags)
        
        # Test 1: Check if the correct number of rows were dropped (equal to n_lags)
        self.assertEqual(len(df_lags), len(df) - n_lags)
        
        # Test 2: Check if all expected new columns were created
        expected_cols = [f'voc_ppb_lag_{i}' for i in range(1, n_lags + 1)]
        for col in expected_cols:
            self.assertIn(col, df_lags.columns)
        
        # Test 3: Check if the lag values are correct in the first row
        first_row = df_lags.iloc[0]
        self.assertEqual(first_row['voc_ppb_lag_1'], 140)
        self.assertEqual(first_row['voc_ppb_lag_5'], 100)