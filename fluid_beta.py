import logging
from flask import Blueprint, request
from flask import jsonify, make_response
from fluid_seg_test_data import get_fluid_seg_test_data
from fluid_seg import fluid_seg
from FluidSeg import LexiconFactory
from os.path import join, abspath, dirname
import pdb

logger = logging.getLogger("FluidSeg.FluidBeta")
fluid_beta_bp = Blueprint('fluid_beta', __name__)

basepath = abspath(dirname(__file__))
lexicon = LexiconFactory().get(join(basepath, "data/fluid_seg_lexicon.txt"))
lexicon.addSupplementary([
    "我想說", "今天來說", "的話", "今天來說的話", "要不要再研究看看"
])
def make_400_response(msg):
    resp = jsonify({"status": "failed", "message": msg})
    resp.status_code = 400
    return resp

def generate_tag_data(tagName):    
    tag = {"tag": tagName, "pos":[0, 2], "text": "1fd34"}
    return tag

@fluid_beta_bp.route("/")
def index():
    ret = {"status": "ready", "message": "fluidBeta API ready"}
    return jsonify(ret)

@fluid_beta_bp.route("/text", methods=["POST", "GET"])
def input_text():    
    data = request.get_json(silent=True)
    print(data)
    if not data:
        return make_400_response("Cannot get json data")
    
    if "text" not in data or not data["text"]:
        print("invalid data: ", str(data))
        return make_400_response("cannot parse data")

    text = data["text"]
    # pdb.set_trace()
    fluidSeg = fluid_seg(text, lexicon)
    ret = {
        "status": "ready", 
        "fluidSeg": fluidSeg,
        "lu_list": {
            "我想說": [generate_tag_data("tagY" + str(i)) for i in range(3)],
            "今天來說的話": [generate_tag_data("tagX" + str(i)) for i in range(2)]
        },
        "text": text
    }
    return jsonify(ret)

@fluid_beta_bp.route("/annotation", methods=["POST", "GET"])
def annotation():        
    ret = {"status": "ready", "inserted": 0, "debug": request.method}
    return jsonify(ret)

@fluid_beta_bp.route("/lu")
def lu():
    intext = request.args.get("text", "")
    if not intext:
        ret = {"status": "failed", "message": "empty text"}
        resp = jsonify(ret)
        resp.status_code = 400
        return resp

    lu = [generate_tag_data("tag" + str(i)) for i in range(3)]
    
    ret = {"status": "ready", 
           "lu": lu, "echo": intext }
    return jsonify(ret)