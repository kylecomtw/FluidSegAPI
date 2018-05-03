import logging
import sqlite3
import config
import os
import db_scheme
import pdb

logger = logging.getLogger("FluidSeg.Db")
logger.setLevel("WARNING")

class FluidDb:
    def __init__(self):
        os.remove(config.DB_PATH)
        self.conn = sqlite3.connect(config.DB_PATH)
        if not self.check_table_exists("tbl_sess"):
            self.create_datatables()
        
    def create_datatables(self):
        self.conn.execute(db_scheme.tbl_lus)
        self.conn.execute(db_scheme.tbl_field)        
        self.conn.execute(db_scheme.tbl_tag)
        self.conn.execute(db_scheme.tbl_seg)
        self.conn.execute(db_scheme.tbl_sess)        
        logger.info("Table created")
        self.conn.execute(db_scheme.idx_lus_lus)
        self.conn.execute(db_scheme.idx_field_field)
        self.conn.execute(db_scheme.idx_tag_sess)
        self.conn.execute(db_scheme.idx_tag_lu)
        self.conn.execute(db_scheme.idx_tag_tag)
        self.conn.execute(db_scheme.idx_seg_sess)
        self.conn.execute(db_scheme.idx_sess_docid)
        logger.info("Index created")
        self.conn.commit()

    def check_table_exists(self, tblname):
        cur = self.conn.cursor()
        cur.execute("SELECT 1 FROM sqlite_master WHERE name=?", (tblname,))
        ret = cur.fetchone()
        return ret != None
    
    def commit_change(self):
        self.conn.commit()
    
    def get_lu_info(self, lus):
        logger.warning("Not implemented")
    
    def get_session_info(self, sess_id):
        logger.warning("Not implemented")

    def get_segment_info(self, seg_id):
        logger.warning("Not implemented")

    def save_session(self, sess_item):
        logger.warning("Not implemented")

    def save_seg(self, seg_data):
        logger.warning("Not implemented")
        
    def save_tag(self, lex_item):
        # tag_data_list = {lu: "...", "data": [...]}
        cur = self.conn.cursor()
        if "lu" not in lex_item or "data" not in lex_item:
            logger.warning("invalid tag_data attempt to save")
        
        lus = (lex_item["lu"],)
        tags = lex_item["data"]
        fields = [(x,) for x in tags.keys()]
        
        cur.execute("INSERT OR IGNORE INTO tbl_lus (lus) VALUES (?)", lus)               
        cur.execute("SELECT lus_id FROM tbl_lus WHERE lus = ?", lus)
        lus_id = cur.fetchone()[0]

        logger.info("lu rowid: %d", lus_id)
        
        cur.executemany("INSERT OR IGNORE INTO tbl_field (field) VALUES (?)", fields)
        logger.info("tbl_field INSERT affected %d row(s)", cur.rowcount)
        
        fields_str = ",".join(["'%s'" % (x,) for x in tags.keys()])
        cmd = "SELECT * FROM tbl_field WHERE field IN (%s)" % fields_str
        cur.execute(cmd)
        field_map = {field: field_id for field_id, field in cur.fetchall()}
    
        ins_data_list = []
        for tag_field, tag_value in tags.items():
            ins_data_list.append((
                None, # tag_id
                None,   # sess_id
                lus_id, # lus_id
                field_map[tag_field], #field_id,                
                tag_value, # tagvalue
                None, # ranges
                ))
        
        # pdb.set_trace()                    
        cur.executemany("INSERT INTO tbl_tag VALUES (?,?,?,?,?,?)",
            ins_data_list)
        logger.info("tbl_tag INSERT affect %d rows", cur.rowcount)        

        

