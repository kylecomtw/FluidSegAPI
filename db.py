import sqlite3
import config
import os
import db_scheme
import pdb

class FluidDb:
    def __init__(self):
        self.conn = sqlite3.connect(config.DB_PATH)
        if not self.check_table_exists("tbl_sess"):
            self.create_datatables()
        
    def create_datatables(self):
        self.conn.execute(db_scheme.tbl_tag)
        self.conn.execute(db_scheme.tbl_seg)
        self.conn.execute(db_scheme.tbl_sess)
        self.conn.execute(db_scheme.idx_tag_sess)
        self.conn.execute(db_scheme.idx_tag_lu)
        self.conn.execute(db_scheme.idx_tag_tag)
        self.conn.execute(db_scheme.idx_seg_sess)
        self.conn.execute(db_scheme.idx_sess_docid)
        self.conn.commit()

    def check_table_exists(self, tblname):
        cur = self.conn.cursor()
        cur.execute("SELECT 1 FROM sqlite_master WHERE name=?", (tblname,))
        ret = cur.fetchone()
        return ret != None
        

