import logging
from itertools import chain
from flask import Blueprint, request
from flask import jsonify, make_response
from fluid_seg_test_data import get_fluid_seg_test_data
from fluid_seg import fluid_seg
from FluidSeg import LexiconFactory
from db import FluidDb
from os.path import join, abspath, dirname
import pdb

logger = logging.getLogger("FluidSegAPI.FluidBeta")
fluid_beta_bp = Blueprint('fluid_beta', __name__)

basepath = abspath(dirname(__file__))
_db = FluidDb()
logger.info("loading lus from db")
lus_list = _db.get_lus()
lexicon = LexiconFactory().getWithList(lus_list)
lexicon.addSupplementary([
    "我想說", "今天來說", "的話", "今天來說的話", "要不要再研究看看"
])

n_newlu = 0

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

@fluid_beta_bp.route("/stat")
def status():    
    db = FluidDb()
    ret = db.get_statistics()
    ret["nLU"] += n_newlu    
    return jsonify(ret)

@fluid_beta_bp.route("/text", methods=["POST", "GET"])
def input_text():    
    data = request.get_json(silent=True)
    
    if not data:
        return make_400_response("Cannot get json data")
    
    if "text" not in data or not data["text"]:
        print("invalid data: ", str(data))
        return make_400_response("cannot parse data")

    if "session" not in data or \
        not data.get("session", {}).get("sessionKey", None):
        print("invalid data: ", str(data))
        return make_400_response("cannot find sessionKey")

    text = data["text"]
    sess_obj = data.get("session", {})    

    # pdb.set_trace()
    ## Handling persistence
    db = FluidDb()
    doc_id = db.save_doc({"text": text})
    sess_id = db.save_session({
        "doc_id": doc_id, 
        "sess_key": sess_obj.get("sessionKey", ""),
        "userName": sess_obj.get("userName", "")
        })

    ## Handling FluidSeg
    fluidSeg = fluid_seg(text, lexicon)
    lus_list = extract_all_lus(fluidSeg)
    try:
        lus_info = db.get_lu_info(lus_list)
    except Exception as ex:
        logger.error(ex)
        lus_info = {}

    ret = {
        "status": "ready", 
        "fluidSeg": fluidSeg,
        "lu_list": lus_info,
        "text": text
    }
    return jsonify(ret)


def annotation():
    if request.method == "GET":
        return get_annotation()
    elif request.method == "POST":
        return post_annotation()        

@fluid_beta_bp.route("/annotation", methods=["GET"])
def get_annotation():
    db = FluidDb()
    sessKey = request.args.get("sessionKey", "")
    if not sessKey:
        ret = {"status": "failed", "message": "sessionKey missing"}
        resp = jsonify(ret)
        resp.status_code = 400
        return resp
    
    sess_info = db.get_session_info(sessKey)    
    sess_id = sess_info["sess_id"]

    annot = db.get_annotation(sess_id) 
    return jsonify(annot)   

@fluid_beta_bp.route("/annotation", methods=["POST"])
def post_annotation():        
    data = request.get_json(silent=True)    
    if not data:
        return make_400_response("Cannot get json data")
    
    segs_obj = data.get("segments", [])
    tags_obj = data.get("tags", [])
    sess_key = data.get("session", {}).get("sessionKey")

    if not sess_key:
        return make_400_response("Cannot find session key")

    if "segments" in data and len(segs_obj) > 0:
        if "lus" not in segs_obj[0]:
            return make_400_response("missing lu in segments")
    
    if "tags" in data and len(tags_obj) > 0:
        tag0 = tags_obj[0]
        if "lus" not in tag0: return make_400_response("missing lu in tags")                
        if "ranges" not in tag0: return make_400_response("missing range in tags")
        if "tagField" not in tag0: return make_400_response("missing tagField in tags")                
        if "tagValue" not in tag0: return make_400_response("missing tagValue in tags")                


    ## Handling Persistence
    n_inserted = 0
    n_seg_added = 0
    global n_newlu
    try:        
        db = FluidDb()
        sess_info = db.get_session_info(sess_key)
    
        sess_id = sess_info["sess_id"]
        doc_id = sess_info["doc_id"]
        
        if len(segs_obj) > 0:
            # Convert json to db format
            seg_list = [x["ranges"] for x in segs_obj]
            lus_list = [x["lus"] for x in segs_obj]
            seg_text_list = set("/".join(x) for x in lus_list)
            
            n_seg_added = lexicon.addSupplementary(seg_text_list)
            n_newlu += n_seg_added
            db.save_seg({
                "doc_id": doc_id, 
                "sess_id": sess_id,
                "segments": seg_list
                })
        
        if len(tags_obj) > 0:
            for tag_x in tags_obj:
                # tag_data:: LexRangedDataItem
                # object passed in from json actually follows the LexRangedDataItem
                tag_data = tag_x
                tag_data["lus"] = "/".join(tag_data["lus"])
                db.save_tag(tag_data, sess_id)
                n_inserted += 1        
        db.commit_change()

    except Exception as ex:
        logger.error(ex)
        return make_status_response("Internal db error", 500)

    ret = {"status": "ready", 
            "segAdded": n_seg_added,
            "inserted": n_inserted, 
            }
    return jsonify(ret)

@fluid_beta_bp.route("/lu")
def lu():
    lus = request.args.get("text", "")
    if not lus:
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
            lus_set.add(tok["text"])
        return list(lus_set)
    except KeyError as ex:
        logger.error(ex)
        return []