# tests/test_transcriber.py
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from src.core.transcriber import KinyarwandaTranscriber

class TestTranscriber(unittest.TestCase):
    def test_placeholder(self):
        self.assertEqual(True, True)

if __name__ == '__main__':
    unittest.main()
