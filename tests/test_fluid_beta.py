import unittest
import requests
import pdb

endpoint = "http://127.0.0.1:5000/beta"
class FluidBetaTest(unittest.TestCase):    
    def test_statistics(self):
        resp = requests.get(endpoint + "/stat")
        self.assertEqual(resp.status_code, 200)
        ret = resp.json()
        self.assertGreater(ret["nField"], 0)
        self.assertGreater(ret["nLU"], 0)
        self.assertGreater(ret["nTag"], 0)

    def test_flow(self):
        self.text_POST()
        self.annotation_POST()
        self.annotation_GET()

    def text_POST(self):
        indata = {
            "session": {
                "userName": "testUser",
                "sessionKey": "myTestSession"
            },
            "text": "我想說這樣子的話不曉得可不可以。"
        }
        resp = requests.post(endpoint + "/text", json=indata)        
        ret = resp.json()        
        self.assertEqual(resp.status_code, 200)        
        self.assertIsNotNone(ret.get("lu_list"))
        self.assertIsNotNone(ret.get("fluidSeg"))

        fluidSeg = ret.get("fluidSeg")        
        self.assertGreater(len(fluidSeg.get("granularity")), 0)
        self.assertGreater(len(fluidSeg.get("segments")), 0)

        lu_list = ret.get("lu_list")
        self.assertGreater(len(lu_list), 0)
        lu_key = list(lu_list.keys())[0]
        self.assertGreater(len(lu_list[lu_key]), 0)
        print("lu_list[lu_key]: ", lu_list[lu_key])
    
    def annotation_POST(self):
        req_data = {
            "session": {"userName": "testUser", "sessionKey": "myTestSession"},
            "segments": [
                {"lus": ["可不可以"], "ranges": [[11,15]]}, 
                {"lus": ["我想說"], "ranges": [[0,3]]}], 
            "tags": [
                {"lus": ["我想說"], "ranges": [[0, 3]], "tagField": "stance", "tagValue": "speculative"},
                {"lus": ["不曉得"], "ranges": [[8,11]], "tagField": "stance", "tagValue": "suggestive"},
                {"lus": ["我想說", "的話"], "ranges": [[0, 3], [6,8]], "tagField": "construction", "tagValue": "conjecture"},]
            }

        resp = requests.post(endpoint + "/annotation", json=req_data)        
        ret = resp.json() 
        print(ret)
        self.assertEqual(resp.status_code, 200)  

    def annotation_GET(self):
        resp = requests.get(endpoint + "/annotation", params={"sessionKey": "myTestSession"})
        ret = resp.json()
        print(ret)
        self.assertEqual(resp.status_code, 200)  

    def test_lu_GET(self):
        resp = requests.get(endpoint + "/lu", params={"text": "高興"})        
        self.assertEqual(resp.status_code, 200)  
        ret = resp.json() 
        print(ret)
    
    
        