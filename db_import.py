import json
import os
import gzip
import logging
from db import FluidDb
import pdb

logger = logging.getLogger("FluidSeg.DbImport")
logger.setLevel("INFO")

def import_deep_lexicon(deeplex_path):
    if not os.path.exists(deeplex_path):
        logger.warning("Cannot find deeplex file at %s", deeplex_path)
        return
    
    with gzip.open(deeplex_path, "rt", encoding="UTF-8") as fin:
        dlex_data = json.load(fin)
    
    print("Deeplex loaded: %d entries" % len(dlex_data))
    db = FluidDb()    
    
    nItem = len(dlex_data)    
    for lex_idx, lex_item in enumerate(dlex_data):  
        if type(lex_item["lu"]) != str:
            logger.warning("invalid LU encounter: %s", str(lex_item))
            continue

        if lex_idx % 1000 == 0:
            logger.info("saving tag %d/%d", lex_idx, nItem)                  
        try:        
            lex_item["lus"] = lex_item["lu"]
            db.save_tag(lex_item)
        except Exception as ex:
            logger.error(ex)
                         
    db.commit_change()


        