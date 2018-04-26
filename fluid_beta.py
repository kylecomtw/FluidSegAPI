import logging
from flask import Blueprint, request
from flask import jsonify
from fluid_seg_test_data import get_fluid_seg_test_data

logger = logging.getLogger("FluidSeg.FluidBeta")

fluid_beta_bp = Blueprint('fluid_beta', __name__)

def generate_tag_data(tagName):    
    tag = {"tag": tagName, "pos":[0, 2], "text": "1fd34"}
    return tag

@fluid_beta_bp.route("/")
def index():
    ret = {"status": "ready", "message": "fluidBeta API ready"}
    return jsonify(ret)

@fluid_beta_bp.route("/text")
def input_text():    
    text = "今天來說的話，我想說，不知道大家要不要再研究看看。"
    fluidSeg = get_fluid_seg_test_data()
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