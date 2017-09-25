import flask
from flask import Flask
from flask_restful import Resource, Api
from flask import request
from FluidSeg import FluidSeg
from FluidSeg import LexiconFactory, TokenData
import pyOceanus

app = Flask(__name__)
api = Api(app)

class UserLexicon(Resource):
    def get(self):
        return {"n_entry": 1024}

    def post(self):
        data = request.get_json()        
        if not data or "annotations" not in data:
            return flask.make_response("Cannot get json data", 400)        
        
        annot = data["annotations"]
        n_added = len([x["w"] for x in annot if "w" in x])
        return {"added": n_added}

class Segments(Resource):
    def __init__(self):
        # self.lexicon = LexiconFactory.get("")
        # self.fseg = FluidSeg(lexicon)
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

@app.after_request
def after_request(response):
    h = response.headers
    h["Access-Control-Allow-Origin"] = "*"
    return response

api.add_resource(Segments, '/seg')
api.add_resource(UserLexicon, "/lexicon")
api.add_resource(IndexAPI, "/")

if __name__ == "__main__":
    app.config.update(JSON_AS_ASCII = False)
    app.run(debug=True)


