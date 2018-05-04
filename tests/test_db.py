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
        ret = db.get_lu_info(["高興", "生氣"])        
        self.assertIsNotNone(ret)
        self.assertGreater(len(ret), 0)
        print(ret)

    def test_session_query(self):
        db = FluidDb()
        doc_id = db.save_doc({"text": "session test"})
        sess_id = db.save_session({"sess_key": "Sess123", "doc_id": doc_id, "userName": "anony1"})
        ret = db.get_session_info("Sess123")
        self.assertIsNotNone(ret)
        self.assertGreaterEqual(len(ret), 0)
        print(ret)
    
    def test_segment(self):
        db = FluidDb()

        doc_id = db.save_doc({"text": "segmentation test"})
        sess_id = db.save_session({"doc_id": doc_id, "userName": "anony2"})
        ret_id = db.save_seg({
                    "doc_id": doc_id, 
                    "sess_id": sess_id, 
                    "segments": [(0,1),(3,4),(2,5)]})
        print(ret_id)
        self.assertGreaterEqual(ret_id, 0)
        ret = db.get_segment_info(sess_id)
        print(ret)
        self.assertIsNotNone(ret)
        self.assertGreaterEqual(len(ret), 0)
    
    def test_document(self):
        db = FluidDb()
        ret_id = db.save_doc({"text": "abcde"})
        self.assertGreaterEqual(ret_id, 0)
        ret = db.get_document_text(ret_id)
        print(ret)

    
if __name__ == "__main__":
    unittest.main()
