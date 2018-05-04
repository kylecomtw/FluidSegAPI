import logging
from flask import Blueprint, request
from flask import jsonify, make_response
from fluid_seg_test_data import get_fluid_seg_test_data
from fluid_seg import fluid_seg
from FluidSeg import LexiconFactory
from db import FluidDb
from os.path import join, abspath, dirname
import pdb

logger = logging.getLogger("FluidSeg.FluidBeta")
fluid_beta_bp = Blueprint('fluid_beta', __name__)

basepath = abspath(dirname(__file__))
db = FluidDb()
lus_list = db.get_lus()
lexicon = LexiconFactory().getWithList(lus_list)
lexicon.addSupplementary([
    "我想說", "今天來說", "的話", "今天來說的話", "要不要再研究看看"
])
def make_400_response(msg):
    return make_status_response(msg, 400)

def make_status_response(msg, status_code):
    resp = jsonify({"status": "failed", "message": msg})
    resp.status_code = status_code
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

    if "session" not in data or \
        not data.get(session, {}).get("sessionKey", None):
        print("invalid data: ", str(data))
        return make_400_response("cannot find sessionKey")

    text = data["text"]
    sess_obj = data.get("session", {})    

    # pdb.set_trace()
    ## Handling persistence
    db = FluidDb()
    doc_id = db.save_doc({"text": text})
    db.save_session({
        "doc_id": doc_id, 
        "sess_key": sess_obj.get("sessionKey", ""),
        "userName": sess_obj.get("userName", "")
        })

    ## Handling FluidSeg
    fluidSeg = fluid_seg(text, lexicon)
    lus_list = extract_all_lus(fluidSeg)
    try:
        lus_info = db.get_lu_info(lus_list)
    except:
    ret = {
        "status": "ready", 
        "fluidSeg": fluidSeg,
        "lu_list": lus_list,
        "text": text
    }
    return jsonify(ret)

@fluid_beta_bp.route("/annotation", methods=["POST", "GET"])
def annotation():        
    data = request.get_json(silent=True)    
    if not data:
        return make_400_response("Cannot get json data")
    segs_obj = data.get("segments", [])
    tags_obj = data.get("tags", [])

    # Convert json to db format
    seg_list = [tuple(x["range"]) for x in segs_obj]

    ## Handling Persistence
    try:
        db = FluidDb()
        sess_info = db.get_session_info(sess_key)
    
        sess_id = sess_info["sess_id"]
        doc_id = sess_info["doc_id"]

        db.save_seg({
            "doc_id": doc_id, 
            "sess_id": sess_id,
            "segments": seg_list
            })
        
        for tag_x in tags_obj:
            # tag_data:: LexRangedDataItem
            # object passed in from json actually follows the LexRangedDataItem
            tag_data = tag_x
            db.save_tag(tag_data)
        db.commit_change()

    except Exception as ex:
        logger.error(ex)
        make_status_response("Internal db error", 500)

    ret = {"status": "ready", "inserted": 0, "debug": request.method}
    return jsonify(ret)

@fluid_beta_bp.route("/lu")
def lu():
    lus = request.args.get("text", "")
    if not intext:
        ret = {"status": "failed", "message": "empty text"}
        resp = jsonify(ret)
        resp.status_code = 400
        return resp

    try:
        db = FluidDb()
        lu_list = lus.split(",")
        lu_data = db.get_lu_info(lu_list)
    except Exception as ex:
        logger.error(ex)
        lu_data = {}
    
    ret = lu_data
    return jsonify(ret)

def extract_all_lus(fluidseg_obj):
    lus_set = set()
    try:
        segments_list = fluidseg_obj["segments"]
        for tok in chain.from_iterable(segments_list):
            lus_list.add(tok["text"])
        return lus_list
    except KeyError as ex:
        logger.error(ex)
        return []