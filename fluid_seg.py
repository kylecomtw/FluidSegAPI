from os.path import abspath, dirname
from itertools import chain
import pyOceanus
from FluidSeg import FluidSeg
from FluidSeg import TokenData
import config

oc = pyOceanus.Oceanus(config.OCEANUS_ENDPOINT)

def fluid_seg(text, lexicon):

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
            segData.toSegmentedToken(segData.preseg, granularity=0.00),
            segData.toSegmentedToken(segData.preseg, granularity=0.33),
            segData.toSegmentedToken(segData.preseg, granularity=0.66),
            segData.toSegmentedToken(segData.preseg, granularity=1.00),
            segData.toSegmentedToken(segData.preseg),
            segData.toSegmentedToken(segData.tokens),
            ]
    seg_obj_list = []
    for seg in seg_list:
        seg_obj_list.append([tok.__dict__ for tok in seg])

    return {
            "granularity": gran_label, 
            "segments": seg_obj_list 
        }