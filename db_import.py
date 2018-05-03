import json
import os
import gzip
import logging

logger = logging.getLogger("DeepLex.DbImport")
logger.setLevel("INFO")

def import_deep_lexicon(deeplex_path):
    if os.path.exists(deeplex_path):
        logger.warning("Cannot find deeplex file at %s", deeplex_path)
        return
    
    with gzip.open(deeplex_path, "rt", encoding="UTF-8") as fin:
        dlex_data = json.load(fin)
    
    print("Deeplex loaded: %d entries" % len(dlex_data))
    for lex_item in dlex_data:
        lu = lex_item.lu
        lex_data = lex_item.data
        