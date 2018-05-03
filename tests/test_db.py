import unittest
from db import FluidDb
import pdb

class DbTest(unittest.TestCase):
    @unittest.skip("")
    def test_create_db(self):
        db = FluidDb()
        self.assertTrue(True)

    def test_lu_query(self):
        db = FluidDb()
        ret = db.get_lu_info("高興")
        self.assertIsNotNone(ret)
        self.assertGreater(len(ret), 0)

    def test_session_query(self):
        db = FluidDb()
        ret = db.get_session_info(343)
        self.assertIsNotNone(ret)
        self.assertGreater(len(ret), 0)
    
    def test_segment(self):
        db = FluidDb()
        ret = db.get_segment_info(343)
        self.assertIsNotNone(ret)
        self.assertGreater(len(ret), 0)
    
    def test_document(self):
        db = FluidDb()
        ret = db.save_doc({"text": "abcde"})

    
if __name__ == "__main__":
    unittest.main()
