import flask
import logging

logger = logging.getLogger("FluidSegAPI")
ch = logging.StreamHandler()
formatter = logging.Formatter("%(name)s - [%(levelname)s]: %(message)s")
ch.setFormatter(formatter)
logger.addHandler(ch)
logger.setLevel("INFO")


import os
from os.path import abspath, dirname, join
from itertools import chain
from flask import Flask
from flask_restful import Resource, Api
from flask_cors import CORS
from flask import request
from FluidSeg import FluidSeg
from FluidSeg import LexiconFactory, TokenData
from fluid_beta import fluid_beta_bp
import config
import pyOceanus
import pdb

app = Flask(__name__)
CORS(app)
api = Api(app)


basepath = abspath(dirname(__file__))
lexicon = LexiconFactory().get(join(basepath, "data/fluid_seg_lexicon.txt"))


oc = pyOceanus.Oceanus(config.OCEANUS_ENDPOINT)

class UserLexicon(Resource):
    def __init__(self):
        self.n_user_words = 0

    def get(self):
        return {"n_entry": self.n_user_words}
        # return {"n_entry": self.n_user_words}

    def post(self):
        data = request.get_json()        
        if not data or "annotations" not in data:
            return flask.make_response("Cannot get json data", 400)        
        
        annot = data["annotations"]
        words = [x["w"] for x in annot if "w" in x]
        n_added = lexicon.addSupplementary(words)
        return {"added": n_added}

class Segments(Resource):
    def __init__(self):
        pass

    def get(self):
        return "FluidSeg API standby"

    def post(self):
        data = request.get_json()
        if not data:
            return flask.make_response("Cannot get json data", 400)
        
        if "text" not in data:
            print("invalid data: ", str(data))
            return flask.make_response("cannot parse data", 400)

        text = data["text"]
        fseg = FluidSeg(lexicon)
        segData = fseg.segment(text)
        try:
            od = oc.parse(text)        
            preseg = list(chain.from_iterable(od.tokens))
            preseg = [TokenData(x[0], x[3], x[4]) for x in preseg]
        except Exception as ex:
            print("cannot process text content")
            return flask.make_response("cannot process text content", 400)
        
        segData.setPresegment(preseg)
        gran_label = ["0.00", "0.33", "0.66", "1.00", "preseg", "token"]
        seg_list = [
                segData.toSegmentedText(segData.preseg, granularity=0.00),
                segData.toSegmentedText(segData.preseg, granularity=0.33),
                segData.toSegmentedText(segData.preseg, granularity=0.66),
                segData.toSegmentedText(segData.preseg, granularity=1.00),
                segData.toSegmentedText(segData.preseg),
                segData.toSegmentedText(segData.tokens),
                ]
        return {"fluidSeg": {
                    "granularity": gran_label, 
                    "segments": seg_list }, 
                "text": text }

class SegmentsTest(Resource):
    def __init__(self):
        pass

    def get(self):
        return "FluidSeg API standby"

    def post(self):
        data = request.get_json()
        if not data:
            return flask.make_response("Cannot get json data", 400)

        echo = data["text"]

        gran_label = ["0.33", "0.66", "1.00", "preseg", "token"]
        test_data = [
            ['今天來說的話', '，', '我想說', '，', '不知道大家要不要再研究看看', '。'],
            ['今天來說的話', '，', '我想說', '，', '不知道大家要不要', '再研究看看', '。'],
            ['今天來說', '的話', '，', '我想說', '，', '不知道', '大家', '要不要', '再研究', '看看', '。'],
            ['今天', '來說', '的話', '，', '我', '想', '說', '，', '不', '知道', 
                '大家', '要', '不', '要', '再', '研究', '看看', '。'],
            ['今', '天', '來', '說', '的', '話', '，', 
                '我', '想', '說', '，', '不', '知', '道', '大', '家', 
                '要', '不', '要', '再', '研', '究', '看', '看', '。'] 
        ]
        
        return {"fluidSeg": {
                    "granularity": gran_label, 
                    "segments": test_data 
                    }, 
                "debug_echo": echo
               }

class IndexAPI(Resource):
    def get(self):
        return "use /seg endpoint"

api.add_resource(Segments, '/seg')
api.add_resource(SegmentsTest, '/segtest')
api.add_resource(UserLexicon, "/lexicon")
api.add_resource(IndexAPI, "/")
app.register_blueprint(fluid_beta_bp, url_prefix="/beta")
app.config.update(JSON_AS_ASCII = False)

if __name__ == "__main__":    
    app.run(debug=True)


