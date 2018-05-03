import argparse
import db_import as dbImport 
import logging

logger = logging.getLogger("FluidSeg")
logger.setLevel("INFO")
ch = logging.StreamHandler()
formatter = logging.Formatter("%(name)s: [%(levelname)s] %(message)s")
ch.setFormatter(formatter)
logger.addHandler(ch)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--import-db", dest='deeplex_path', 
            action="store", nargs='?', help="import deeplex database")
    pargs = parser.parse_args()

    if pargs.deeplex_path:
        print("import deep lexicon database: " + pargs.deeplex_path)
        dbImport.import_deep_lexicon(pargs.deeplex_path)