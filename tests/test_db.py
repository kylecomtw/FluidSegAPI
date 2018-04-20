import unittest
from db import FluidDb

class DbTest(unittest.TestCase):
    def test_create_db(self):
        db = FluidDb()
        self.assertTrue(True)

if __name__ == "__main__":
    unittest.main()
